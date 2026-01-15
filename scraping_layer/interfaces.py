"""
Core interfaces for the Universal Scraping Layer (Phase 1: Static Scraping).

This module defines the minimal interfaces needed for static HTML scraping.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any

from .models import ScriptConfig, ScrapingResult, StaticScrapingConfig


class IStaticScraper(ABC):
    """Interface for static HTML scraping."""
    
    @abstractmethod
    async def scrape_static(self, config: StaticScrapingConfig) -> List[Dict[str, Any]]:
        """Scrape data from static HTML websites."""
        pass
    
    @abstractmethod
    def extract_with_selectors(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using CSS selectors."""
        pass


class IScrapingEngine(ABC):
    """Interface for the main scraping orchestrator."""
    
    @abstractmethod
    async def scrape(self, script_config: ScriptConfig) -> ScrapingResult:
        """Execute a complete scraping operation."""
        pass
