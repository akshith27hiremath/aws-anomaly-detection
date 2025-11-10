"""
Open Interest (OI) specific anomaly detection algorithms.
Implements divergence detection, OI spike detection, and funding rate anomalies.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from backend.utils.config import get_detection_config
from backend.utils.helpers import calculate_confidence

logger = logging.getLogger(__name__)


class OIDivergenceDetector:
    """
    Detects price-OI divergences that signal potential market reversals or manipulation.

    Scenarios:
    - Bearish Divergence: Price up + OI down = Potential reversal down
    - Bullish Divergence: Price down + OI up = Potential reversal up
    - Bullish Continuation: Price up + OI up = Strong uptrend
    - Bearish Continuation: Price down + OI down = Strong downtrend
    """

    def __init__(
        self,
        price_threshold: float = 1.0,
        oi_threshold: float = 2.0,
        spike_threshold: float = 10.0
    ):
        """
        Initialize OI divergence detector.

        Args:
            price_threshold: Minimum price change % to consider
            oi_threshold: Minimum OI change % to consider
            spike_threshold: Large OI change % indicating spike
        """
        self.config = get_detection_config()
        self.price_threshold = price_threshold
        self.oi_threshold = oi_threshold
        self.spike_threshold = spike_threshold

        # Load from config if available
        divergence_config = self.config.get('data_sources.oi_derivatives.divergence_detection', {})
        if divergence_config:
            self.price_threshold = divergence_config.get('price_threshold', self.price_threshold)
            self.oi_threshold = divergence_config.get('oi_threshold', self.oi_threshold)
            self.spike_threshold = divergence_config.get('spike_threshold', self.spike_threshold)

    def detect(
        self,
        price_changes: List[float],
        oi_changes: List[float],
        timestamps: Optional[List[Any]] = None,
        symbols: Optional[List[str]] = None,
        additional_data: Optional[Dict[str, List[float]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect price-OI divergences.

        Args:
            price_changes: List of price change percentages
            oi_changes: List of OI change percentages
            timestamps: Optional timestamps for each data point
            symbols: Optional symbol names
            additional_data: Optional dict with funding_rate, long_short_ratio, etc.

        Returns:
            List of detected divergence anomalies
        """
        if len(price_changes) != len(oi_changes):
            logger.warning("Price and OI change lists have different lengths")
            return []

        if len(price_changes) == 0:
            return []

        anomalies = []

        for i, (price_chg, oi_chg) in enumerate(zip(price_changes, oi_changes)):
            divergence_type = None
            severity = 'low'
            confidence = 0.0

            # Bearish Divergence: Price up, OI down
            if price_chg > self.price_threshold and oi_chg < -self.oi_threshold:
                divergence_type = 'bearish_divergence'
                # Higher confidence if divergence is stronger
                confidence = min(0.95, 0.6 + (abs(oi_chg) / 20))
                severity = 'high' if abs(oi_chg) > 5 else 'medium'

            # Bullish Divergence: Price down, OI up
            elif price_chg < -self.price_threshold and oi_chg > self.oi_threshold:
                divergence_type = 'bullish_divergence'
                confidence = min(0.95, 0.6 + (oi_chg / 20))
                severity = 'high' if oi_chg > 5 else 'medium'

            # Bullish Continuation: Price up, OI up strongly
            elif price_chg > 2 and oi_chg > 5:
                divergence_type = 'bullish_continuation'
                confidence = min(0.9, 0.5 + (oi_chg / 30))
                severity = 'medium'

            # Bearish Continuation: Price down, OI up strongly (potential squeeze)
            elif price_chg < -2 and oi_chg > 5:
                divergence_type = 'bearish_continuation'
                confidence = min(0.9, 0.5 + (oi_chg / 30))
                severity = 'medium'

            # OI Spike Anomaly: Large OI change regardless of price
            elif abs(oi_chg) > self.spike_threshold:
                divergence_type = 'oi_spike_anomaly'
                confidence = min(0.95, 0.7 + (abs(oi_chg) / 50))
                severity = 'high' if abs(oi_chg) > 20 else 'medium'

            if divergence_type:
                anomaly = {
                    'index': i,
                    'divergence_type': divergence_type,
                    'price_change_pct': float(price_chg),
                    'oi_change_pct': float(oi_chg),
                    'confidence': confidence,
                    'severity': severity,
                    'method': 'oi_divergence',
                    'explanation': self._generate_explanation(divergence_type, price_chg, oi_chg)
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                if symbols and i < len(symbols):
                    anomaly['symbol'] = symbols[i]

                # Add additional metrics if available
                if additional_data:
                    for key, values in additional_data.items():
                        if i < len(values):
                            anomaly[key] = float(values[i])

                anomalies.append(anomaly)

        logger.info(f"Detected {len(anomalies)} OI divergence anomalies")
        return anomalies

    def _generate_explanation(
        self,
        divergence_type: str,
        price_chg: float,
        oi_chg: float
    ) -> str:
        """Generate human-readable explanation for divergence."""
        explanations = {
            'bearish_divergence': f"Price increased {price_chg:.2f}% while OI decreased {abs(oi_chg):.2f}%. This suggests weakening bullish momentum and potential reversal.",
            'bullish_divergence': f"Price decreased {abs(price_chg):.2f}% while OI increased {oi_chg:.2f}%. This suggests weakening bearish momentum and potential reversal.",
            'bullish_continuation': f"Price increased {price_chg:.2f}% with OI increasing {oi_chg:.2f}%. Strong bullish momentum with new positions being added.",
            'bearish_continuation': f"Price decreased {abs(price_chg):.2f}% while OI increased {oi_chg:.2f}%. Potential short squeeze setup or strong bearish conviction.",
            'oi_spike_anomaly': f"Unusual OI change of {oi_chg:.2f}% detected. This may indicate market manipulation, large whale activity, or approaching liquidation cascade."
        }

        return explanations.get(divergence_type, f"Divergence detected: price={price_chg:.2f}%, OI={oi_chg:.2f}%")


class FundingRateDetector:
    """
    Detects anomalous funding rates that indicate market imbalance.
    Extreme funding rates can signal overbought/oversold conditions.
    """

    def __init__(
        self,
        extreme_threshold: float = 0.1,  # 0.1% = very high
        moderate_threshold: float = 0.05  # 0.05% = moderate
    ):
        """
        Initialize funding rate detector.

        Args:
            extreme_threshold: Funding rate % considered extreme
            moderate_threshold: Funding rate % considered moderate
        """
        self.config = get_detection_config()
        self.extreme_threshold = extreme_threshold
        self.moderate_threshold = moderate_threshold

    def detect(
        self,
        funding_rates: List[float],
        timestamps: Optional[List[Any]] = None,
        symbols: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous funding rates.

        Args:
            funding_rates: List of funding rates (in percentage)
            timestamps: Optional timestamps
            symbols: Optional symbol names

        Returns:
            List of funding rate anomalies
        """
        if len(funding_rates) == 0:
            return []

        anomalies = []

        for i, rate in enumerate(funding_rates):
            if abs(rate) >= self.extreme_threshold:
                # Extreme funding rate
                anomaly = {
                    'index': i,
                    'funding_rate': float(rate),
                    'severity': 'high',
                    'confidence': min(0.95, 0.7 + (abs(rate) / 0.2)),
                    'method': 'funding_rate',
                    'signal': 'extreme_long_pressure' if rate > 0 else 'extreme_short_pressure',
                    'explanation': f"Extreme funding rate of {rate:.4f}% indicates {'overbought' if rate > 0 else 'oversold'} conditions. Potential reversal or forced liquidations."
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                if symbols and i < len(symbols):
                    anomaly['symbol'] = symbols[i]

                anomalies.append(anomaly)

            elif abs(rate) >= self.moderate_threshold:
                # Moderate funding rate
                anomaly = {
                    'index': i,
                    'funding_rate': float(rate),
                    'severity': 'medium',
                    'confidence': 0.6 + (abs(rate) / 0.15),
                    'method': 'funding_rate',
                    'signal': 'high_long_pressure' if rate > 0 else 'high_short_pressure',
                    'explanation': f"Elevated funding rate of {rate:.4f}% indicates strong {'long' if rate > 0 else 'short'} bias in the market."
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                if symbols and i < len(symbols):
                    anomaly['symbol'] = symbols[i]

                anomalies.append(anomaly)

        logger.info(f"Detected {len(anomalies)} funding rate anomalies")
        return anomalies


class LongShortRatioDetector:
    """
    Detects extreme long/short ratio imbalances that indicate crowded trades.
    """

    def __init__(
        self,
        extreme_ratio: float = 3.0,  # 3:1 ratio considered extreme
        moderate_ratio: float = 2.0   # 2:1 ratio considered moderate
    ):
        """
        Initialize long/short ratio detector.

        Args:
            extreme_ratio: Ratio considered extremely imbalanced
            moderate_ratio: Ratio considered moderately imbalanced
        """
        self.config = get_detection_config()
        self.extreme_ratio = extreme_ratio
        self.moderate_ratio = moderate_ratio

    def detect(
        self,
        ratios: List[float],
        timestamps: Optional[List[Any]] = None,
        symbols: Optional[List[str]] = None,
        is_top_trader: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Detect extreme long/short ratio imbalances.

        Args:
            ratios: List of long/short ratios
            timestamps: Optional timestamps
            symbols: Optional symbol names
            is_top_trader: Whether this is top trader data (more significant)

        Returns:
            List of ratio anomalies
        """
        if len(ratios) == 0:
            return []

        anomalies = []

        for i, ratio in enumerate(ratios):
            # Check for extreme ratios (both high and low)
            if ratio >= self.extreme_ratio or ratio <= (1 / self.extreme_ratio):
                direction = 'long' if ratio > 1 else 'short'
                anomaly = {
                    'index': i,
                    'long_short_ratio': float(ratio),
                    'severity': 'high' if is_top_trader else 'medium',
                    'confidence': min(0.9, 0.65 + (abs(np.log(ratio)) / 5)),
                    'method': 'long_short_ratio',
                    'signal': f'extreme_{direction}_crowding',
                    'trader_type': 'top_traders' if is_top_trader else 'global',
                    'explanation': f"Extreme {direction} bias detected with ratio {ratio:.2f}. Crowded trade may lead to squeeze or rapid reversal."
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                if symbols and i < len(symbols):
                    anomaly['symbol'] = symbols[i]

                anomalies.append(anomaly)

            elif ratio >= self.moderate_ratio or ratio <= (1 / self.moderate_ratio):
                direction = 'long' if ratio > 1 else 'short'
                anomaly = {
                    'index': i,
                    'long_short_ratio': float(ratio),
                    'severity': 'low',
                    'confidence': 0.5 + (abs(np.log(ratio)) / 8),
                    'method': 'long_short_ratio',
                    'signal': f'elevated_{direction}_bias',
                    'trader_type': 'top_traders' if is_top_trader else 'global',
                    'explanation': f"Elevated {direction} bias with ratio {ratio:.2f}. Monitor for potential reversal."
                }

                if timestamps and i < len(timestamps):
                    anomaly['timestamp'] = timestamps[i]

                if symbols and i < len(symbols):
                    anomaly['symbol'] = symbols[i]

                anomalies.append(anomaly)

        logger.info(f"Detected {len(anomalies)} long/short ratio anomalies")
        return anomalies


class OIFeatureEngineer:
    """
    Engineers advanced features from OI data for better anomaly detection.
    Calculates ΔOI, OI momentum, OI-price correlation, etc.
    """

    @staticmethod
    def calculate_oi_delta(oi_values: List[float]) -> List[float]:
        """Calculate change in OI (ΔOI)."""
        if len(oi_values) < 2:
            return []

        deltas = []
        for i in range(1, len(oi_values)):
            delta = ((oi_values[i] - oi_values[i-1]) / oi_values[i-1]) * 100 if oi_values[i-1] > 0 else 0
            deltas.append(delta)

        return deltas

    @staticmethod
    def calculate_oi_momentum(oi_values: List[float], window: int = 5) -> List[float]:
        """Calculate OI momentum using moving average of ΔOI."""
        deltas = OIFeatureEngineer.calculate_oi_delta(oi_values)

        if len(deltas) < window:
            return deltas

        momentum = []
        for i in range(len(deltas)):
            if i < window - 1:
                momentum.append(np.mean(deltas[:i+1]))
            else:
                momentum.append(np.mean(deltas[i-window+1:i+1]))

        return momentum

    @staticmethod
    def calculate_oi_price_correlation(
        oi_values: List[float],
        price_values: List[float],
        window: int = 20
    ) -> List[float]:
        """Calculate rolling correlation between OI and price."""
        if len(oi_values) != len(price_values) or len(oi_values) < window:
            return []

        oi_arr = np.array(oi_values)
        price_arr = np.array(price_values)

        correlations = []
        for i in range(len(oi_arr)):
            if i < window - 1:
                correlations.append(0.0)
            else:
                oi_window = oi_arr[i-window+1:i+1]
                price_window = price_arr[i-window+1:i+1]

                # Calculate Pearson correlation
                correlation = np.corrcoef(oi_window, price_window)[0, 1]
                correlations.append(correlation if not np.isnan(correlation) else 0.0)

        return correlations

    @staticmethod
    def calculate_oi_zscore(oi_values: List[float], window: int = 30) -> List[float]:
        """Calculate rolling Z-score of OI values."""
        if len(oi_values) < window:
            return [0.0] * len(oi_values)

        oi_arr = np.array(oi_values)
        zscores = []

        for i in range(len(oi_arr)):
            if i < window - 1:
                zscores.append(0.0)
            else:
                window_data = oi_arr[i-window+1:i+1]
                mean = np.mean(window_data)
                std = np.std(window_data)

                if std > 0:
                    zscore = (oi_arr[i] - mean) / std
                    zscores.append(float(zscore))
                else:
                    zscores.append(0.0)

        return zscores
