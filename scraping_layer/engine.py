"""
Main Scraping Engine - The central orchestrator for scraping operations (Phase 1: Static Scraping).
"""

import logging
from typing import Optional
from datetime import datetime

from .interfaces import IScrapingEngine, IStaticScraper
from .models import (
    ScriptConfig, ScrapingResult, ScrapingStrategy,
    ScrapingMetadata, PerformanceMetrics, ScrapingError, StaticScrapingConfig
)


class ScrapingEngine(IScrapingEngine):
    """Central orchestrator that coordinates scraping operations."""
    
    def __init__(
        self,
        static_scraper: IStaticScraper,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the scraping engine with static scraper."""
        self.static_scraper = static_scraper
        self.logger = logger or logging.getLogger(__name__)
    
    async def scrape(self, script_config: ScriptConfig) -> ScrapingResult:
        """Execute a complete scraping operation."""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting scrape for {script_config.url}")
            
            # Create static scraping config
            static_config = StaticScrapingConfig(
                url=script_config.url,
                selectors=script_config.selectors,
                timeout=script_config.timeout
            )
            
            # Execute static scraping
            data = await self.static_scraper.scrape_static(static_config)
            
            self.logger.info(f"Extracted {len(data)} items")
            
            # Create result
            end_time = datetime.now()
            result = ScrapingResult(
                success=True,
                data=data,
                metadata=ScrapingMetadata(
                    strategy_used=ScrapingStrategy.STATIC,
                    final_url=script_config.url,
                    response_status=200
                ),
                performance_metrics=PerformanceMetrics(
                    start_time=start_time,
                    end_time=end_time,
                    total_duration=(end_time - start_time).total_seconds(),
                    items_extracted=len(data)
                )
            )
            
            self.logger.info("Scraping completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            
            return ScrapingResult(
                success=False,
                data=[],
                metadata=ScrapingMetadata(
                    strategy_used=ScrapingStrategy.STATIC,
                    final_url=script_config.url
                ),
                errors=[ScrapingError(
                    error_type=type(e).__name__,
                    message=str(e),
                    recoverable=False
                )]
            )
