"""
Universal Scraping Layer (Phase 1: Static Scraping)

A simple, focused scraping system for extracting data from static HTML websites.
"""

from .models import (
    ScriptConfig,
    ScrapingResult,
    ScrapingStrategy,
    StaticScrapingConfig,
    ScrapingError,
    ScrapingMetadata,
    PerformanceMetrics
)

from .interfaces import (
    IScrapingEngine,
    IStaticScraper
)

from .engine import ScrapingEngine
from .static_scraper import StaticScraper
from .config import ScrapingConfig, get_config, set_config

__all__ = [
    # Models
    'ScriptConfig',
    'ScrapingResult',
    'ScrapingStrategy',
    'StaticScrapingConfig',
    'ScrapingError',
    'ScrapingMetadata',
    'PerformanceMetrics',
    
    # Interfaces
    'IScrapingEngine',
    'IStaticScraper',
    
    # Implementations
    'ScrapingEngine',
    'StaticScraper',
    
    # Config
    'ScrapingConfig',
    'get_config',
    'set_config',
]

__version__ = '0.1.0-phase1'
