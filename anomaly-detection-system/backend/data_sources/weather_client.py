"""
Weather data source client using Open-Meteo API.
Fetches real-time weather data for multiple cities (free, no API key required).
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from backend.utils.config import get_detection_config, get_settings
from backend.utils.helpers import RateLimiter

logger = logging.getLogger(__name__)


class WeatherClient:
    """
    Client for fetching weather data from Open-Meteo API.
    Open-Meteo is free, no API key required, and has excellent uptime.
    """

    def __init__(self):
        """Initialize the weather client."""
        self.settings = get_settings()
        self.config = get_detection_config()
        self.base_url = "https://api.open-meteo.com/v1"

        # Get weather configuration
        weather_config = self.config.get_data_source_config('weather')
        self.cities = weather_config.get('cities', [])
        self.metrics = weather_config.get('metrics', ['temperature', 'humidity', 'pressure'])

        # Rate limiter: 10,000 calls per day for free tier (essentially unlimited)
        self.rate_limiter = RateLimiter(max_calls=10000, time_window=86400)

        # Cache for recent data
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamp: Optional[datetime] = None
        self.cache_ttl = 60  # seconds

    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch weather data for configured cities.

        Returns:
            List of data points with timestamp and values
        """
        if not self._should_fetch():
            logger.debug("Using cached weather data")
            return self._format_cached_data()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Fetch data for all cities
                tasks = [self._fetch_city_data(client, city) for city in self.cities]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                data_points = []
                timestamp = datetime.now()

                for city, result in zip(self.cities, results):
                    if isinstance(result, Exception):
                        logger.error(f"Error fetching {city['name']}: {result}")
                        continue

                    if result:
                        city_name = city['name']
                        # Store in cache
                        self.cache[city_name] = result

                        # Create data points for each metric
                        for metric in self.metrics:
                            value = self._extract_metric_value(result, metric)
                            if value is not None:
                                data_points.append({
                                    'source': 'weather',
                                    'city': city_name,
                                    'metric': metric,
                                    'value': value,
                                    'timestamp': timestamp,
                                    'metadata': {
                                        'api': 'open-meteo',
                                        'coordinates': {
                                            'lat': city['lat'],
                                            'lon': city['lon']
                                        },
                                        'raw_data': result
                                    }
                                })

                self.cache_timestamp = timestamp
                logger.info(f"Fetched {len(data_points)} weather data points")
                return data_points

        except Exception as e:
            logger.error(f"Error in weather data fetch: {e}")
            return []

    async def _fetch_city_data(
        self,
        client: httpx.AsyncClient,
        city: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data for a single city using Open-Meteo API.

        Args:
            client: HTTP client
            city: City configuration with lat/lon

        Returns:
            Dictionary with weather data or None
        """
        # Check rate limit
        if not self.rate_limiter.can_proceed():
            logger.warning("Rate limit reached for Open-Meteo API")
            await asyncio.sleep(1)

        try:
            url = f"{self.base_url}/forecast"
            params = {
                'latitude': city['lat'],
                'longitude': city['lon'],
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,pressure_msl',
                'timezone': 'auto'
            }

            response = await client.get(url, params=params)
            self.rate_limiter.record_call()

            if response.status_code == 200:
                data = response.json()
                return self._parse_weather_data(data)
            elif response.status_code == 429:
                logger.warning("Rate limited by Open-Meteo API")
                await asyncio.sleep(5)
            else:
                logger.error(f"Open-Meteo API error for {city['name']}: {response.status_code}")

        except Exception as e:
            logger.error(f"Error fetching {city['name']}: {e}")

        return None

    def _parse_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse weather data from Open-Meteo API response.

        Args:
            data: Raw API response

        Returns:
            Parsed weather data
        """
        current = data.get('current', {})

        return {
            'temperature': current.get('temperature_2m'),  # Celsius
            'humidity': current.get('relative_humidity_2m'),  # Percentage
            'pressure': current.get('pressure_msl'),  # hPa
            'wind_speed': current.get('wind_speed_10m'),  # km/h
            'weather_code': current.get('weather_code'),  # WMO code
        }

    def _extract_metric_value(
        self,
        data: Dict[str, Any],
        metric: str
    ) -> Optional[float]:
        """
        Extract specific metric value from parsed data.

        Args:
            data: Parsed weather data
            metric: Metric name

        Returns:
            Metric value or None
        """
        value = data.get(metric)
        if value is not None and not isinstance(value, (bool, str)):
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

        for city_name, data in self.cache.items():
            for metric in self.metrics:
                value = self._extract_metric_value(data, metric)
                if value is not None:
                    data_points.append({
                        'source': 'weather',
                        'city': city_name,
                        'metric': metric,
                        'value': value,
                        'timestamp': timestamp,
                        'metadata': {
                            'cached': True,
                            'api': 'open-meteo'
                        }
                    })

        return data_points

    async def get_forecast(
        self,
        city: Dict[str, Any],
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Fetch weather forecast for a city using Open-Meteo.

        Args:
            city: City configuration with lat/lon
            days: Number of days of forecast (Open-Meteo free tier supports up to 16 days)

        Returns:
            List of forecast data points
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{self.base_url}/forecast"
                params = {
                    'latitude': city['lat'],
                    'longitude': city['lon'],
                    'daily': 'temperature_2m_max,temperature_2m_min,relative_humidity_2m_max,pressure_msl_max,wind_speed_10m_max',
                    'timezone': 'auto',
                    'forecast_days': days
                }

                response = await client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_forecast_data(city['name'], data)
                else:
                    logger.error(f"Error fetching forecast: {response.status_code}")

        except Exception as e:
            logger.error(f"Error in forecast fetch: {e}")

        return []

    def _parse_forecast_data(
        self,
        city_name: str,
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse forecast data from Open-Meteo API response."""
        data_points = []

        daily = data.get('daily', {})
        time_list = daily.get('time', [])
        temp_max = daily.get('temperature_2m_max', [])
        temp_min = daily.get('temperature_2m_min', [])
        humidity_max = daily.get('relative_humidity_2m_max', [])
        pressure = daily.get('pressure_msl_max', [])
        wind_speed = daily.get('wind_speed_10m_max', [])

        for i, timestamp_str in enumerate(time_list):
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except:
                continue

            # Create data point for max temperature
            if i < len(temp_max) and temp_max[i] is not None:
                data_points.append({
                    'source': 'weather_forecast',
                    'city': city_name,
                    'metric': 'temperature',
                    'value': float(temp_max[i]),
                    'timestamp': timestamp
                })

            # Create data point for humidity
            if i < len(humidity_max) and humidity_max[i] is not None:
                data_points.append({
                    'source': 'weather_forecast',
                    'city': city_name,
                    'metric': 'humidity',
                    'value': float(humidity_max[i]),
                    'timestamp': timestamp
                })

            # Create data point for pressure
            if i < len(pressure) and pressure[i] is not None:
                data_points.append({
                    'source': 'weather_forecast',
                    'city': city_name,
                    'metric': 'pressure',
                    'value': float(pressure[i]),
                    'timestamp': timestamp
                })

        return data_points
