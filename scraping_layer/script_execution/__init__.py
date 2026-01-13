"""
Script Execution Layer - Direct script execution without AI generation.

This module provides functionality to accept pre-written scraping scripts
and execute them using the Universal Scraping Layer.
"""

from .models import ScrapingScript, ScriptResult, ScriptMetadata
from .executor import ScriptExecutor

__all__ = [
    'ScrapingScript',
    'ScriptResult', 
    'ScriptMetadata',
    'ScriptExecutor'
]