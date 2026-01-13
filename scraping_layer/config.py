"""
Configuration management for the Universal Scraping Layer.

This module provides centralized configuration management with environment
variable support and validation.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class SecurityConfig:
    """Security-related configuration."""
    max_script_execution_time: int = 300  # seconds
    max_memory_usage: int = 512  # MB
    allowed_domains: List[str] = field(default_factory=list)
    sandbox_temp_dir: str = "/tmp/scraping_sandbox"
    enable_script_validation: bool = True
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Create SecurityConfig from environment variables."""
        return cls(
            max_script_execution_time=int(os.getenv('SCRAPING_MAX_EXECUTION_TIME', 300)),
            max_memory_usage=int(os.getenv('SCRAPING_MAX_MEMORY_MB', 512)),
            allowed_domains=os.getenv('SCRAPING_ALLOWED_DOMAINS', '').split(',') if os.getenv('SCRAPING_ALLOWED_DOMAINS') else [],
            sandbox_temp_dir=os.getenv('SCRAPING_SANDBOX_DIR', '/tmp/scraping_sandbox'),
            enable_script_validation=os.getenv('SCRAPING_ENABLE_VALIDATION', 'true').lower() == 'true'
        )


@dataclass
class BrowserConfig:
    """Browser management configuration."""
    max_concurrent_browsers: int = 5
    browser_timeout: int = 30  # seconds
    browser_memory_limit: int = 1024  # MB
    headless: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    @classmethod
    def from_env(cls) -> 'BrowserConfig':
        """Create BrowserConfig from environment variables."""
        return cls(
            max_concurrent_browsers=int(os.getenv('SCRAPING_MAX_BROWSERS', 5)),
            browser_timeout=int(os.getenv('SCRAPING_BROWSER_TIMEOUT', 30)),
            browser_memory_limit=int(os.getenv('SCRAPING_BROWSER_MEMORY_LIMIT', 1024)),
            headless=os.getenv('SCRAPING_HEADLESS', 'true').lower() == 'true',
            user_agent=os.getenv('SCRAPING_USER_AGENT', cls.user_agent),
            viewport_width=int(os.getenv('SCRAPING_VIEWPORT_WIDTH', 1920)),
            viewport_height=int(os.getenv('SCRAPING_VIEWPORT_HEIGHT', 1080))
        )


@dataclass
class CacheConfig:
    """Cache management configuration."""
    cache_backend: str = "memory"  # memory, redis, file
    default_ttl: int = 3600  # seconds
    max_cache_size: int = 1000  # number of entries
    cache_directory: str = "./cache"
    redis_url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'CacheConfig':
        """Create CacheConfig from environment variables."""
        return cls(
            cache_backend=os.getenv('SCRAPING_CACHE_BACKEND', 'memory'),
            default_ttl=int(os.getenv('SCRAPING_CACHE_TTL', 3600)),
            max_cache_size=int(os.getenv('SCRAPING_CACHE_SIZE', 1000)),
            cache_directory=os.getenv('SCRAPING_CACHE_DIR', './cache'),
            redis_url=os.getenv('SCRAPING_REDIS_URL')
        )


@dataclass
class NetworkConfig:
    """Network-related configuration."""
    request_timeout: int = 30  # seconds
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    max_retry_delay: float = 60.0  # seconds
    user_agent_rotation: bool = True
    proxy_rotation: bool = False
    proxy_list: List[str] = field(default_factory=list)
    
    @classmethod
    def from_env(cls) -> 'NetworkConfig':
        """Create NetworkConfig from environment variables."""
        return cls(
            request_timeout=int(os.getenv('SCRAPING_REQUEST_TIMEOUT', 30)),
            max_retries=int(os.getenv('SCRAPING_MAX_RETRIES', 3)),
            retry_delay=float(os.getenv('SCRAPING_RETRY_DELAY', 1.0)),
            max_retry_delay=float(os.getenv('SCRAPING_MAX_RETRY_DELAY', 60.0)),
            user_agent_rotation=os.getenv('SCRAPING_USER_AGENT_ROTATION', 'true').lower() == 'true',
            proxy_rotation=os.getenv('SCRAPING_PROXY_ROTATION', 'false').lower() == 'true',
            proxy_list=os.getenv('SCRAPING_PROXY_LIST', '').split(',') if os.getenv('SCRAPING_PROXY_LIST') else []
        )


