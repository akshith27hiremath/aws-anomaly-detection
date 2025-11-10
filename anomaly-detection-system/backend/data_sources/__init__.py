"""
Data source clients for anomaly detection system.
"""

from .crypto_client import CryptoClient
from .github_client import GitHubClient
from .oi_derivatives_client import OIDerivativesClient
from .weather_client import WeatherClient

__all__ = ['CryptoClient', 'WeatherClient', 'GitHubClient', 'OIDerivativesClient']
