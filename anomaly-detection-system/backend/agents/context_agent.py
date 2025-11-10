"""
Context Agent - Fetches external context to explain anomalies.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.utils.config import get_detection_config

logger = logging.getLogger(__name__)


class ContextAgent:
    """
    Agent that fetches external context (news, events) to explain anomalies.
    In a production system, this would integrate with news APIs, event databases, etc.
    """

    def __init__(self):
        """Initialize the context agent."""
        self.config = get_detection_config()
        agent_config = self.config.get_agent_config('context')

        self.weight = agent_config.get('weight', 0.15)
        self.min_confidence = agent_config.get('min_confidence', 0.4)

        self.name = "ContextAgent"

        # In production, initialize news API clients
        # For demo, we'll use pattern matching

    async def analyze(
        self,
        data_points: List[Dict[str, Any]],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze data points and fetch relevant context.

        Args:
            data_points: Current data points
            historical_data: Historical data

        Returns:
            Analysis with contextual information
        """
        logger.info(f"{self.name}: Starting context analysis")

        anomalies = []
        context_findings = []

        # Group by source
        grouped = self._group_by_source(data_points)

        for source, points in grouped.items():
            # Fetch context for this source
            context = await self._fetch_context(source, points)

            if context and context.get('relevance', 0) >= self.min_confidence:
                context_findings.append(context)

                # Create ONE contextual anomaly summary per source (not per point)
                # Use the most recent/extreme point as representative
                if self._is_context_relevant_for_source(points, context):
                    representative_point = max(points, key=lambda p: abs(p.get('value', 0)))

                    anomaly = {
                        'agent': self.name,
                        'source': source,
                        'metric': representative_point.get('metric', 'unknown'),
                        'timestamp': representative_point.get('timestamp', datetime.now()),
                        'value': representative_point.get('value'),
                        'confidence': context.get('relevance', 0.5),
                        'severity': 'medium',
                        'severity_score': 0.5,
                        'context': context,
                        'explanation': self._generate_explanation(representative_point, context),
                        'context_data': {
                            'affected_points': len(points),
                            'source_metrics': list(set(p.get('metric', 'unknown') for p in points))
                        }
                    }

                    anomalies.append(anomaly)

        logger.info(f"{self.name}: Found {len(context_findings)} contextual insights")

        return {
            'agent': self.name,
            'weight': self.weight,
            'anomalies': anomalies,
            'metadata': {
                'context_findings': context_findings,
                'sources_analyzed': len(grouped)
            }
        }

    def _group_by_source(
        self,
        data_points: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group data points by source."""
        grouped = {}

        for point in data_points:
            source = point.get('source', 'unknown')

            if source not in grouped:
                grouped[source] = []

            grouped[source].append(point)

        return grouped

    async def _fetch_context(
        self,
        source: str,
        data_points: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch external context for a data source.
        In production, this would query news APIs, event databases, etc.

        For demo purposes, we'll simulate context based on patterns and data characteristics.
        """
        if not data_points:
            return None

        # Analyze data characteristics to determine appropriate context
        values = [p.get('value', 0) for p in data_points if p.get('value') is not None]

        # Calculate volatility/extremeness
        if values:
            avg_value = sum(values) / len(values) if values else 1
            max_value = max(values) if values else 1
            deviation = (max_value - avg_value) / (avg_value if avg_value != 0 else 1)
        else:
            deviation = 0

        # Simulate context fetching with metric-specific responses
        context = {
            'source': source,
            'timestamp': datetime.now(),
            'events': [],
            'relevance': 0.0
        }

        # Pattern-based context (for demo) with variation based on data
        if source == 'cryptocurrency':
            if deviation > 2:  # High volatility
                context['events'] = [
                    {'type': 'market_event', 'description': 'Extreme price volatility detected'},
                    {'type': 'news', 'description': 'Market manipulation alert'}
                ]
                context['relevance'] = 0.75
            else:
                context['events'] = [
                    {'type': 'market_event', 'description': 'Normal trading activity'},
                    {'type': 'news', 'description': 'Standard market conditions'}
                ]
                context['relevance'] = 0.4

        elif source == 'weather':
            # Check for extreme weather patterns
            temps = [p.get('value', 0) for p in data_points if p.get('metric') == 'temperature']
            if temps and (max(temps) > 30 or min(temps) < 0):
                context['events'] = [
                    {'type': 'meteorological', 'description': 'Extreme temperature alert'},
                    {'type': 'event', 'description': 'Weather advisory issued'}
                ]
                context['relevance'] = 0.7
            else:
                context['events'] = [
                    {'type': 'meteorological', 'description': 'Seasonal weather pattern'},
                    {'type': 'event', 'description': 'Normal conditions'}
                ]
                context['relevance'] = 0.3

        elif source == 'github':
            context['events'] = [
                {'type': 'platform', 'description': 'API activity change'},
                {'type': 'event', 'description': 'Repository activity spike'}
            ]
            context['relevance'] = 0.5

        return context if context['events'] else None

    def _is_context_relevant(
        self,
        data_point: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Determine if context is relevant to a data point."""
        # Check relevance score
        if context.get('relevance', 0) < self.min_confidence:
            return False

        # In production, would do semantic matching
        return len(context.get('events', [])) > 0

    def _is_context_relevant_for_source(
        self,
        data_points: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> bool:
        """Determine if context is relevant to a source's data."""
        # Check relevance score
        if context.get('relevance', 0) < self.min_confidence:
            return False

        # Check if we have data points
        return len(data_points) > 0 and len(context.get('events', [])) > 0

    def _generate_explanation(
        self,
        data_point: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate contextual explanation."""
        source = data_point.get('source', 'unknown')
        metric = data_point.get('metric', 'unknown')

        events = context.get('events', [])
        event_descriptions = [e['description'] for e in events]

        explanation = (
            f"Anomaly in {source} {metric} may be related to external events: "
            f"{', '.join(event_descriptions)}. "
            f"Contextual relevance: {context.get('relevance', 0):.2f}."
        )

        return explanation
