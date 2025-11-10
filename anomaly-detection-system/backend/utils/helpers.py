"""
Helper utilities for the anomaly detection system.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats


# Configure logging
def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def calculate_confidence(
    deviation: float,
    threshold: float,
    scale: float = 1.0
) -> float:
    """
    Calculate confidence score based on deviation from threshold.

    Args:
        deviation: Magnitude of deviation
        threshold: Detection threshold
        scale: Scaling factor for sigmoid function

    Returns:
        Confidence score between 0 and 1
    """
    if threshold == 0:
        return 1.0 if deviation > 0 else 0.0

    # Use sigmoid function for smooth confidence scaling
    ratio = deviation / threshold
    confidence = 1 / (1 + np.exp(-scale * (ratio - 1)))
    return float(np.clip(confidence, 0.0, 1.0))


def normalize_values(values: List[float]) -> np.ndarray:
    """
    Normalize values to 0-1 range.

    Args:
        values: List of values to normalize

    Returns:
        Normalized numpy array
    """
    arr = np.array(values)
    min_val = np.min(arr)
    max_val = np.max(arr)

    if max_val == min_val:
        return np.ones_like(arr)

    return (arr - min_val) / (max_val - min_val)


def weighted_average(
    values: List[float],
    weights: List[float]
) -> float:
    """
    Calculate weighted average.

    Args:
        values: Values to average
        weights: Weights for each value

    Returns:
        Weighted average
    """
    if not values or not weights or len(values) != len(weights):
        return 0.0

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0

    return sum(v * w for v, w in zip(values, weights)) / total_weight


def calculate_severity(
    confidence: float,
    deviation_magnitude: float,
    impact_scope: int = 1,
    is_novel: bool = False
) -> Tuple[str, float]:
    """
    Calculate anomaly severity based on multiple factors.

    Args:
        confidence: Detection confidence (0-1)
        deviation_magnitude: Magnitude of deviation from normal
        impact_scope: Number of metrics/sources affected
        is_novel: Whether this is a novel anomaly pattern

    Returns:
        Tuple of (severity_label, severity_score)
    """
    # Base score from confidence
    score = confidence * 0.4

    # Add deviation magnitude contribution (normalized)
    deviation_score = min(deviation_magnitude / 10.0, 1.0) * 0.3
    score += deviation_score

    # Add impact scope contribution
    scope_score = min(impact_scope / 5.0, 1.0) * 0.2
    score += scope_score

    # Add novelty bonus
    if is_novel:
        score += 0.1

    score = min(score, 1.0)

    # Determine severity label
    if score >= 0.9:
        label = "critical"
    elif score >= 0.75:
        label = "high"
    elif score >= 0.5:
        label = "medium"
    else:
        label = "low"

    return label, float(score)


def generate_anomaly_fingerprint(
    source: str,
    metric: str,
    pattern: Dict[str, Any]
) -> str:
    """
    Generate unique fingerprint for anomaly pattern.

    Args:
        source: Data source name
        metric: Metric name
        pattern: Pattern characteristics

    Returns:
        Hex string fingerprint
    """
    # Create deterministic string from pattern
    pattern_str = f"{source}:{metric}:"
    pattern_str += f"{pattern.get('type', 'unknown')}:"
    pattern_str += f"{pattern.get('magnitude', 0):.2f}:"
    pattern_str += f"{pattern.get('duration', 0)}"

    # Generate hash
    return hashlib.sha256(pattern_str.encode()).hexdigest()[:16]


def time_window_filter(
    timestamps: List[datetime],
    values: List[float],
    window_start: datetime,
    window_end: datetime
) -> Tuple[List[datetime], List[float]]:
    """
    Filter data points within a time window.

    Args:
        timestamps: List of timestamps
        values: List of corresponding values
        window_start: Start of time window
        window_end: End of time window

    Returns:
        Tuple of (filtered_timestamps, filtered_values)
    """
    filtered_times = []
    filtered_vals = []

    for ts, val in zip(timestamps, values):
        if window_start <= ts <= window_end:
            filtered_times.append(ts)
            filtered_vals.append(val)

    return filtered_times, filtered_vals


def detect_seasonality(values: np.ndarray, period: int = 24) -> Dict[str, Any]:
    """
    Detect seasonal patterns in time series data.

    Args:
        values: Array of time series values
        period: Expected seasonal period

    Returns:
        Dictionary with seasonality information
    """
    if len(values) < period * 2:
        return {"has_seasonality": False, "strength": 0.0}

    # Simple seasonality detection using autocorrelation
    try:
        # Calculate autocorrelation at seasonal lag
        autocorr = np.correlate(values - np.mean(values), values - np.mean(values), mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]

        if len(autocorr) > period:
            seasonal_autocorr = autocorr[period]
            has_seasonality = seasonal_autocorr > 0.5

            return {
                "has_seasonality": bool(has_seasonality),
                "strength": float(seasonal_autocorr),
                "period": period
            }
    except Exception:
        pass

    return {"has_seasonality": False, "strength": 0.0}


def calculate_trend(values: np.ndarray) -> Dict[str, Any]:
    """
    Calculate trend in time series data.

    Args:
        values: Array of time series values

    Returns:
        Dictionary with trend information
    """
    if len(values) < 3:
        return {"direction": "stable", "strength": 0.0, "slope": 0.0}

    # Linear regression for trend
    x = np.arange(len(values))
    slope, intercept, r_value, _, _ = stats.linregress(x, values)

    # Determine trend direction
    if abs(slope) < 0.01 * np.std(values):
        direction = "stable"
    elif slope > 0:
        direction = "increasing"
    else:
        direction = "decreasing"

    return {
        "direction": direction,
        "strength": float(abs(r_value)),
        "slope": float(slope),
        "intercept": float(intercept)
    }


def format_timestamp(dt: datetime, include_seconds: bool = True) -> str:
    """
    Format datetime for display.

    Args:
        dt: Datetime to format
        include_seconds: Whether to include seconds

    Returns:
        Formatted string
    """
    if include_seconds:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt.strftime("%Y-%m-%d %H:%M")


def calculate_time_diff_human(dt1: datetime, dt2: datetime) -> str:
    """
    Calculate human-readable time difference.

    Args:
        dt1: First datetime
        dt2: Second datetime

    Returns:
        Human-readable string (e.g., "5 minutes ago")
    """
    diff = abs(dt2 - dt1)

    if diff.total_seconds() < 60:
        return f"{int(diff.total_seconds())} seconds"
    elif diff.total_seconds() < 3600:
        return f"{int(diff.total_seconds() / 60)} minutes"
    elif diff.total_seconds() < 86400:
        return f"{int(diff.total_seconds() / 3600)} hours"
    else:
        return f"{int(diff.total_seconds() / 86400)} days"


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: List[datetime] = []

    def can_proceed(self) -> bool:
        """Check if a new call can proceed."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)

        # Remove old calls
        self.calls = [call for call in self.calls if call > cutoff]

        return len(self.calls) < self.max_calls

    def record_call(self) -> None:
        """Record a new call."""
        self.calls.append(datetime.now())
