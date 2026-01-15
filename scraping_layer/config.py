"""
Configuration management for the Universal Scraping Layer (Phase 1: Static Scraping).

This module provides minimal configuration for static HTML scraping.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class NetworkConfig:
    """Network-related configuration."""
    request_timeout: int = 30  # seconds
    # Full User-Agent string that Wikipedia and other sites accept
    # Wikipedia requires a descriptive User-Agent per their policy
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36 "
        "AIAPIGenerator/1.0 (Educational/Research Project; Contact: admin@example.com)"
    )
    
    @classmethod
    def from_env(cls) -> 'NetworkConfig':
        """Create NetworkConfig from environment variables."""
        return cls(
            request_timeout=int(os.getenv('SCRAPING_REQUEST_TIMEOUT', 30)),
            user_agent=os.getenv('SCRAPING_USER_AGENT', cls.user_agent)
        )


@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create LoggingConfig from environment variables."""
        return cls(
            log_level=os.getenv('SCRAPING_LOG_LEVEL', 'INFO'),
            log_format=os.getenv('SCRAPING_LOG_FORMAT', cls.log_format)
        )


@dataclass
class ScrapingConfig:
    """Main configuration class."""
    network: NetworkConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        if self.network is None:
            self.network = NetworkConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
    
    @classmethod
    def from_env(cls) -> 'ScrapingConfig':
        """Create complete configuration from environment variables."""
        return cls(
            network=NetworkConfig.from_env(),
            logging=LoggingConfig.from_env()
        )


# Global configuration instance
_config: Optional[ScrapingConfig] = None


def get_config() -> ScrapingConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = ScrapingConfig.from_env()
    return _config


def set_config(config: ScrapingConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
