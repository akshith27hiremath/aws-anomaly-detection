"""
Temporal Agent - Analyzes time-series patterns and temporal anomalies.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.detection.temporal_detectors import (
    ChangePointDetector,
    ExponentialSmoothingDetector,
    MovingAverageCrossoverDetector,
    SeasonalAnomalyDetector,
    TrendAnomalyDetector,
)
from backend.utils.config import get_detection_config
from backend.utils.helpers import calculate_severity, calculate_trend, detect_seasonality

logger = logging.getLogger(__name__)


class TemporalAgent:
    """
    Agent specialized in temporal and time-series anomaly detection.
    """

    def __init__(self):
        """Initialize the temporal agent."""
        self.config = get_detection_config()
        agent_config = self.config.get_agent_config('temporal')

        self.weight = agent_config.get('weight', 0.25)
        self.min_confidence = agent_config.get('min_confidence', 0.5)

        # Initialize detectors
        self.detectors = [
            ChangePointDetector(),
            TrendAnomalyDetector(),
            SeasonalAnomalyDetector(),
            ExponentialSmoothingDetector(),
            MovingAverageCrossoverDetector()
        ]

        self.name = "TemporalAgent"

    async def analyze(
        self,
        data_points: List[Dict[str, Any]],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze temporal patterns and detect time-series anomalies.

        Args:
            data_points: Current data points
            historical_data: Historical data for context

        Returns:
            Analysis results
        """
        logger.info(f"{self.name}: Starting temporal analysis")

        # Combine current and historical data
        all_data = (historical_data or []) + data_points

        # Group by source and metric
        grouped_data = self._group_data(all_data)

        anomalies = []
        patterns = []

        for key, data in grouped_data.items():
            source, metric = key

            # Sort by timestamp
            data.sort(key=lambda x: x.get('timestamp', datetime.now()))

            values = [d['value'] for d in data]
            timestamps = [d['timestamp'] for d in data]

            # Analyze patterns
            pattern_info = self._analyze_patterns(values, timestamps)
            patterns.append({
                'source': source,
                'metric': metric,
                **pattern_info
            })

            # Run all detectors
            for detector in self.detectors:
                try:
                    detections = detector.detect(values, timestamps)

                    for detection in detections:
                        if detection.get('confidence', 0) >= self.min_confidence:
                            # Only keep recent anomalies (in current data_points window)
                            if self._is_recent(detection, data_points):
                                severity_label, severity_score = calculate_severity(
                                    confidence=detection['confidence'],
                                    deviation_magnitude=abs(detection.get('change_magnitude', 0)),
                                    impact_scope=1
                                )

                                anomaly = {
                                    'agent': self.name,
                                    'source': source,
                                    'metric': metric,
                                    'timestamp': detection.get('timestamp', datetime.now()),
                                    'value': detection['value'],
                                    'confidence': detection['confidence'],
                                    'severity': severity_label,
                                    'severity_score': severity_score,
                                    'detection_method': detection['method'],
                                    'anomaly_type': detection.get('type', 'temporal'),
                                    'pattern_context': pattern_info,
                                    'explanation': self._generate_explanation(detection, pattern_info)
                                }

                                anomalies.append(anomaly)

                except Exception as e:
                    logger.error(f"Error in {detector.__class__.__name__}: {e}")

        logger.info(f"{self.name}: Found {len(anomalies)} temporal anomalies")

        return {
            'agent': self.name,
            'weight': self.weight,
            'anomalies': anomalies,
            'metadata': {
                'patterns_analyzed': patterns,
                'total_anomalies': len(anomalies)
            }
        }

    def _group_data(
        self,
        data_points: List[Dict[str, Any]]
    ) -> Dict[tuple, List[Dict[str, Any]]]:
        """Group data points by source and metric."""
        grouped = {}

        for point in data_points:
            source = point.get('source', 'unknown')
            metric = point.get('metric', 'unknown')
            key = (source, metric)

            if key not in grouped:
                grouped[key] = []

            grouped[key].append(point)

        return grouped

    def _analyze_patterns(
        self,
        values: List[float],
        timestamps: List[datetime]
    ) -> Dict[str, Any]:
        """Analyze overall patterns in time series."""
        import numpy as np

        if len(values) < 10:
            return {'insufficient_data': True}

        arr = np.array(values)

        # Trend analysis
        trend_info = calculate_trend(arr)

        # Seasonality detection
        seasonality_info = detect_seasonality(arr)

        # Volatility
        volatility = float(np.std(arr) / np.mean(arr)) if np.mean(arr) != 0 else 0

        return {
            'trend': trend_info,
            'seasonality': seasonality_info,
            'volatility': volatility,
            'data_points': len(values),
            'time_span': (timestamps[-1] - timestamps[0]).total_seconds() / 3600  # hours
        }

    def _is_recent(
        self,
        detection: Dict[str, Any],
        current_data: List[Dict[str, Any]]
    ) -> bool:
        """Check if detection is in current data window."""
        if not current_data:
            return True

        detection_ts = detection.get('timestamp')
        if detection_ts is None:
            return True

        earliest = min(d.get('timestamp', datetime.now()) for d in current_data)
        return detection_ts >= earliest

    def _generate_explanation(
        self,
        detection: Dict[str, Any],
        pattern_context: Dict[str, Any]
    ) -> str:
        """Generate explanation for temporal anomaly."""
        method = detection.get('method', 'unknown')
        anomaly_type = detection.get('type', 'temporal')

        explanation = f"Temporal anomaly ({anomaly_type}) detected using {method}. "

        if method == 'changepoint':
            explanation += (
                f"Significant regime change detected. "
                f"Mean shifted from {detection.get('mean_before', 0):.2f} "
                f"to {detection.get('mean_after', 0):.2f}. "
            )

        elif method == 'trend_deviation':
            explanation += (
                f"Local trend diverged significantly from global trend. "
            )

        elif method == 'seasonal_decomposition':
            explanation += (
                f"Value deviates from expected seasonal pattern. "
            )

        elif method == 'ma_crossover':
            explanation += (
                f"Short and long-term moving averages diverged by "
                f"{detection.get('deviation', 0):.2%}. "
            )

        # Add context
        if pattern_context.get('trend', {}).get('direction') == 'increasing':
            explanation += "Overall trend is increasing. "
        elif pattern_context.get('trend', {}).get('direction') == 'decreasing':
            explanation += "Overall trend is decreasing. "

        if pattern_context.get('seasonality', {}).get('has_seasonality'):
            explanation += "Seasonal patterns detected in data. "

        return explanation.strip()
