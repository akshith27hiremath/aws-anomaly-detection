"""
Cryptocurrency data source client using CoinGecko API.
Fetches real-time crypto prices, volumes, and market cap data.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from backend.utils.config import get_detection_config, get_settings
from backend.utils.helpers import RateLimiter

logger = logging.getLogger(__name__)


class CryptoClient:
    """
    Client for fetching cryptocurrency data from CoinGecko API.
    """

    def __init__(self):
        """Initialize the crypto client."""
        self.settings = get_settings()
        self.config = get_detection_config()
        self.base_url = self.settings.coingecko_base_url
        self.api_key = self.settings.coingecko_api_key

        # Get crypto configuration
        crypto_config = self.config.get_data_source_config('cryptocurrency')
        self.symbols = crypto_config.get('symbols', ['bitcoin', 'ethereum'])
        self.metrics = crypto_config.get('metrics', ['price_usd', 'volume_24h', 'market_cap'])

        # Rate limiter: 50 calls per minute for free tier
        self.rate_limiter = RateLimiter(max_calls=50, time_window=60)

        # Cache for recent data
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl = 30  # seconds

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch cryptocurrency data for configured symbols.

        Returns:
            List of data points with timestamp and values
        """
        if not self._should_fetch():
            logger.debug("Using cached crypto data")
            return self._format_cached_data()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Fetch data for all symbols
                tasks = [self._fetch_symbol_data(client, symbol) for symbol in self.symbols]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                data_points = []
                timestamp = datetime.now()

                for symbol, result in zip(self.symbols, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error fetching {symbol}: {result}")
                        continue

                    if result:
                        # Store in cache
                        self.cache[symbol] = result

                        # Create data points for each metric
                        for metric in self.metrics:
                            value = self._extract_metric_value(result, metric)
                            if value is not None:
                                data_points.append({
                                    'source': 'cryptocurrency',
                                    'symbol': symbol,
                                    'metric': metric,
                                    'value': value,
                                    'timestamp': timestamp,
                                    'metadata': {
                                        'api': 'coingecko',
                                        'raw_data': result
                                    }
                                })

                self.cache_timestamp = timestamp
                logger.info(f"Fetched {len(data_points)} crypto data points")
                return data_points

        except Exception as e:
            logger.error(f"Error in crypto data fetch: {e}")
            return []

    async def _fetch_symbol_data(
        self,
        client: httpx.AsyncClient,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch data for a single cryptocurrency symbol.

        Args:
            client: HTTP client
            symbol: Cryptocurrency symbol (e.g., 'bitcoin')

        Returns:
            Dictionary with symbol data or None
        """
        # Check rate limit
        if not self.rate_limiter.can_proceed():
            logger.warning("Rate limit reached for CoinGecko API")
            await asyncio.sleep(1)

        try:
            url = f"{self.base_url}/coins/{symbol}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            }

            if self.api_key:
                params['x_cg_demo_api_key'] = self.api_key

            response = await client.get(url, params=params)
            self.rate_limiter.record_call()

            if response.status_code == 200:
                data = response.json()
                return self._parse_coin_data(data)
            elif response.status_code == 429:
                logger.warning("Rate limited by CoinGecko API")
                await asyncio.sleep(5)
            else:
                logger.error(f"CoinGecko API error for {symbol}: {response.status_code}")

        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")

        return None

    def _parse_coin_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse coin data from API response.

        Args:
            data: Raw API response

        Returns:
            Parsed coin data
        """
        market_data = data.get('market_data', {})

        return {
            'price_usd': market_data.get('current_price', {}).get('usd'),
            'volume_24h': market_data.get('total_volume', {}).get('usd'),
            'market_cap': market_data.get('market_cap', {}).get('usd'),
            'price_change_24h': market_data.get('price_change_24h'),
            'price_change_percentage_24h': market_data.get('price_change_percentage_24h'),
            'market_cap_rank': data.get('market_cap_rank'),
            'circulating_supply': market_data.get('circulating_supply'),
            'total_supply': market_data.get('total_supply'),
            'ath': market_data.get('ath', {}).get('usd'),  # All-time high
            'atl': market_data.get('atl', {}).get('usd'),  # All-time low
        }

    def _extract_metric_value(
        self,
        data: Dict[str, Any],
        metric: str
    ) -> Optional[float]:
        """
        Extract specific metric value from parsed data.

        Args:
            data: Parsed coin data
            metric: Metric name

        Returns:
            Metric value or None
        """
        value = data.get(metric)
        if value is not None and not isinstance(value, bool):
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
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
                value = self._extract_metric_value(data, metric)
                if value is not None:
                    data_points.append({
                        'source': 'cryptocurrency',
                        'symbol': symbol,
                        'metric': metric,
                        'value': value,
                        'timestamp': timestamp,
                        'metadata': {
                            'cached': True,
                            'api': 'coingecko'
                        }
                    })

        return data_points

    async def get_historical_data(
        self,
        symbol: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical data for a cryptocurrency.

        Args:
            symbol: Cryptocurrency symbol
            days: Number of days of historical data

        Returns:
            List of historical data points
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                url = f"{self.base_url}/coins/{symbol}/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'hourly' if days <= 7 else 'daily'
                }

                if self.api_key:
                    params['x_cg_demo_api_key'] = self.api_key

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_historical_data(symbol, data)
                else:
                    logger.error(f"Error fetching historical data: {response.status_code}")

        except Exception as e:
            logger.error(f"Error in historical data fetch: {e}")

        return []

    def _parse_historical_data(
        self,
        symbol: str,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse historical data from API response."""
        data_points = []

        prices = data.get('prices', [])
        volumes = data.get('total_volumes', [])
        market_caps = data.get('market_caps', [])

        # Combine all data points
        for i in range(len(prices)):
            timestamp = datetime.fromtimestamp(prices[i][0] / 1000)

            data_points.append({
                'source': 'cryptocurrency',
                'symbol': symbol,
                'metric': 'price_usd',
                'value': prices[i][1],
                'timestamp': timestamp
            })

            if i < len(volumes):
                data_points.append({
                    'source': 'cryptocurrency',
                    'symbol': symbol,
                    'metric': 'volume_24h',
                    'value': volumes[i][1],
                    'timestamp': timestamp
                })

            if i < len(market_caps):
                data_points.append({
                    'source': 'cryptocurrency',
                    'symbol': symbol,
                    'metric': 'market_cap',
                    'value': market_caps[i][1],
                    'timestamp': timestamp
                })

        return data_points
