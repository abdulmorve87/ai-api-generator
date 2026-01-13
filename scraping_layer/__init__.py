"""
Universal Scraping Layer

A comprehensive scraping system that handles both static and dynamic websites
with direct script execution and intelligent strategy selection.
"""

__version__ = "1.0.0"
__author__ = "AI API Generator Team"

# Import core models first
from .models import ScriptConfig, ScrapingResult, WebsiteAnalysis

# Import engine (now that dependencies are resolved)
from .engine import ScrapingEngine

# Import script execution layer
from .script_execution import ScrapingScript, ScriptExecutor, ScriptResult

__all__ = [
    "ScrapingEngine",
    "ScriptConfig", 
    "ScrapingResult",
    "WebsiteAnalysis",
    "ScrapingScript",
    "ScriptExecutor", 
    "ScriptResult"
]