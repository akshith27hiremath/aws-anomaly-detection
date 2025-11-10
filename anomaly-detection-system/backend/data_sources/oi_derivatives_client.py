"""
Open Interest (OI) Derivatives data source client using Binance Futures API.
Fetches real-time open interest, funding rates, and long/short ratios for perpetual futures.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from backend.utils.config import get_detection_config, get_settings
from backend.utils.helpers import RateLimiter

logger = logging.getLogger(__name__)


class OIDerivativesClient:
    """
    Client for fetching Open Interest and derivatives data from Binance Futures API.
    Tracks OI, funding rates, and long/short ratios to detect market manipulation
    and divergence anomalies.
    """

    def __init__(self):
        """Initialize the OI derivatives client."""
        self.settings = get_settings()
        self.config = get_detection_config()

        # Binance Futures API (no auth required for public endpoints)
        self.base_url = "https://fapi.binance.com"

        # Get OI configuration from config or use defaults
        oi_config = self.config.get_data_source_config('oi_derivatives')
        self.symbols = oi_config.get('symbols', ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'])
        self.metrics = oi_config.get('metrics', [
            'open_interest',
            'funding_rate',
            'long_short_ratio',
            'top_trader_long_short_ratio'
        ])

        # Rate limiter: Binance allows 1200 requests per minute
        self.rate_limiter = RateLimiter(max_calls=1200, time_window=60)

        # Cache for recent data
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl = 30  # seconds

        # Historical OI data for divergence calculation
        self.oi_history: Dict[str, List[float]] = {}
        self.history_max_length = 100  # Keep last 100 data points

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch OI derivatives data for configured symbols.

        Returns:
            List of data points with timestamp and values
        """
        if not self._should_fetch():
            logger.debug("Using cached OI derivatives data")
            return self._format_cached_data()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Fetch data for all symbols in parallel
                tasks = [self._fetch_symbol_data(client, symbol) for symbol in self.symbols]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                data_points = []
                timestamp = datetime.now()

                for symbol, result in zip(self.symbols, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error fetching OI for {symbol}: {result}")
                        continue

                    if result:
                        # Store in cache
                        self.cache[symbol] = result

                        # Update OI history for divergence detection
                        if 'open_interest' in result and result['open_interest'] is not None:
                            if symbol not in self.oi_history:
                                self.oi_history[symbol] = []
                            self.oi_history[symbol].append(result['open_interest'])
                            # Keep only recent history
                            if len(self.oi_history[symbol]) > self.history_max_length:
                                self.oi_history[symbol] = self.oi_history[symbol][-self.history_max_length:]

                        # Create data points for each metric
                        for metric in self.metrics:
                            value = result.get(metric)
                            if value is not None:
                                data_points.append({
                                    'source': 'oi_derivatives',
                                    'symbol': symbol,
                                    'metric': metric,
                                    'value': value,
                                    'timestamp': timestamp,
                                    'metadata': {
                                        'api': 'binance_futures',
                                        'raw_data': result,
                                        'oi_change_pct': result.get('oi_change_pct'),
                                        'oi_history_length': len(self.oi_history.get(symbol, []))
                                    }
                                })

                self.cache_timestamp = timestamp
                logger.info(f"Fetched {len(data_points)} OI derivatives data points")
                return data_points

        except Exception as e:
            logger.error(f"Error in OI derivatives data fetch: {e}")
            return []

    async def _fetch_symbol_data(
        self,
        client: httpx.AsyncClient,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch OI derivatives data for a single symbol.

        Args:
            client: HTTP client
            symbol: Trading pair symbol (e.g., 'BTCUSDT')

        Returns:
            Dictionary with derivatives data or None
        """
        # Check rate limit
        if not self.rate_limiter.can_proceed():
            logger.warning("Rate limit reached for Binance Futures API")
            await asyncio.sleep(0.1)

        try:
            # Fetch multiple metrics in parallel
            oi_task = self._fetch_open_interest(client, symbol)
            funding_task = self._fetch_funding_rate(client, symbol)
            ratio_task = self._fetch_long_short_ratio(client, symbol)
            trader_ratio_task = self._fetch_top_trader_ratio(client, symbol)

            oi_data, funding_data, ratio_data, trader_ratio_data = await asyncio.gather(
                oi_task, funding_task, ratio_task, trader_ratio_task,
                return_exceptions=True
            )

            # Combine all data
            result = {
                'symbol': symbol,
                'open_interest': None,
                'open_interest_value': None,
                'funding_rate': None,
                'long_short_ratio': None,
                'top_trader_long_short_ratio': None,
                'oi_change_pct': None
            }

            # Parse Open Interest
            if not isinstance(oi_data, Exception) and oi_data:
                result['open_interest'] = float(oi_data.get('openInterest', 0))
                result['open_interest_value'] = float(oi_data.get('sumOpenInterestValue', 0))

            # Parse Funding Rate
            if not isinstance(funding_data, Exception) and funding_data:
                result['funding_rate'] = float(funding_data.get('lastFundingRate', 0)) * 100  # Convert to percentage

            # Parse Long/Short Ratio
            if not isinstance(ratio_data, Exception) and ratio_data:
                result['long_short_ratio'] = float(ratio_data.get('longShortRatio', 1.0))

            # Parse Top Trader Long/Short Ratio
            if not isinstance(trader_ratio_data, Exception) and trader_ratio_data:
                result['top_trader_long_short_ratio'] = float(trader_ratio_data.get('longShortRatio', 1.0))

            # Calculate OI change percentage if we have history
            if symbol in self.oi_history and len(self.oi_history[symbol]) > 0:
                if result['open_interest'] is not None:
                    prev_oi = self.oi_history[symbol][-1]
                    if prev_oi > 0:
                        result['oi_change_pct'] = ((result['open_interest'] - prev_oi) / prev_oi) * 100

            return result

        except Exception as e:
            logger.error(f"Error fetching derivatives data for {symbol}: {e}")
            return None

    async def _fetch_open_interest(
        self,
        client: httpx.AsyncClient,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch open interest data from Binance Futures."""
        try:
            url = f"{self.base_url}/fapi/v1/openInterest"
            params = {'symbol': symbol}

            response = await client.get(url, params=params)
            self.rate_limiter.record_call()

            if response.status_code == 200:
                return response.json()
            else:
                logger.debug(f"OI fetch failed for {symbol}: {response.status_code}")
        except Exception as e:
            logger.debug(f"Error fetching OI for {symbol}: {e}")

        return None

    async def _fetch_funding_rate(
        self,
        client: httpx.AsyncClient,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch funding rate data from Binance Futures."""
        try:
            url = f"{self.base_url}/fapi/v1/premiumIndex"
            params = {'symbol': symbol}

            response = await client.get(url, params=params)
            self.rate_limiter.record_call()

            if response.status_code == 200:
                return response.json()
            else:
                logger.debug(f"Funding rate fetch failed for {symbol}: {response.status_code}")
        except Exception as e:
            logger.debug(f"Error fetching funding rate for {symbol}: {e}")

        return None

    async def _fetch_long_short_ratio(
        self,
        client: httpx.AsyncClient,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch global long/short ratio from Binance Futures."""
        try:
            url = f"{self.base_url}/futures/data/globalLongShortAccountRatio"
            params = {
                'symbol': symbol,
                'period': '5m'  # 5-minute interval
            }

            response = await client.get(url, params=params)
            self.rate_limiter.record_call()

            if response.status_code == 200:
                data = response.json()
                # Return most recent data point
                return data[-1] if data else None
            else:
                logger.debug(f"Long/short ratio fetch failed for {symbol}: {response.status_code}")
        except Exception as e:
            logger.debug(f"Error fetching long/short ratio for {symbol}: {e}")

        return None

    async def _fetch_top_trader_ratio(
        self,
        client: httpx.AsyncClient,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch top trader long/short ratio from Binance Futures."""
        try:
            url = f"{self.base_url}/futures/data/topLongShortAccountRatio"
            params = {
                'symbol': symbol,
                'period': '5m'  # 5-minute interval
            }

            response = await client.get(url, params=params)
            self.rate_limiter.record_call()

            if response.status_code == 200:
                data = response.json()
                # Return most recent data point
                return data[-1] if data else None
            else:
                logger.debug(f"Top trader ratio fetch failed for {symbol}: {response.status_code}")
        except Exception as e:
            logger.debug(f"Error fetching top trader ratio for {symbol}: {e}")

        return None

    def _should_fetch(self) -> bool:
        """Check if new data should be fetched or use cache."""
        if not self.cache_timestamp:
            return True

        elapsed = (datetime.now() - self.cache_timestamp).total_seconds()
        return elapsed >= self.cache_ttl

    def _format_cached_data(self) -> List[Dict[str, Any]]:
        """Format cached data as data points."""
        data_points = []
        timestamp = self.cache_timestamp or datetime.now()

        for symbol, data in self.cache.items():
            for metric in self.metrics:
                value = data.get(metric)
                if value is not None:
                    data_points.append({
                        'source': 'oi_derivatives',
                        'symbol': symbol,
                        'metric': metric,
                        'value': value,
                        'timestamp': timestamp,
                        'metadata': {
                            'cached': True,
                            'api': 'binance_futures'
                        }
                    })

        return data_points

    def get_oi_divergence_signal(self, symbol: str, price_change_pct: float) -> Optional[Dict[str, Any]]:
        """
        Calculate OI divergence signal for a symbol.

        Args:
            symbol: Trading pair symbol
            price_change_pct: Price change percentage

        Returns:
            Divergence signal data or None
        """
        if symbol not in self.cache or symbol not in self.oi_history:
            return None

        oi_change_pct = self.cache[symbol].get('oi_change_pct')
        if oi_change_pct is None:
            return None

        # Detect divergence scenarios
        divergence_type = None
        severity = 'low'

        # Price up, OI down = Bearish divergence (potential reversal)
        if price_change_pct > 1 and oi_change_pct < -2:
            divergence_type = 'bearish_divergence'
            severity = 'high' if abs(oi_change_pct) > 5 else 'medium'

        # Price down, OI up = Bullish divergence (potential reversal)
        elif price_change_pct < -1 and oi_change_pct > 2:
            divergence_type = 'bullish_divergence'
            severity = 'high' if oi_change_pct > 5 else 'medium'

        # Price up, OI up strongly = Continuation signal
        elif price_change_pct > 2 and oi_change_pct > 5:
            divergence_type = 'bullish_continuation'
            severity = 'medium'

        # Price down, OI up strongly = Bearish continuation
        elif price_change_pct < -2 and oi_change_pct > 5:
            divergence_type = 'bearish_continuation'
            severity = 'medium'

        # Large OI spike (potential manipulation)
        elif abs(oi_change_pct) > 10:
            divergence_type = 'oi_spike_anomaly'
            severity = 'high'

        if divergence_type:
            return {
                'symbol': symbol,
                'divergence_type': divergence_type,
                'severity': severity,
                'price_change_pct': price_change_pct,
                'oi_change_pct': oi_change_pct,
                'current_oi': self.cache[symbol].get('open_interest'),
                'funding_rate': self.cache[symbol].get('funding_rate'),
                'long_short_ratio': self.cache[symbol].get('long_short_ratio')
            }

        return None

    async def get_historical_oi(
        self,
        symbol: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical OI data for analysis.

        Args:
            symbol: Trading pair symbol
            hours: Number of hours of historical data

        Returns:
            List of historical OI data points
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Use 5-minute intervals for recent data
                url = f"{self.base_url}/futures/data/openInterestHist"
                params = {
                    'symbol': symbol,
                    'period': '5m',
                    'limit': min(288, hours * 12)  # 288 = 24 hours of 5-min data
                }

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return [
                        {
                            'source': 'oi_derivatives',
                            'symbol': symbol,
                            'metric': 'open_interest',
                            'value': float(point['sumOpenInterest']),
                            'timestamp': datetime.fromtimestamp(point['timestamp'] / 1000),
                            'metadata': {
                                'open_interest_value': float(point['sumOpenInterestValue'])
                            }
                        }
                        for point in data
                    ]
                else:
                    logger.error(f"Error fetching historical OI: {response.status_code}")

        except Exception as e:
            logger.error(f"Error in historical OI fetch: {e}")

        return []
