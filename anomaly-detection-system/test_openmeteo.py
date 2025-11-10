"""
Test script to verify Open-Meteo weather API integration.
"""

import asyncio
from backend.data_sources import WeatherClient


async def test_weather_client():
    """Test the weather client with Open-Meteo API."""
    print("=" * 60)
    print("Testing Open-Meteo Weather API Integration")
    print("=" * 60)

    client = WeatherClient()
    print(f"\nFetching weather data for {len(client.cities)} cities...")
    print(f"Cities: {[city['name'] for city in client.cities]}\n")

    data = await client.fetch_data()

    if data:
        print(f"[SUCCESS] Fetched {len(data)} data points!")
        print("\nSample data points:")
        for i, point in enumerate(data[:5]):
            print(f"  {i+1}. {point['city']}: {point['metric']} = {point['value']}")
        return True
    else:
        print("[FAILED] No data fetched")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_weather_client())
    exit(0 if success else 1)
