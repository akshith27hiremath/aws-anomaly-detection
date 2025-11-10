"""
Correlation Agent - Detects cross-source anomalies and correlations.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import pearsonr, spearmanr
from backend.utils.config import get_detection_config
from backend.utils.helpers import calculate_severity

logger = logging.getLogger(__name__)


class CorrelationAgent:
    """
    Agent specialized in detecting correlations and cross-source anomalies.
    """

    def __init__(self):
        """Initialize the correlation agent."""
        self.config = get_detection_config()
        agent_config = self.config.get_agent_config('correlation')

        self.weight = agent_config.get('weight', 0.20)
        self.min_confidence = agent_config.get('min_confidence', 0.6)

        corr_config = self.config.get_detection_params('correlation')
        self.pearson_threshold = corr_config.get('pearson_threshold', 0.7)
        self.spearman_threshold = corr_config.get('spearman_threshold', 0.7)
        self.window_size = corr_config.get('window_size', 30)
        self.break_threshold = corr_config.get('break_threshold', 0.3)

        self.name = "CorrelationAgent"

    async def analyze(
        self,
        data_points: List[Dict[str, Any]],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze correlations and detect correlation breaks.

        Args:
            data_points: Current data points
            historical_data: Historical data

        Returns:
            Analysis results
        """
        logger.info(f"{self.name}: Starting correlation analysis")

        # Combine data
        all_data = (historical_data or []) + data_points

        # Group by source and metric
        grouped_data = self._group_data(all_data)

        anomalies = []
        correlation_matrix = []

        # Analyze all pairs
        keys = list(grouped_data.keys())
        for i, key1 in enumerate(keys):
            for key2 in keys[i+1:]:
                source1, metric1 = key1
                source2, metric2 = key2

                # Align time series
                aligned = self._align_series(grouped_data[key1], grouped_data[key2])

                if len(aligned) >= self.window_size:
                    # Calculate correlation
                    corr_result = self._calculate_correlation(aligned)

                    if corr_result:
                        correlation_matrix.append({
                            'source1': source1,
                            'metric1': metric1,
                            'source2': source2,
                            'metric2': metric2,
                            **corr_result
                        })

                        # Detect correlation breaks
                        break_anomalies = self._detect_correlation_breaks(
                            aligned, key1, key2, corr_result
                        )

                        # Filter to recent anomalies
                        for anomaly in break_anomalies:
                            if self._is_recent(anomaly, data_points):
                                anomalies.append(anomaly)

        # Detect simultaneous anomalies across sources
        simultaneous = self._detect_simultaneous_anomalies(data_points)
        anomalies.extend(simultaneous)

        logger.info(f"{self.name}: Found {len(anomalies)} correlation anomalies")

        return {
            'agent': self.name,
            'weight': self.weight,
            'anomalies': anomalies,
            'metadata': {
                'correlation_matrix': correlation_matrix,
                'pairs_analyzed': len(correlation_matrix),
                'total_anomalies': len(anomalies)
            }
        }

    def _group_data(
        self,
        data_points: List[Dict[str, Any]]
    ) -> Dict[Tuple[str, str], List[Dict[str, Any]]]:
        """Group data by source and metric."""
        grouped = {}

        for point in data_points:
            source = point.get('source', 'unknown')
            metric = point.get('metric', 'unknown')
            key = (source, metric)

            if key not in grouped:
                grouped[key] = []

            grouped[key].append(point)

        # Sort each group by timestamp
        for key in grouped:
            grouped[key].sort(key=lambda x: x.get('timestamp', datetime.now()))

        return grouped

    def _align_series(
        self,
        series1: List[Dict[str, Any]],
        series2: List[Dict[str, Any]]
    ) -> List[Tuple[float, float, datetime]]:
        """Align two time series by timestamp."""
        # Create timestamp to value mappings
        map1 = {d['timestamp']: d['value'] for d in series1}
        map2 = {d['timestamp']: d['value'] for d in series2}

        # Find common timestamps
        common_timestamps = set(map1.keys()) & set(map2.keys())

        aligned = [
            (map1[ts], map2[ts], ts)
            for ts in sorted(common_timestamps)
        ]

        return aligned

    def _calculate_correlation(
        self,
        aligned_data: List[Tuple[float, float, datetime]]
    ) -> Optional[Dict[str, Any]]:
        """Calculate correlation metrics between two series."""
        if len(aligned_data) < 3:
            return None

        values1 = [d[0] for d in aligned_data]
        values2 = [d[1] for d in aligned_data]

        try:
            # Pearson correlation
            pearson_corr, pearson_p = pearsonr(values1, values2)

            # Spearman correlation (rank-based, more robust)
            spearman_corr, spearman_p = spearmanr(values1, values2)

            return {
                'pearson': float(pearson_corr),
                'pearson_pvalue': float(pearson_p),
                'spearman': float(spearman_corr),
                'spearman_pvalue': float(spearman_p),
                'data_points': len(aligned_data),
                'significant': abs(pearson_corr) >= self.pearson_threshold
            }

        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return None

    def _detect_correlation_breaks(
        self,
        aligned_data: List[Tuple[float, float, datetime]],
        key1: Tuple[str, str],
        key2: Tuple[str, str],
        historical_corr: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect points where historical correlation breaks down."""
        anomalies = []

        if len(aligned_data) < self.window_size * 2:
            return anomalies

        historical_pearson = historical_corr.get('pearson', 0)

        # Check if there was a significant correlation
        if abs(historical_pearson) < self.pearson_threshold:
            return anomalies

        # Sliding window to detect correlation breaks
        for i in range(self.window_size, len(aligned_data)):
            window = aligned_data[i - self.window_size:i]
            values1 = [d[0] for d in window]
            values2 = [d[1] for d in window]

            try:
                current_corr, _ = pearsonr(values1, values2)

                # Detect significant correlation break
                corr_change = abs(current_corr - historical_pearson)

                if corr_change >= self.break_threshold:
                    confidence = min(corr_change / self.break_threshold, 1.0)

                    if confidence >= self.min_confidence:
                        severity_label, severity_score = calculate_severity(
                            confidence=confidence,
                            deviation_magnitude=corr_change * 10,
                            impact_scope=2  # Affects two sources
                        )

                        anomaly = {
                            'agent': self.name,
                            'type': 'correlation_break',
                            'source1': key1[0],
                            'metric1': key1[1],
                            'source2': key2[0],
                            'metric2': key2[1],
                            'timestamp': aligned_data[i][2],
                            'value': f"{key1[0]}/{key1[1]}: {aligned_data[i][0]:.2f}, {key2[0]}/{key2[1]}: {aligned_data[i][1]:.2f}",
                            'historical_correlation': historical_pearson,
                            'current_correlation': float(current_corr),
                            'correlation_change': float(corr_change),
                            'confidence': confidence,
                            'severity': severity_label,
                            'severity_score': severity_score,
                            'explanation': (
                                f"Correlation between {key1[0]} {key1[1]} and {key2[0]} {key2[1]} "
                                f"broke down. Historical correlation: {historical_pearson:.2f}, "
                                f"current: {current_corr:.2f}."
                            )
                        }

                        anomalies.append(anomaly)

            except Exception:
                continue

        return anomalies

    def _detect_simultaneous_anomalies(
        self,
        data_points: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect anomalies occurring simultaneously across sources."""
        anomalies = []

        # Group by timestamp
        time_groups = {}
        for point in data_points:
            ts = point.get('timestamp', datetime.now())
            # Round to minute for grouping
            ts_key = ts.replace(second=0, microsecond=0)

            if ts_key not in time_groups:
                time_groups[ts_key] = []

            time_groups[ts_key].append(point)

        # Find timestamps with multiple sources
        for ts, points in time_groups.items():
            if len(points) >= 2:
                sources = set(p.get('source') for p in points)

                if len(sources) >= 2:
                    # Simultaneous anomaly across sources
                    confidence = min(len(sources) / 3.0, 1.0)

                    if confidence >= self.min_confidence:
                        severity_label, severity_score = calculate_severity(
                            confidence=confidence,
                            deviation_magnitude=5,
                            impact_scope=len(sources)
                        )

                        anomaly = {
                            'agent': self.name,
                            'type': 'simultaneous_anomaly',
                            'source': 'multi-source',
                            'metric': 'correlation',
                            'timestamp': ts,
                            'value': None,
                            'affected_sources': list(sources),
                            'data_points': points,
                            'confidence': confidence,
                            'severity': severity_label,
                            'severity_score': severity_score,
                            'explanation': (
                                f"Simultaneous anomaly detected across {len(sources)} sources: "
                                f"{', '.join(sources)} at {ts.strftime('%Y-%m-%d %H:%M')}."
                            )
                        }

                        anomalies.append(anomaly)

        return anomalies

    def _is_recent(
        self,
        anomaly: Dict[str, Any],
        current_data: List[Dict[str, Any]]
    ) -> bool:
        """Check if anomaly is in current window."""
        if not current_data:
            return True

        anomaly_ts = anomaly.get('timestamp')
        if anomaly_ts is None:
            return True

        earliest = min(d.get('timestamp', datetime.now()) for d in current_data)
        return anomaly_ts >= earliest
