"""
OI (Open Interest) Agent - Specialized agent for derivatives market anomaly detection.
Detects price-OI divergences, funding rate extremes, and long/short ratio imbalances.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.detection.oi_detectors import (
    FundingRateDetector,
    LongShortRatioDetector,
    OIDivergenceDetector,
    OIFeatureEngineer,
)
from backend.utils.config import get_detection_config
from backend.utils.helpers import calculate_severity

logger = logging.getLogger(__name__)


class OIAgent:
    """
    Agent specialized in Open Interest derivatives anomaly detection.
    Detects divergences, funding rate extremes, and market manipulation signals.
    """

    def __init__(self):
        """Initialize the OI agent."""
        self.config = get_detection_config()
        agent_config = self.config.get_agent_config('oi_derivatives')

        # Default weight and confidence if not configured
        self.weight = agent_config.get('weight', 0.20)
        self.min_confidence = agent_config.get('min_confidence', 0.6)

        # Initialize detectors
        self.divergence_detector = OIDivergenceDetector()
        self.funding_detector = FundingRateDetector()
        self.ratio_detector = LongShortRatioDetector()
        self.feature_engineer = OIFeatureEngineer()

        self.name = "OIAgent"

    async def analyze(
        self,
        data_points: List[Dict[str, Any]],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze OI derivatives data for anomalies.

        Args:
            data_points: Current data points to analyze
            historical_data: Historical data for context

        Returns:
            Analysis results with detected anomalies
        """
        logger.info(f"{self.name}: Starting OI derivatives analysis on {len(data_points)} data points")

        # Filter for OI derivatives data only
        oi_data_points = [
            dp for dp in data_points
            if dp.get('source') == 'oi_derivatives'
        ]

        if not oi_data_points:
            logger.info(f"{self.name}: No OI derivatives data found")
            return {
                'agent': self.name,
                'weight': self.weight,
                'anomalies': [],
                'metadata': {
                    'message': 'No OI derivatives data available'
                }
            }

        # Also get crypto price data for divergence detection
        crypto_data_points = [
            dp for dp in data_points
            if dp.get('source') == 'cryptocurrency'
        ]

        # Group data by symbol
        oi_by_symbol = self._group_by_symbol(oi_data_points)
        crypto_by_symbol = self._group_by_symbol(crypto_data_points)

        anomalies = []
        analysis_metadata = []

        for symbol, oi_data in oi_by_symbol.items():
            symbol_anomalies = []

            # Extract metrics from OI data
            oi_values = []
            funding_rates = []
            long_short_ratios = []
            top_trader_ratios = []
            timestamps = []

            for point in oi_data:
                metric = point.get('metric')
                value = point.get('value')
                timestamp = point.get('timestamp', datetime.now())

                if metric == 'open_interest' and value is not None:
                    oi_values.append(value)
                elif metric == 'funding_rate' and value is not None:
                    funding_rates.append(value)
                    timestamps.append(timestamp)
                elif metric == 'long_short_ratio' and value is not None:
                    long_short_ratios.append(value)
                elif metric == 'top_trader_long_short_ratio' and value is not None:
                    top_trader_ratios.append(value)

            # 1. Detect price-OI divergences
            if symbol in crypto_by_symbol and len(oi_values) >= 2:
                crypto_data = crypto_by_symbol[symbol]
                price_data = [p for p in crypto_data if p.get('metric') == 'price_usd']

                if len(price_data) >= 2:
                    # Calculate price changes
                    prices = [p['value'] for p in price_data[-2:]]
                    price_change_pct = ((prices[-1] - prices[-2]) / prices[-2]) * 100 if prices[-2] > 0 else 0

                    # Calculate OI changes
                    oi_change_pct = ((oi_values[-1] - oi_values[-2]) / oi_values[-2]) * 100 if len(oi_values) >= 2 and oi_values[-2] > 0 else 0

                    # Detect divergences
                    divergence_results = self.divergence_detector.detect(
                        price_changes=[price_change_pct],
                        oi_changes=[oi_change_pct],
                        timestamps=[timestamps[-1]] if timestamps else None,
                        symbols=[symbol],
                        additional_data={
                            'funding_rate': funding_rates[-1:] if funding_rates else [],
                            'long_short_ratio': long_short_ratios[-1:] if long_short_ratios else []
                        }
                    )

                    for detection in divergence_results:
                        if detection['confidence'] >= self.min_confidence:
                            anomaly = self._create_anomaly(detection, 'divergence')
                            symbol_anomalies.append(anomaly)

            # 2. Detect funding rate anomalies
            if funding_rates:
                funding_results = self.funding_detector.detect(
                    funding_rates=funding_rates,
                    timestamps=timestamps if timestamps else None,
                    symbols=[symbol] * len(funding_rates)
                )

                for detection in funding_results:
                    if detection['confidence'] >= self.min_confidence:
                        anomaly = self._create_anomaly(detection, 'funding_rate')
                        symbol_anomalies.append(anomaly)

            # 3. Detect long/short ratio imbalances (global)
            if long_short_ratios:
                ratio_results = self.ratio_detector.detect(
                    ratios=long_short_ratios,
                    timestamps=timestamps if timestamps else None,
                    symbols=[symbol] * len(long_short_ratios),
                    is_top_trader=False
                )

                for detection in ratio_results:
                    if detection['confidence'] >= self.min_confidence:
                        anomaly = self._create_anomaly(detection, 'long_short_ratio')
                        symbol_anomalies.append(anomaly)

            # 4. Detect top trader ratio imbalances (more significant)
            if top_trader_ratios:
                top_trader_results = self.ratio_detector.detect(
                    ratios=top_trader_ratios,
                    timestamps=timestamps if timestamps else None,
                    symbols=[symbol] * len(top_trader_ratios),
                    is_top_trader=True
                )

                for detection in top_trader_results:
                    if detection['confidence'] >= self.min_confidence:
                        anomaly = self._create_anomaly(detection, 'top_trader_ratio')
                        symbol_anomalies.append(anomaly)

            anomalies.extend(symbol_anomalies)

            analysis_metadata.append({
                'symbol': symbol,
                'oi_data_points': len(oi_data),
                'anomalies_found': len(symbol_anomalies),
                'metrics_analyzed': {
                    'oi_values': len(oi_values),
                    'funding_rates': len(funding_rates),
                    'long_short_ratios': len(long_short_ratios),
                    'top_trader_ratios': len(top_trader_ratios)
                }
            })

        logger.info(f"{self.name}: Found {len(anomalies)} OI derivatives anomalies")

        return {
            'agent': self.name,
            'weight': self.weight,
            'anomalies': anomalies,
            'metadata': {
                'symbols_analyzed': len(oi_by_symbol),
                'total_anomalies': len(anomalies),
                'analysis_details': analysis_metadata
            }
        }

    def _group_by_symbol(
        self,
        data_points: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group data points by symbol."""
        grouped = {}

        for point in data_points:
            symbol = point.get('symbol', 'unknown')

            if symbol not in grouped:
                grouped[symbol] = []

            grouped[symbol].append(point)

        return grouped

    def _create_anomaly(
        self,
        detection: Dict[str, Any],
        detection_type: str
    ) -> Dict[str, Any]:
        """Create standardized anomaly object from detection."""
        # Calculate severity
        severity_label, severity_score = calculate_severity(
            confidence=detection.get('confidence', 0.0),
            deviation_magnitude=abs(detection.get('oi_change_pct', 0.0)) / 10,  # Normalize
            impact_scope=1.5 if detection.get('severity') == 'high' else 1.0
        )

        anomaly = {
            'agent': self.name,
            'source': 'oi_derivatives',
            'symbol': detection.get('symbol', 'unknown'),
            'timestamp': detection.get('timestamp', datetime.now()),
            'detection_type': detection_type,
            'confidence': detection.get('confidence', 0.0),
            'severity': severity_label,
            'severity_score': severity_score,
            'detection_methods': [detection.get('method', 'oi_analysis')],
            'explanation': detection.get('explanation', 'OI derivatives anomaly detected'),
            'metadata': {
                key: value for key, value in detection.items()
                if key not in ['timestamp', 'confidence', 'explanation', 'method', 'severity']
            }
        }

        return anomaly

    def _generate_narrative(
        self,
        detection: Dict[str, Any],
        detection_type: str
    ) -> str:
        """Generate narrative explanation for the anomaly."""
        if detection_type == 'divergence':
            div_type = detection.get('divergence_type', 'unknown')
            price_chg = detection.get('price_change_pct', 0.0)
            oi_chg = detection.get('oi_change_pct', 0.0)

            narratives = {
                'bearish_divergence': f"⚠️ Bearish Divergence: Price rose {price_chg:.2f}% but Open Interest fell {abs(oi_chg):.2f}%. This suggests profit-taking and weakening bullish momentum, indicating potential reversal.",
                'bullish_divergence': f"📈 Bullish Divergence: Price dropped {abs(price_chg):.2f}% yet Open Interest increased {oi_chg:.2f}%. This suggests bottom formation and potential bullish reversal.",
                'bullish_continuation': f"🚀 Bullish Continuation: Strong uptrend with price +{price_chg:.2f}% and OI +{oi_chg:.2f}%. New positions being added, momentum is strong.",
                'bearish_continuation': f"📉 Bearish Setup: Price down {abs(price_chg):.2f}% with OI up {oi_chg:.2f}%. Potential short squeeze or strong bearish conviction.",
                'oi_spike_anomaly': f"🔔 OI Spike Alert: Unusual {oi_chg:.2f}% change in Open Interest. Possible whale activity, manipulation, or approaching liquidation cascade."
            }

            return narratives.get(div_type, detection.get('explanation', ''))

        elif detection_type == 'funding_rate':
            rate = detection.get('funding_rate', 0.0)
            signal = detection.get('signal', '')

            if 'extreme' in signal:
                direction = 'longs' if rate > 0 else 'shorts'
                return f"💥 Extreme funding rate {rate:.4f}% indicates {direction} are heavily dominant. Market is {'overbought' if rate > 0 else 'oversold'}, reversal risk is high."
            else:
                direction = 'long' if rate > 0 else 'short'
                return f"⚡ Elevated funding rate {rate:.4f}% shows strong {direction} bias in the market."

        elif detection_type in ['long_short_ratio', 'top_trader_ratio']:
            ratio = detection.get('long_short_ratio', 1.0)
            is_top = detection_type == 'top_trader_ratio'
            trader_type = "Top traders" if is_top else "Overall market"

            direction = 'long' if ratio > 1 else 'short'
            return f"{'🎯' if is_top else '📊'} {trader_type} showing {ratio:.2f}:1 {direction} bias. Crowded trade detected, squeeze risk elevated."

        return detection.get('explanation', 'OI derivatives anomaly detected')
