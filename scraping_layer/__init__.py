"""
Universal Scraping Layer

A comprehensive scraping system that handles both static and dynamic websites
with AI-generated script execution, security sandboxing, and intelligent
strategy selection.
"""

__version__ = "1.0.0"
__author__ = "AI API Generator Team"

# Import core models first
from .models import ScriptConfig, ScrapingResult, WebsiteAnalysis

# Import engine (now that dependencies are resolved)
from .engine import ScrapingEngine

__all__ = [
    "ScrapingEngine",
    "ScriptConfig", 
    "ScrapingResult",
    "WebsiteAnalysis"
]