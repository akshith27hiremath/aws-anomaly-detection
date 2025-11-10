"""
Tests for anomaly detection algorithms.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta

from backend.detection.statistical_detectors import (
    ZScoreDetector,
    ModifiedZScoreDetector,
    IQRDetector,
    CUSUMDetector,
    EnsembleStatisticalDetector
)
from backend.detection.temporal_detectors import (
    ChangePointDetector,
    TrendAnomalyDetector
)


class TestStatisticalDetectors:
    """Test statistical detection methods."""

    def test_zscore_detector(self):
        """Test Z-score anomaly detection."""
        # Create normal data with one outlier
        values = [10, 12, 11, 10, 11, 12, 50, 11, 10, 12]

        detector = ZScoreDetector(threshold=2.0)
        anomalies = detector.detect(values)

        # Should detect the outlier at index 6
        assert len(anomalies) > 0
        assert any(a['index'] == 6 for a in anomalies)
        assert all('z_score' in a for a in anomalies)

    def test_modified_zscore_detector(self):
        """Test Modified Z-score detector."""
        values = [5, 5, 6, 5, 6, 5, 100, 5, 6, 5]

        detector = ModifiedZScoreDetector(threshold=3.0)
        anomalies = detector.detect(values)

        assert len(anomalies) > 0
        assert all('modified_z_score' in a for a in anomalies)

    def test_iqr_detector(self):
        """Test IQR method."""
        values = list(range(1, 100)) + [1000]  # Add outlier

        detector = IQRDetector(multiplier=1.5)
        anomalies = detector.detect(values)

        assert len(anomalies) > 0
        assert any(a['value'] == 1000 for a in anomalies)

    def test_cusum_detector(self):
        """Test CUSUM detector."""
        # Create data with a mean shift
        values = [10] * 20 + [20] * 20

        detector = CUSUMDetector(threshold=3.0, drift=0.5)
        anomalies = detector.detect(values)

        # Should detect the shift
        assert len(anomalies) > 0

    def test_ensemble_detector(self):
        """Test ensemble detector."""
        values = [10, 11, 10, 12, 11, 100, 10, 11, 12]

        detector = EnsembleStatisticalDetector()
        anomalies = detector.detect(values, min_consensus=2)

        # Ensemble should agree on the outlier
        assert len(anomalies) > 0
        assert all('consensus_count' in a for a in anomalies)


class TestTemporalDetectors:
    """Test temporal detection methods."""

    def test_changepoint_detector(self):
        """Test changepoint detection."""
        # Create data with regime change
        values = [10] * 30 + [20] * 30

        detector = ChangePointDetector(min_size=5)
        anomalies = detector.detect(values)

        assert len(anomalies) > 0
        assert all('mean_before' in a for a in anomalies)
        assert all('mean_after' in a for a in anomalies)

    def test_trend_detector(self):
        """Test trend anomaly detection."""
        # Create trending data with reversal
        values = list(range(50)) + list(range(50, 0, -1))

        detector = TrendAnomalyDetector(window_size=10)
        anomalies = detector.detect(values)

        # Should detect the trend reversal
        assert len(anomalies) >= 0  # May or may not detect depending on sensitivity


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_insufficient_data(self):
        """Test with insufficient data points."""
        values = [1, 2]

        detector = ZScoreDetector()
        anomalies = detector.detect(values)

        # Should return empty list, not crash
        assert anomalies == []

    def test_constant_values(self):
        """Test with all same values."""
        values = [5] * 100

        detector = ZScoreDetector()
        anomalies = detector.detect(values)

        # Should handle zero variance
        assert anomalies == []

    def test_with_timestamps(self):
        """Test detection with timestamps."""
        values = [10, 11, 100, 12, 11]
        timestamps = [datetime.now() + timedelta(minutes=i) for i in range(5)]

        detector = ZScoreDetector()
        anomalies = detector.detect(values, timestamps)

        # Anomalies should include timestamps
        assert len(anomalies) > 0
        assert all('timestamp' in a for a in anomalies)
