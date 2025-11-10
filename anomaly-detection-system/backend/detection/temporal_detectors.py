"""
Temporal and time-series anomaly detection algorithms.
Implements changepoint detection, trend analysis, and seasonal decomposition.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import signal, stats
from backend.utils.config import get_detection_config
from backend.utils.helpers import calculate_confidence, calculate_trend, detect_seasonality

logger = logging.getLogger(__name__)


class ChangePointDetector:
    """
    Detects abrupt changes in time series data.
    Uses statistical methods to identify regime changes.
    """

    def __init__(self, min_size: int = 5, penalty: float = 10):
        """
        Initialize changepoint detector.

        Args:
            min_size: Minimum segment size
            penalty: Penalty for adding changepoints (higher = fewer changepoints)
        """
        self.config = get_detection_config()

        params = self.config.get_detection_params('changepoint')
        if params:
            min_size = params.get('min_size', min_size)
            penalty = params.get('penalty', penalty)

        self.min_size = min_size
        self.penalty = penalty

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect changepoints in time series.

        Args:
            values: Time series values
            timestamps: Optional timestamps

        Returns:
            List of changepoint anomalies
        """
        if len(values) < self.min_size * 2:
            return []

        arr = np.array(values)
        changepoints = self._detect_changepoints(arr)

        anomalies = []
        for cp_idx in changepoints:
            # Calculate statistics before and after changepoint
            before = arr[max(0, cp_idx - self.min_size):cp_idx]
            after = arr[cp_idx:min(len(arr), cp_idx + self.min_size)]

            if len(before) > 0 and len(after) > 0:
                mean_before = np.mean(before)
                mean_after = np.mean(after)
                std_before = np.std(before)

                # Calculate magnitude of change
                change_magnitude = abs(mean_after - mean_before)

                if std_before > 0:
                    significance = change_magnitude / std_before
                    confidence = calculate_confidence(significance, 2.0, scale=0.5)
                else:
                    confidence = 0.5

                anomaly = {
                    'index': cp_idx,
                    'value': float(values[cp_idx]),
                    'mean_before': float(mean_before),
                    'mean_after': float(mean_after),
                    'change_magnitude': float(change_magnitude),
                    'confidence': confidence,
                    'method': 'changepoint',
                    'type': 'regime_change'
                }

                if timestamps and cp_idx < len(timestamps):
                    anomaly['timestamp'] = timestamps[cp_idx]

                anomalies.append(anomaly)

        return anomalies

    def _detect_changepoints(self, arr: np.ndarray) -> List[int]:
        """
        Internal method to detect changepoints using PELT-like algorithm.

        Args:
            arr: Array of values

        Returns:
            List of changepoint indices
        """
        changepoints = []
        n = len(arr)

        if n < self.min_size * 2:
            return changepoints

        # Simple binary segmentation approach
        def find_best_split(start: int, end: int) -> Tuple[int, float]:
            """Find best split point in range."""
            best_idx = start + self.min_size
            best_cost = float('inf')

            for i in range(start + self.min_size, end - self.min_size):
                left = arr[start:i]
                right = arr[i:end]

                # Calculate cost as variance reduction
                total_var = np.var(arr[start:end]) * (end - start)
                split_var = np.var(left) * len(left) + np.var(right) * len(right)
                cost = total_var - split_var - self.penalty

                if cost < best_cost:
                    best_cost = cost
                    best_idx = i

            return best_idx, best_cost

        # Recursive binary segmentation
        def segment(start: int, end: int):
            """Recursively segment the series."""
            if end - start < self.min_size * 2:
                return

            idx, cost = find_best_split(start, end)

            # If cost improvement is significant, add changepoint
            if cost < -self.penalty:
                changepoints.append(idx)
                segment(start, idx)
                segment(idx, end)

        segment(0, n)
        return sorted(changepoints)


