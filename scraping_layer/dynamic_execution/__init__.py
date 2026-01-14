"""
Dynamic Execution Module for AI-Scraping Layer Integration.

This module provides components for safely executing AI-generated scraper scripts
and displaying results on the console.

Components:
- DynamicScriptExecutor: Executes AI-generated Python scripts safely
- ScriptSandbox: Provides isolated execution environment
- ConsoleOutputFormatter: Formats and displays scraping results
- AIScrapingIntegration: Main orchestrator connecting AI and scraping layers
"""

import logging

from .models import (
    ExecutionConfig,
    ExecutionResult,
    ExecutionMetadata,
    SourceResult,
)

from .exceptions import (
    ScriptExecutionError,
    SecurityError,
    ScriptTimeoutError,
    ScriptSyntaxError,
    ScriptRuntimeError,
)

from .executor import DynamicScriptExecutor
from .formatter import ConsoleOutputFormatter
from .sandbox import ScriptSandbox
from .integration import AIScrapingIntegration, create_integration


def configure_logging(
    level: int = logging.INFO,
    format_string: str = None,
    handler: logging.Handler = None
) -> None:
    """
    Configure logging for the dynamic execution module.
    
    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string
        handler: Custom handler (default: StreamHandler)
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Get the module logger
    logger = logging.getLogger('scraping_layer.dynamic_execution')
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Add handler
    if handler is None:
        handler = logging.StreamHandler()
    
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(handler)


__all__ = [
    # Models
    'ExecutionConfig',
    'ExecutionResult',
    'ExecutionMetadata',
    'SourceResult',
    # Exceptions
    'ScriptExecutionError',
    'SecurityError',
    'ScriptTimeoutError',
    'ScriptSyntaxError',
    'ScriptRuntimeError',
    # Components
    'DynamicScriptExecutor',
    'ConsoleOutputFormatter',
    'ScriptSandbox',
    'AIScrapingIntegration',
    # Factory functions
    'create_integration',
    'configure_logging',
]
