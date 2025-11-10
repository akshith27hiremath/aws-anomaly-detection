"""
Narrative Generator - Converts technical findings to natural language narratives.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class NarrativeGenerator:
    """
    Generates human-readable narratives from anomaly detections.
    """

    def __init__(self, detail_level: str = "medium"):
        """
        Initialize narrative generator.

        Args:
            detail_level: Level of detail (low, medium, high)
        """
        self.detail_level = detail_level

    def generate(
        self,
        primary_anomaly: Dict[str, Any],
        supporting_detections: List[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a narrative explanation for an anomaly.

        Args:
            primary_anomaly: Main anomaly data
            supporting_detections: Additional supporting detections

        Returns:
            Natural language narrative
        """
        narrative_parts = []

        # Opening statement
        narrative_parts.append(self._generate_opening(primary_anomaly))

        # Detection details
        if self.detail_level in ["medium", "high"]:
            narrative_parts.append(self._generate_detection_details(primary_anomaly))

        # Supporting evidence
        if supporting_detections and len(supporting_detections) > 1:
            narrative_parts.append(
                self._generate_consensus_statement(supporting_detections)
            )

        # Technical details (high detail only)
        if self.detail_level == "high":
            narrative_parts.append(self._generate_technical_details(primary_anomaly))

        # Impact and recommendations
        narrative_parts.append(self._generate_impact_statement(primary_anomaly))

        return " ".join(narrative_parts)

    def _generate_opening(self, anomaly: Dict[str, Any]) -> str:
        """Generate opening statement."""
        source = anomaly.get('source', 'unknown source')
        metric = anomaly.get('metric', 'unknown metric')
        timestamp = anomaly.get('timestamp', datetime.now())
        severity = anomaly.get('severity', 'medium')

        # Format timestamp
        time_str = timestamp.strftime("%B %d, %Y at %I:%M %p")

        # Severity adjective
        severity_adj = {
            'critical': 'critical',
            'high': 'significant',
            'medium': 'notable',
            'low': 'minor'
        }.get(severity, 'notable')

        return (
            f"A {severity_adj} anomaly was detected in the {metric} metric "
            f"from {source} on {time_str}."
        )

    def _generate_detection_details(self, anomaly: Dict[str, Any]) -> str:
        """Generate detection method details."""
        value = anomaly.get('value')
        expected = anomaly.get('expected_value')

        # Handle None values (e.g., from correlation anomalies)
        if value is None:
            return "This multi-source correlation anomaly was detected across multiple data sources."

        details = f"The observed value was {value:.2f}"

        if expected is not None:
            deviation = abs(value - expected)
            percent_dev = (deviation / expected * 100) if expected != 0 else 0

            details += (
                f", deviating {percent_dev:.1f}% from the expected value of {expected:.2f}"
            )

        details += "."

        return details

    def _generate_consensus_statement(
        self,
        detections: List[Dict[str, Any]]
    ) -> str:
        """Generate consensus statement from multiple detections."""
        agent_names = list(set(d.get('agent_name', 'Unknown') for d in detections))
        count = len(detections)

        return (
            f"This anomaly was independently detected by {count} different "
            f"analysis methods ({', '.join(agent_names)}), providing strong "
            f"confidence in the finding."
        )

    def _generate_technical_details(self, anomaly: Dict[str, Any]) -> str:
        """Generate technical details."""
        details = []

        # Z-score
        if 'z_score' in anomaly:
            details.append(f"Z-score: {anomaly['z_score']:.2f}")

        # Confidence
        if 'confidence' in anomaly:
            details.append(f"Detection confidence: {anomaly['confidence']:.2%}")

        # Methods
        if 'detection_methods' in anomaly:
            methods = anomaly['detection_methods']
            if isinstance(methods, list) and methods:
                details.append(f"Methods: {', '.join(methods)}")

        if details:
            return "Technical details: " + "; ".join(details) + "."

        return ""

    def _generate_impact_statement(self, anomaly: Dict[str, Any]) -> str:
        """Generate impact and recommendation statement."""
        severity = anomaly.get('severity', 'medium')

        impact_statements = {
            'critical': (
                "This is a critical anomaly that requires immediate attention and "
                "investigation to determine root cause and prevent potential system issues."
            ),
            'high': (
                "This significant anomaly warrants prompt investigation to understand "
                "the underlying cause and assess potential impacts."
            ),
            'medium': (
                "This anomaly should be reviewed to determine if any action is needed "
                "and to identify potential patterns."
            ),
            'low': (
                "This minor anomaly has been logged for awareness and trend analysis."
            )
        }

        return impact_statements.get(severity, impact_statements['medium'])

    def generate_summary(self, anomalies: List[Dict[str, Any]]) -> str:
        """
        Generate executive summary for multiple anomalies.

        Args:
            anomalies: List of anomalies

        Returns:
            Executive summary
        """
        if not anomalies:
            return "No anomalies detected in the analyzed period."

        total = len(anomalies)

        # Count by severity
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }

        sources = set()
        for anomaly in anomalies:
            sev = anomaly.get('severity', 'medium')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            sources.add(anomaly.get('source', 'unknown'))

        summary = f"Detected {total} anomalies across {len(sources)} data sources. "

        # Severity breakdown
        if severity_counts['critical'] > 0:
            summary += f"{severity_counts['critical']} critical, "

        if severity_counts['high'] > 0:
            summary += f"{severity_counts['high']} high severity, "

        if severity_counts['medium'] > 0:
            summary += f"{severity_counts['medium']} medium severity, "

        if severity_counts['low'] > 0:
            summary += f"{severity_counts['low']} low severity. "

        # Top source
        source_list = list(sources)
        if source_list:
            summary += f"Affected sources include: {', '.join(source_list)}."

        return summary

    def generate_timeline(self, anomalies: List[Dict[str, Any]]) -> str:
        """
        Generate timeline narrative.

        Args:
            anomalies: List of anomalies sorted by time

        Returns:
            Timeline narrative
        """
        if not anomalies:
            return "No timeline available."

        # Sort by timestamp
        sorted_anomalies = sorted(
            anomalies,
            key=lambda x: x.get('timestamp', datetime.now())
        )

        timeline = "Anomaly timeline: "

        for i, anomaly in enumerate(sorted_anomalies[:5], 1):  # Limit to 5
            ts = anomaly.get('timestamp', datetime.now())
            source = anomaly.get('source', 'unknown')
            metric = anomaly.get('metric', 'unknown')

            timeline += (
                f"{i}. {ts.strftime('%H:%M:%S')} - {source} {metric}; "
            )

        if len(sorted_anomalies) > 5:
            timeline += f"and {len(sorted_anomalies) - 5} more..."

        return timeline
