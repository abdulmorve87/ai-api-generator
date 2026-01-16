"""
Configuration management for the Universal Scraping Layer (Phase 1: Static Scraping).

This module provides minimal configuration for static HTML scraping.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict


# Default headers that mimic a real browser to avoid 403 errors
# These headers work for most public websites including ESPN, Cricbuzz, Wikipedia, etc.
DEFAULT_BROWSER_HEADERS: Dict[str, str] = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def get_default_headers() -> Dict[str, str]:
    """Get a copy of the default browser headers."""
    return DEFAULT_BROWSER_HEADERS.copy()


def get_headers_as_python_dict_string() -> str:
    """Get headers formatted as a Python dict string for code generation."""
    lines = ["headers = {"]
    for key, value in DEFAULT_BROWSER_HEADERS.items():
        lines.append(f"    '{key}': '{value}',")
    lines.append("}")
    return "\n".join(lines)


@dataclass
class NetworkConfig:
    """Network-related configuration."""
    request_timeout: int = 30  # seconds
    # Full User-Agent string that Wikipedia and other sites accept
    # Wikipedia requires a descriptive User-Agent per their policy
    user_agent: str = DEFAULT_BROWSER_HEADERS['User-Agent']
    # Complete headers dict for requests
    default_headers: Dict[str, str] = field(default_factory=get_default_headers)
    
    @classmethod
    def from_env(cls) -> 'NetworkConfig':
        """Create NetworkConfig from environment variables."""
        headers = get_default_headers()
        custom_ua = os.getenv('SCRAPING_USER_AGENT')
        if custom_ua:
            headers['User-Agent'] = custom_ua
        return cls(
            request_timeout=int(os.getenv('SCRAPING_REQUEST_TIMEOUT', 30)),
            user_agent=headers['User-Agent'],
            default_headers=headers
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
