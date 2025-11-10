"""
Statistical Agent - Performs statistical anomaly detection.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.detection.statistical_detectors import EnsembleStatisticalDetector
from backend.utils.config import get_detection_config
from backend.utils.helpers import calculate_severity

logger = logging.getLogger(__name__)


class StatisticalAgent:
    """
    Agent specialized in statistical anomaly detection.
    Uses multiple statistical methods to identify outliers.
    """

    def __init__(self):
        """Initialize the statistical agent."""
        self.config = get_detection_config()
        agent_config = self.config.get_agent_config('statistical')

        self.weight = agent_config.get('weight', 0.25)
        self.min_confidence = agent_config.get('min_confidence', 0.5)

        self.detector = EnsembleStatisticalDetector()
        self.name = "StatisticalAgent"

    async def analyze(
        self,
        data_points: List[Dict[str, Any]],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze data for statistical anomalies.

        Args:
            data_points: Current data points to analyze
            historical_data: Historical data for context

        Returns:
            Analysis results with detected anomalies
        """
        logger.info(f"{self.name}: Starting statistical analysis on {len(data_points)} data points")

        # Group data by source and metric
        grouped_data = self._group_data(data_points)

        anomalies = []
        analysis_metadata = []

        for key, data in grouped_data.items():
            source, metric = key

            # Extract values and timestamps
            values = [d['value'] for d in data]
            timestamps = [d['timestamp'] for d in data]

            # Perform detection
            detections = self.detector.detect(values, timestamps, min_consensus=2)

            # Process detections
            for detection in detections:
                if detection['confidence'] >= self.min_confidence:
                    # Calculate severity
                    severity_label, severity_score = calculate_severity(
                        confidence=detection['confidence'],
                        deviation_magnitude=detection.get('deviation', 0),
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
                        'detection_methods': detection['methods'],
                        'consensus_count': detection['consensus_count'],
                        'individual_detections': detection.get('individual_detections', []),
                        'explanation': self._generate_explanation(detection, source, metric)
                    }

                    anomalies.append(anomaly)

            analysis_metadata.append({
                'source': source,
                'metric': metric,
                'data_points': len(data),
                'anomalies_found': len(detections)
            })

        logger.info(f"{self.name}: Found {len(anomalies)} statistical anomalies")

        return {
            'agent': self.name,
            'weight': self.weight,
            'anomalies': anomalies,
            'metadata': {
                'groups_analyzed': len(grouped_data),
                'total_anomalies': len(anomalies),
                'analysis_details': analysis_metadata
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

    def _generate_explanation(
        self,
        detection: Dict[str, Any],
        source: str,
        metric: str
    ) -> str:
        """Generate human-readable explanation for detection."""
        methods = detection.get('methods', [])
        consensus = detection.get('consensus_count', 0)
        confidence = detection.get('confidence', 0.0)

        explanation = (
            f"Statistical anomaly detected in {source} {metric}. "
            f"{consensus} detection methods agreed (confidence: {confidence:.2f}). "
        )

        if 'zscore' in methods:
            explanation += "Value is significantly outside normal distribution. "

        if 'iqr' in methods:
            explanation += "Value is beyond interquartile range bounds. "

        if 'cusum' in methods:
            explanation += "Cumulative sum indicates a sustained shift in mean. "

        return explanation.strip()
