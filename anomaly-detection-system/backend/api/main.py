"""
FastAPI main application with WebSocket support for real-time anomaly detection.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents import AgentOrchestrator
from backend.data_sources import CryptoClient, GitHubClient, OIDerivativesClient, WeatherClient
from backend.utils.config import get_settings
from backend.utils.helpers import setup_logging


# Custom JSON encoder for datetime serialization
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Initialize settings and logging
settings = get_settings()
logger = setup_logging(settings.log_level)

# Create FastAPI app
app = FastAPI(
    title="Anomaly Detection System",
    description="Multi-agent anomaly detection with explainable AI",
    version="1.0.0"
)

# CORS middleware
origins = settings.cors_origins.split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
orchestrator = AgentOrchestrator()
data_clients = {
    'crypto': CryptoClient(),
    'weather': WeatherClient(),
    'github': GitHubClient(),
    'oi_derivatives': OIDerivativesClient()
}

# Data storage
historical_data: List[Dict[str, Any]] = []
latest_analysis: Dict[str, Any] = {}

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                # Use custom encoder to handle datetime objects
                message_str = json.dumps(message, cls=DateTimeEncoder)
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")


manager = ConnectionManager()


# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


class AnalysisResponse(BaseModel):
    status: str
    timestamp: datetime
    anomaly_count: int
    high_severity_count: int
    reports: List[Dict[str, Any]]


# Background task for continuous data collection
async def collect_data_continuously():
    """Continuously collect data from all sources."""
    while True:
        try:
            # Fetch data from all sources
            tasks = [
                client.fetch_data()
                for client in data_clients.values()
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Combine all data points
            current_data = []
            for result in results:
                if isinstance(result, list):
                    current_data.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Data fetch error: {result}")

            if current_data:
                # Add to historical data
                historical_data.extend(current_data)

                # Keep only recent data (last 1000 points per source/metric)
                if len(historical_data) > 10000:
                    historical_data[:] = historical_data[-10000:]

                # Run analysis
                analysis = await orchestrator.analyze(current_data, historical_data[-500:])

                # Store latest analysis
                latest_analysis.clear()
                latest_analysis.update(analysis)

                # Broadcast to WebSocket clients
                await manager.broadcast({
                    'type': 'anomaly_update',
                    'timestamp': datetime.now().isoformat(),
                    'data': analysis
                })

                logger.info(f"Analyzed {len(current_data)} data points, found {analysis.get('total_anomalies', 0)} anomalies")

        except Exception as e:
            logger.error(f"Error in data collection: {e}", exc_info=True)

        # Wait before next collection
        await asyncio.sleep(settings.collection_interval_seconds)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup."""
    logger.info("Starting anomaly detection system...")

    # Start data collection in background
    asyncio.create_task(collect_data_continuously())

    logger.info("System started successfully")


# API endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@app.get("/analysis", response_model=AnalysisResponse)
async def get_latest_analysis():
    """Get latest anomaly analysis results."""
    if not latest_analysis:
        return AnalysisResponse(
            status="no_data",
            timestamp=datetime.now(),
            anomaly_count=0,
            high_severity_count=0,
            reports=[]
        )

    return AnalysisResponse(
        status="success",
        timestamp=datetime.now(),
        anomaly_count=latest_analysis.get('total_anomalies', 0),
        high_severity_count=latest_analysis.get('high_severity_count', 0),
        reports=latest_analysis.get('reports', [])
    )


@app.get("/knowledge-graph")
async def get_knowledge_graph():
    """Get knowledge graph data for visualization."""
    if 'knowledge_graph' in latest_analysis:
        return latest_analysis['knowledge_graph']

    return {
        'nodes': [],
        'edges': [],
        'stats': {}
    }


