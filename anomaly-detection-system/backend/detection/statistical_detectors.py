"""
Statistical anomaly detection algorithms.
Implements Z-score, Modified Z-score, IQR, and CUSUM methods.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from backend.utils.config import get_detection_config
from backend.utils.helpers import calculate_confidence

logger = logging.getLogger(__name__)


class StatisticalDetector:
    """
    Base class for statistical anomaly detection.
    """

    def __init__(self):
        """Initialize the statistical detector."""
        self.config = get_detection_config()

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in a list of values.

        Args:
            values: List of numerical values
            timestamps: Optional list of corresponding timestamps

        Returns:
            List of detected anomalies with metadata
        """
        raise NotImplementedError("Subclasses must implement detect method")


class ZScoreDetector(StatisticalDetector):
    """
    Detects anomalies using standard Z-score method.
    Points beyond ±threshold standard deviations are anomalies.
    """

    def __init__(self, threshold: float = 3.0):
        """
        Initialize Z-score detector.

        Args:
            threshold: Number of standard deviations for anomaly threshold
        """
        super().__init__()
        self.threshold = threshold

        # Load from config if available
        params = self.config.get_detection_params('zscore')
        if params:
            self.threshold = params.get('threshold', self.threshold)

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using Z-score method."""
        if len(values) < 3:
            return []

        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            return []

        # Calculate Z-scores
        z_scores = np.abs((arr - mean) / std)

        # Find anomalies
        anomalies = []
        for i, (z_score, value) in enumerate(zip(z_scores, values)):
            if z_score > self.threshold:
                confidence = calculate_confidence(z_score, self.threshold, scale=0.5)

                anomaly = {
                    'index': i,
                    'value': float(value),
                    'expected_value': float(mean),
                    'z_score': float(z_score),
                    'confidence': confidence,
                    'deviation': float(abs(value - mean)),
                    'method': 'zscore',
                    'threshold': self.threshold
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                anomalies.append(anomaly)

        return anomalies


class ModifiedZScoreDetector(StatisticalDetector):
    """
    Detects anomalies using Modified Z-score (based on median absolute deviation).
    More robust to outliers than standard Z-score.
    """

    def __init__(self, threshold: float = 3.5):
        """
        Initialize Modified Z-score detector.

        Args:
            threshold: Modified Z-score threshold
        """
        super().__init__()
        self.threshold = threshold

        params = self.config.get_detection_params('modified_zscore')
        if params:
            self.threshold = params.get('threshold', self.threshold)

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using Modified Z-score method."""
        if len(values) < 3:
            return []

        arr = np.array(values)
        median = np.median(arr)

        # Calculate Median Absolute Deviation (MAD)
        mad = np.median(np.abs(arr - median))

        if mad == 0:
            # Use mean absolute deviation if MAD is zero
            mad = np.mean(np.abs(arr - median))
            if mad == 0:
                return []

        # Calculate Modified Z-scores
        modified_z_scores = 0.6745 * (arr - median) / mad

        # Find anomalies
        anomalies = []
        for i, (mod_z, value) in enumerate(zip(modified_z_scores, values)):
            if abs(mod_z) > self.threshold:
                confidence = calculate_confidence(abs(mod_z), self.threshold, scale=0.5)

                anomaly = {
                    'index': i,
                    'value': float(value),
                    'expected_value': float(median),
                    'modified_z_score': float(mod_z),
                    'confidence': confidence,
                    'deviation': float(abs(value - median)),
                    'method': 'modified_zscore',
                    'threshold': self.threshold
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                anomalies.append(anomaly)

        return anomalies


class IQRDetector(StatisticalDetector):
    """
    Detects anomalies using Interquartile Range (IQR) method.
    Points beyond Q1 - k*IQR or Q3 + k*IQR are anomalies.
    """

    def __init__(self, multiplier: float = 1.5):
        """
        Initialize IQR detector.

        Args:
            multiplier: IQR multiplier for outlier bounds
        """
        super().__init__()
        self.multiplier = multiplier

        params = self.config.get_detection_params('iqr')
        if params:
            self.multiplier = params.get('multiplier', self.multiplier)

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using IQR method."""
        if len(values) < 4:
            return []

        arr = np.array(values)
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1

        if iqr == 0:
            return []

        # Calculate bounds
        lower_bound = q1 - self.multiplier * iqr
        upper_bound = q3 + self.multiplier * iqr

        # Find anomalies
        anomalies = []
        for i, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                # Calculate how far beyond bounds
                if value < lower_bound:
                    deviation = lower_bound - value
                    expected = lower_bound
                else:
                    deviation = value - upper_bound
                    expected = upper_bound

                # Confidence based on deviation
                confidence = calculate_confidence(deviation, iqr, scale=1.0)

                anomaly = {
                    'index': i,
                    'value': float(value),
                    'expected_range': [float(lower_bound), float(upper_bound)],
                    'q1': float(q1),
                    'q3': float(q3),
                    'iqr': float(iqr),
                    'confidence': confidence,
                    'deviation': float(deviation),
                    'method': 'iqr',
                    'multiplier': self.multiplier
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                anomalies.append(anomaly)

        return anomalies


class CUSUMDetector(StatisticalDetector):
    """
    Cumulative Sum (CUSUM) detector for detecting changes in mean.
    Good for detecting sustained shifts in data distribution.
    """

    def __init__(self, threshold: float = 5.0, drift: float = 0.5):
        """
        Initialize CUSUM detector.

        Args:
            threshold: CUSUM threshold for detection
            drift: Drift parameter (allowance for small variations)
        """
        super().__init__()
        self.threshold = threshold
        self.drift = drift

        params = self.config.get_detection_params('cusum')
        if params:
            self.threshold = params.get('threshold', self.threshold)
            self.drift = params.get('drift', self.drift)

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using CUSUM method."""
        if len(values) < 5:
            return []

        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            return []

        # Initialize CUSUM variables
        cusum_pos = 0
        cusum_neg = 0
        anomalies = []

        for i, value in enumerate(values):
            # Standardize value
            standardized = (value - mean) / std

            # Update CUSUM
            cusum_pos = max(0, cusum_pos + standardized - self.drift)
            cusum_neg = max(0, cusum_neg - standardized - self.drift)

            # Check thresholds
            if cusum_pos > self.threshold or cusum_neg > self.threshold:
                cusum_value = max(cusum_pos, cusum_neg)
                confidence = calculate_confidence(cusum_value, self.threshold, scale=0.3)

                anomaly = {
                    'index': i,
                    'value': float(value),
                    'expected_value': float(mean),
                    'cusum_positive': float(cusum_pos),
                    'cusum_negative': float(cusum_neg),
                    'confidence': confidence,
                    'deviation': float(abs(value - mean)),
                    'method': 'cusum',
                    'threshold': self.threshold
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                anomalies.append(anomaly)

                # Reset CUSUM after detection
                cusum_pos = 0
                cusum_neg = 0

        return anomalies


class MovingAverageDetector(StatisticalDetector):
    """
    Detects anomalies by comparing values to moving average.
    """

    def __init__(self, window_size: int = 10, threshold_std: float = 2.0):
        """
        Initialize moving average detector.

        Args:
            window_size: Size of moving window
            threshold_std: Number of standard deviations for threshold
        """
        super().__init__()
        self.window_size = window_size
        self.threshold_std = threshold_std

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using moving average."""
        if len(values) < self.window_size + 1:
            return []

        arr = np.array(values)
        anomalies = []

        for i in range(self.window_size, len(values)):
            # Calculate moving average and std
            window = arr[i - self.window_size:i]
            ma = np.mean(window)
            ma_std = np.std(window)

            if ma_std == 0:
                continue

            # Check if current value is anomalous
            deviation = abs(values[i] - ma)
            z_score = deviation / ma_std

            if z_score > self.threshold_std:
                confidence = calculate_confidence(z_score, self.threshold_std, scale=0.5)

                anomaly = {
                    'index': i,
                    'value': float(values[i]),
                    'expected_value': float(ma),
                    'moving_average': float(ma),
                    'moving_std': float(ma_std),
                    'z_score': float(z_score),
                    'confidence': confidence,
                    'deviation': float(deviation),
                    'method': 'moving_average',
                    'window_size': self.window_size
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                anomalies.append(anomaly)

        return anomalies


class EnsembleStatisticalDetector:
    """
    Combines multiple statistical detectors for robust detection.
    """

    def __init__(self):
        """Initialize ensemble detector."""
        self.detectors = [
            ZScoreDetector(),
            ModifiedZScoreDetector(),
            IQRDetector(),
            CUSUMDetector()
        ]

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None,
        min_consensus: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using ensemble of methods.

        Args:
            values: List of values
            timestamps: Optional timestamps
            min_consensus: Minimum number of methods that must agree

        Returns:
            List of anomalies with consensus information
        """
        # Run all detectors
        all_detections = {}
        for detector in self.detectors:
            detections = detector.detect(values, timestamps)
            for detection in detections:
                idx = detection['index']
                if idx not in all_detections:
                    all_detections[idx] = {
                        'index': idx,
                        'value': detection['value'],
                        'detections': [],
                        'methods': []
                    }
                all_detections[idx]['detections'].append(detection)
                all_detections[idx]['methods'].append(detection['method'])

        # Filter by consensus
        anomalies = []
        for idx, detection_group in all_detections.items():
            if len(detection_group['detections']) >= min_consensus:
                # Calculate ensemble confidence
                confidences = [d['confidence'] for d in detection_group['detections']]
                ensemble_confidence = np.mean(confidences)

                anomaly = {
                    'index': idx,
                    'value': detection_group['value'],
                    'confidence': float(ensemble_confidence),
                    'consensus_count': len(detection_group['detections']),
                    'methods': detection_group['methods'],
                    'individual_detections': detection_group['detections'],
                    'method': 'ensemble'
                }

                if timestamps and idx < len(timestamps):
                    anomaly['timestamp'] = timestamps[idx]

                anomalies.append(anomaly)

        return anomalies
