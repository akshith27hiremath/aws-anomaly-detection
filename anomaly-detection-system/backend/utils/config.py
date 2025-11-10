"""
Configuration management for the anomaly detection system.
Loads settings from environment variables and YAML configuration files.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # API Keys
    coingecko_api_key: Optional[str] = Field(default=None, alias="COINGECKO_API_KEY")
    openweather_api_key: Optional[str] = Field(default=None, alias="OPENWEATHER_API_KEY")
    github_token: Optional[str] = Field(default=None, alias="GITHUB_TOKEN")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    # API URLs
    coingecko_base_url: str = Field(
        default="https://api.coingecko.com/api/v3",
        alias="COINGECKO_BASE_URL"
    )
    openweather_base_url: str = Field(
        default="https://api.openweathermap.org/data/2.5",
        alias="OPENWEATHER_BASE_URL"
    )
    github_base_url: str = Field(
        default="https://api.github.com",
        alias="GITHUB_BASE_URL"
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Detection Configuration
    zscore_threshold: float = Field(default=3.0, alias="ZSCORE_THRESHOLD")
    iqr_multiplier: float = Field(default=1.5, alias="IQR_MULTIPLIER")
    confidence_threshold: float = Field(default=0.7, alias="CONFIDENCE_THRESHOLD")
    min_samples_for_detection: int = Field(default=10, alias="MIN_SAMPLES_FOR_DETECTION")

    # Data Collection
    collection_interval_seconds: int = Field(default=60, alias="COLLECTION_INTERVAL_SECONDS")
    data_retention_days: int = Field(default=30, alias="DATA_RETENTION_DAYS")

    # Alert Configuration
    alert_severity_high: float = Field(default=0.8, alias="ALERT_SEVERITY_HIGH")
    alert_severity_medium: float = Field(default=0.6, alias="ALERT_SEVERITY_MEDIUM")
    alert_severity_low: float = Field(default=0.4, alias="ALERT_SEVERITY_LOW")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./anomaly_detection.db",
        alias="DATABASE_URL"
    )

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="CORS_ORIGINS"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DetectionConfig:
    """
    Detection algorithm configuration loaded from YAML file.
    """

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "detection_config.yaml"

        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Configuration key in dot notation (e.g., 'statistical.zscore.threshold')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def get_data_source_config(self, source: str) -> Dict[str, Any]:
        """Get configuration for a specific data source."""
        return self.config.get('data_sources', {}).get(source, {})

    def get_agent_config(self, agent: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        return self.config.get('agents', {}).get(agent, {})

    def get_detection_params(self, method: str) -> Dict[str, Any]:
        """Get parameters for a specific detection method."""
        # Check in statistical, temporal, or ml sections
        for section in ['statistical', 'temporal', 'ml', 'correlation']:
            if method in self.config.get(section, {}):
                return self.config[section][method]
        return {}

    def is_enabled(self, method: str) -> bool:
        """Check if a detection method is enabled."""
        params = self.get_detection_params(method)
        return params.get('enabled', False)


# Global instances
settings = Settings()
detection_config = DetectionConfig()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings


def get_detection_config() -> DetectionConfig:
    """Get detection configuration instance."""
    return detection_config