@app.get("/data-sources")
async def get_data_sources():
    """Get current data from all sources."""
    tasks = [client.fetch_data() for client in data_clients.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    data_by_source = {}
    for source_name, result in zip(data_clients.keys(), results):
        if isinstance(result, list):
            data_by_source[source_name] = result
        else:
            data_by_source[source_name] = {'error': str(result)}

    return data_by_source


@app.get("/statistics")
async def get_statistics():
    """Get system statistics."""
    return {
        'historical_data_points': len(historical_data),
        'latest_analysis_time': latest_analysis.get('timestamp'),
        'total_anomalies_detected': latest_analysis.get('total_anomalies', 0),
        'websocket_connections': len(manager.active_connections),
        'data_sources': list(data_clients.keys())
    }


@app.post("/analyze")
async def trigger_analysis():
    """Manually trigger an analysis."""
    try:
        # Fetch fresh data
        tasks = [client.fetch_data() for client in data_clients.values()]
        results = await asyncio.gather(*tasks)

        current_data = []
        for result in results:
            if isinstance(result, list):
                current_data.extend(result)

        # Run analysis
        analysis = await orchestrator.analyze(current_data, historical_data[-500:])

        # Update latest analysis
        latest_analysis.clear()
        latest_analysis.update(analysis)

        # Broadcast
        await manager.broadcast({
            'type': 'anomaly_update',
            'timestamp': datetime.now().isoformat(),
            'data': analysis
        })

        return {
            'status': 'success',
            'anomalies_found': analysis.get('total_anomalies', 0)
        }

    except Exception as e:
        logger.error(f"Error in manual analysis: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


# OI Derivatives specific endpoints
@app.get("/oi/current")
async def get_current_oi():
    """Get current OI derivatives data."""
    try:
        oi_client = data_clients.get('oi_derivatives')
        if not oi_client:
            return {'error': 'OI derivatives client not available'}

        data = await oi_client.fetch_data()

        # Group by symbol
        by_symbol = {}
        for point in data:
            symbol = point.get('symbol', 'unknown')
            if symbol not in by_symbol:
                by_symbol[symbol] = {}

            metric = point.get('metric')
            value = point.get('value')
            by_symbol[symbol][metric] = value

        return {
            'status': 'success',
            'timestamp': datetime.now(),
            'data': by_symbol
        }

    except Exception as e:
        logger.error(f"Error fetching current OI data: {e}")
        return {'status': 'error', 'error': str(e)}


@app.get("/oi/divergences")
async def get_oi_divergences():
    """Get detected OI divergences."""
    try:
        # Filter anomalies for OI divergences
        oi_anomalies = []

        if latest_analysis and 'reports' in latest_analysis:
            for report in latest_analysis['reports']:
                if report.get('source') == 'oi_derivatives':
                    # Check if it's a divergence detection
                    metadata = report.get('metadata', {})
                    if 'divergence_type' in metadata or 'detection_type' in metadata:
                        oi_anomalies.append(report)

        return {
            'status': 'success',
            'timestamp': datetime.now(),
            'divergence_count': len(oi_anomalies),
            'divergences': oi_anomalies
        }

    except Exception as e:
        logger.error(f"Error fetching OI divergences: {e}")
        return {'status': 'error', 'error': str(e)}


@app.get("/oi/funding-rates")
async def get_funding_rates():
    """Get current funding rates for all tracked symbols."""
    try:
        oi_client = data_clients.get('oi_derivatives')
        if not oi_client:
            return {'error': 'OI derivatives client not available'}

        data = await oi_client.fetch_data()

        # Extract funding rates
        funding_rates = {}
        for point in data:
            if point.get('metric') == 'funding_rate':
                symbol = point.get('symbol', 'unknown')
                funding_rates[symbol] = {
                    'rate': point.get('value'),
                    'timestamp': point.get('timestamp'),
                    'signal': 'extreme' if abs(point.get('value', 0)) > 0.1 else 'normal'
                }

        return {
            'status': 'success',
            'timestamp': datetime.now(),
            'funding_rates': funding_rates
        }

    except Exception as e:
        logger.error(f"Error fetching funding rates: {e}")
        return {'status': 'error', 'error': str(e)}


@app.get("/oi/long-short-ratios")
async def get_long_short_ratios():
    """Get long/short ratios for all tracked symbols."""
    try:
        oi_client = data_clients.get('oi_derivatives')
        if not oi_client:
            return {'error': 'OI derivatives client not available'}

        data = await oi_client.fetch_data()

        # Extract ratios
        ratios = {}
        for point in data:
            symbol = point.get('symbol', 'unknown')

            if symbol not in ratios:
                ratios[symbol] = {}

            metric = point.get('metric')
            if metric == 'long_short_ratio':
                ratios[symbol]['global'] = {
                    'ratio': point.get('value'),
                    'timestamp': point.get('timestamp')
                }
            elif metric == 'top_trader_long_short_ratio':
                ratios[symbol]['top_traders'] = {
                    'ratio': point.get('value'),
                    'timestamp': point.get('timestamp')
                }

        return {
            'status': 'success',
            'timestamp': datetime.now(),
            'ratios': ratios
        }

    except Exception as e:
        logger.error(f"Error fetching long/short ratios: {e}")
        return {'status': 'error', 'error': str(e)}


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)

    try:
        # Send latest analysis on connect
        if latest_analysis:
            message = json.dumps({
                'type': 'initial_data',
                'data': latest_analysis
            }, cls=DateTimeEncoder)
            await websocket.send_text(message)

        # Keep connection alive
        while True:
            # Wait for messages from client (ping/pong)
            data = await websocket.receive_text()

            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