class TrendAnomalyDetector:
    """
    Detects anomalies based on trend deviations.
    """

    def __init__(self, window_size: int = 20):
        """
        Initialize trend anomaly detector.

        Args:
            window_size: Window for trend calculation
        """
        self.window_size = window_size

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect trend-based anomalies.

        Args:
            values: Time series values
            timestamps: Optional timestamps

        Returns:
            List of trend anomalies
        """
        if len(values) < self.window_size:
            return []

        arr = np.array(values)
        anomalies = []

        # Calculate global trend
        global_trend = calculate_trend(arr)
        global_slope = global_trend['slope']

        # Look for local trend reversals
        for i in range(self.window_size, len(values) - self.window_size):
            window = arr[i - self.window_size:i + self.window_size]
            local_trend = calculate_trend(window)
            local_slope = local_trend['slope']

            # Detect significant trend change
            if abs(global_slope) > 0.001:
                slope_change = abs(local_slope - global_slope) / abs(global_slope)

                if slope_change > 1.5:  # 150% change in slope
                    confidence = min(slope_change / 3.0, 1.0)

                    anomaly = {
                        'index': i,
                        'value': float(values[i]),
                        'global_slope': float(global_slope),
                        'local_slope': float(local_slope),
                        'slope_change': float(slope_change),
                        'confidence': float(confidence),
                        'method': 'trend_deviation',
                        'type': 'trend_reversal'
                    }

                    if timestamps and i < len(timestamps):
                        anomaly['timestamp'] = timestamps[i]

                    anomalies.append(anomaly)

        return anomalies


class SeasonalAnomalyDetector:
    """
    Detects anomalies by removing seasonal patterns and finding residual outliers.
    """

    def __init__(self, period: int = 24):
        """
        Initialize seasonal anomaly detector.

        Args:
            period: Expected seasonal period
        """
        self.period = period

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect seasonal anomalies.

        Args:
            values: Time series values
            timestamps: Optional timestamps

        Returns:
            List of seasonal anomalies
        """
        if len(values) < self.period * 2:
            return []

        arr = np.array(values)

        # Check for seasonality
        seasonality_info = detect_seasonality(arr, self.period)

        if not seasonality_info['has_seasonality']:
            logger.debug("No seasonality detected, skipping seasonal anomaly detection")
            return []

        # Simple seasonal decomposition
        seasonal_pattern = self._extract_seasonal_pattern(arr)
        deseasonalized = arr - seasonal_pattern[:len(arr)]

        # Find outliers in deseasonalized series
        mean = np.mean(deseasonalized)
        std = np.std(deseasonalized)

        if std == 0:
            return []

        anomalies = []
        threshold = 3.0

        for i, (orig_val, deseas_val) in enumerate(zip(values, deseasonalized)):
            z_score = abs(deseas_val - mean) / std

            if z_score > threshold:
                expected_seasonal = seasonal_pattern[i % self.period]
                expected_value = mean + expected_seasonal

                confidence = calculate_confidence(z_score, threshold, scale=0.5)

                anomaly = {
                    'index': i,
                    'value': float(orig_val),
                    'expected_value': float(expected_value),
                    'seasonal_component': float(expected_seasonal),
                    'residual': float(deseas_val),
                    'z_score': float(z_score),
                    'confidence': confidence,
                    'method': 'seasonal_decomposition',
                    'type': 'seasonal_outlier'
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                anomalies.append(anomaly)

        return anomalies

    def _extract_seasonal_pattern(self, arr: np.ndarray) -> np.ndarray:
        """
        Extract seasonal pattern using averaging.

        Args:
            arr: Time series array

        Returns:
            Seasonal pattern array
        """
        n = len(arr)
        seasonal = np.zeros(self.period)

        # Average values at each seasonal position
        for i in range(self.period):
            indices = np.arange(i, n, self.period)
            if len(indices) > 0:
                seasonal[i] = np.mean(arr[indices])

        # Center the seasonal pattern
        seasonal = seasonal - np.mean(seasonal)

        return seasonal


class ExponentialSmoothingDetector:
    """
    Detects anomalies using exponential smoothing forecast errors.
    """

    def __init__(self, alpha: float = 0.3, threshold: float = 3.0):
        """
        Initialize exponential smoothing detector.

        Args:
            alpha: Smoothing parameter (0-1)
            threshold: Threshold for anomaly detection
        """
        self.config = get_detection_config()

        params = self.config.get_detection_params('exponential_smoothing')
        if params:
            alpha = params.get('alpha', alpha)

        self.alpha = alpha
        self.threshold = threshold

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using exponential smoothing.

        Args:
            values: Time series values
            timestamps: Optional timestamps

        Returns:
            List of anomalies
        """
        if len(values) < 5:
            return []

        anomalies = []
        forecast = values[0]
        errors = []

        # Calculate forecasts and errors
        for i, value in enumerate(values[1:], 1):
            error = abs(value - forecast)
            errors.append(error)

            # Update forecast
            forecast = self.alpha * value + (1 - self.alpha) * forecast

            # Check if error is anomalous (after enough data)
            if i > 10:
                error_mean = np.mean(errors)
                error_std = np.std(errors)

                if error_std > 0:
                    z_score = (error - error_mean) / error_std

                    if z_score > self.threshold:
                        confidence = calculate_confidence(z_score, self.threshold, scale=0.5)

                        anomaly = {
                            'index': i,
                            'value': float(value),
                            'expected_value': float(forecast),
                            'forecast_error': float(error),
                            'z_score': float(z_score),
                            'confidence': confidence,
                            'method': 'exponential_smoothing',
                            'type': 'forecast_error'
                        }

                        if timestamps and i < len(timestamps):
                            anomaly['timestamp'] = timestamps[i]

                        anomalies.append(anomaly)

        return anomalies


class MovingAverageCrossoverDetector:
    """
    Detects anomalies when short-term and long-term moving averages diverge significantly.
    """

    def __init__(self, short_window: int = 5, long_window: int = 20, threshold: float = 0.15):
        """
        Initialize MA crossover detector.

        Args:
            short_window: Short moving average window
            long_window: Long moving average window
            threshold: Deviation threshold for anomaly
        """
        self.config = get_detection_config()

        params = self.config.get_detection_params('moving_average')
        if params:
            short_window = params.get('short_window', short_window)
            long_window = params.get('long_window', long_window)
            threshold = params.get('deviation_threshold', threshold)

        self.short_window = short_window
        self.long_window = long_window
        self.threshold = threshold

    def detect(
        self,
        values: List[float],
        timestamps: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """Detect MA crossover anomalies."""
        if len(values) < self.long_window:
            return []

        arr = np.array(values)
        anomalies = []

        for i in range(self.long_window, len(values)):
            short_ma = np.mean(arr[i - self.short_window:i])
            long_ma = np.mean(arr[i - self.long_window:i])

            if long_ma != 0:
                deviation = abs(short_ma - long_ma) / long_ma

                if deviation > self.threshold:
                    confidence = min(deviation / self.threshold, 1.0)

                    anomaly = {
                        'index': i,
                        'value': float(values[i]),
                        'short_ma': float(short_ma),
                        'long_ma': float(long_ma),
                        'deviation': float(deviation),
                        'confidence': float(confidence),
                        'method': 'ma_crossover',
                        'type': 'moving_average_divergence'
                    }

                    if timestamps and i < len(timestamps):
                        anomaly['timestamp'] = timestamps[i]

                    anomalies.append(anomaly)

        return anomalies
