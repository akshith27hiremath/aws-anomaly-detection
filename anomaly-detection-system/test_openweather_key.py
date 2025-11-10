"""
Test OpenWeather API key validity.
Usage: python test_openweather_key.py YOUR_API_KEY
"""

import sys
import httpx

def test_openweather_key(api_key):
    """Test if OpenWeather API key works."""

    if not api_key:
        print("❌ Error: No API key provided")
        print("Usage: python test_openweather_key.py YOUR_API_KEY")
        return False

    # Test with a simple request to New York
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': 40.7128,
        'lon': -74.0060,
        'appid': api_key,
        'units': 'metric'
    }

    print(f"Testing OpenWeather API key: {api_key[:20]}...")
    print(f"Request URL: {url}")
    print(f"Parameters: {params}\n")

    try:
        response = httpx.get(url, params=params, timeout=10.0)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("[SUCCESS] Your API key works!")
            data = response.json()
            print(f"City: {data.get('name')}")
            print(f"Temperature: {data.get('main', {}).get('temp')}°C")
            print(f"Weather: {data.get('weather', [{}])[0].get('main')}")
            return True

        elif response.status_code == 401:
            print("[FAILED] 401 Unauthorized")
            print("Reasons:")
            print("  1. API key is incorrect")
            print("  2. API key is not activated yet (wait 10-15 mins after creation)")
            print("  3. Account email not verified")
            print("\nFix: Go to https://openweathermap.org/api and verify your account")

        elif response.status_code == 429:
            print("[FAILED] 429 Rate Limited")
            print("Your key might be working but you've hit the rate limit.")
            print("Wait a few minutes and try again.")

        else:
            print(f"[FAILED] HTTP {response.status_code}")
            print(f"Response: {response.text}")

        return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_openweather_key.py YOUR_API_KEY")
        print("\nExample:")
        print("  python test_openweather_key.py 316a7ef8c31293707012b026f74d3b74")
        sys.exit(1)

    api_key = sys.argv[1]
    success = test_openweather_key(api_key)
    sys.exit(0 if success else 1)
