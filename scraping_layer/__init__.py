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

# Dynamic Execution (AI-Scraping Integration)
from .dynamic_execution import (
    DynamicScriptExecutor,
    ConsoleOutputFormatter,
    AIScrapingIntegration,
    create_integration,
    configure_logging,
    ExecutionConfig,
    ExecutionResult,
    ExecutionMetadata,
    SourceResult,
    ScriptExecutionError,
    SecurityError,
    ScriptTimeoutError,
    ScriptSyntaxError,
    ScriptRuntimeError,
)

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
    
    # Dynamic Execution (AI-Scraping Integration)
    'DynamicScriptExecutor',
    'ConsoleOutputFormatter',
    'AIScrapingIntegration',
    'create_integration',
    'configure_logging',
    'ExecutionConfig',
    'ExecutionResult',
    'ExecutionMetadata',
    'SourceResult',
    'ScriptExecutionError',
    'SecurityError',
    'ScriptTimeoutError',
    'ScriptSyntaxError',
    'ScriptRuntimeError',
]

__version__ = '0.2.0-phase1'