@dataclass
class LoggingConfig:
    """Logging configuration."""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    enable_performance_logging: bool = True
    enable_security_logging: bool = True
    
    @classmethod
    def from_env(cls) -> 'LoggingConfig':
        """Create LoggingConfig from environment variables."""
        return cls(
            log_level=os.getenv('SCRAPING_LOG_LEVEL', 'INFO'),
            log_format=os.getenv('SCRAPING_LOG_FORMAT', cls.log_format),
            log_file=os.getenv('SCRAPING_LOG_FILE'),
            enable_performance_logging=os.getenv('SCRAPING_PERFORMANCE_LOGGING', 'true').lower() == 'true',
            enable_security_logging=os.getenv('SCRAPING_SECURITY_LOGGING', 'true').lower() == 'true'
        )


@dataclass
class ScrapingConfig:
    """Main configuration class that combines all configuration sections."""
    security: SecurityConfig = field(default_factory=SecurityConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    @classmethod
    def from_env(cls) -> 'ScrapingConfig':
        """Create complete configuration from environment variables."""
        return cls(
            security=SecurityConfig.from_env(),
            browser=BrowserConfig.from_env(),
            cache=CacheConfig.from_env(),
            network=NetworkConfig.from_env(),
            logging=LoggingConfig.from_env()
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ScrapingConfig':
        """Load configuration from a file (JSON or YAML)."""
        import json
        
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            if config_path.endswith('.json'):
                config_data = json.load(f)
            elif config_path.endswith(('.yml', '.yaml')):
                try:
                    import yaml
                    config_data = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML is required to load YAML configuration files")
            else:
                raise ValueError("Configuration file must be JSON or YAML")
        
        return cls.from_dict(config_data)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ScrapingConfig':
        """Create configuration from a dictionary."""
        return cls(
            security=SecurityConfig(**config_dict.get('security', {})),
            browser=BrowserConfig(**config_dict.get('browser', {})),
            cache=CacheConfig(**config_dict.get('cache', {})),
            network=NetworkConfig(**config_dict.get('network', {})),
            logging=LoggingConfig(**config_dict.get('logging', {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        from dataclasses import asdict
        return asdict(self)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate security config
        if self.security.max_script_execution_time <= 0:
            errors.append("Security: max_script_execution_time must be positive")
        
        if self.security.max_memory_usage <= 0:
            errors.append("Security: max_memory_usage must be positive")
        
        # Validate browser config
        if self.browser.max_concurrent_browsers <= 0:
            errors.append("Browser: max_concurrent_browsers must be positive")
        
        if self.browser.browser_timeout <= 0:
            errors.append("Browser: browser_timeout must be positive")
        
        # Validate cache config
        if self.cache.cache_backend not in ['memory', 'redis', 'file']:
            errors.append("Cache: cache_backend must be 'memory', 'redis', or 'file'")
        
        if self.cache.default_ttl <= 0:
            errors.append("Cache: default_ttl must be positive")
        
        # Validate network config
        if self.network.request_timeout <= 0:
            errors.append("Network: request_timeout must be positive")
        
        if self.network.max_retries < 0:
            errors.append("Network: max_retries must be non-negative")
        
        return errors


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
    
    # Validate configuration
    errors = config.validate()
    if errors:
        raise ValueError(f"Invalid configuration: {', '.join(errors)}")
    
    _config = config


def load_config_from_file(config_path: str) -> None:
    """Load configuration from file and set as global config."""
    config = ScrapingConfig.from_file(config_path)
    set_config(config)