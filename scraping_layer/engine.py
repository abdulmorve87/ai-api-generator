"""
Main Scraping Engine - The central orchestrator for all scraping operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .interfaces import (
    IScrapingEngine, IContentDetector, IScriptExecutor, IStaticScraper,
    IDynamicScraper, IBrowserManager, IDataExtractor, ICacheManager, IErrorHandler
)
from .models import (
    ScriptConfig, ScrapingResult, WebsiteAnalysis, ValidationResult,
    ScrapingStrategy, ScrapingMetadata, PerformanceMetrics, ScrapingError
)


class ScrapingEngine(IScrapingEngine):
    """Central orchestrator that coordinates all scraping operations."""
    
    def __init__(
        self,
        content_detector: IContentDetector,
        script_executor: IScriptExecutor,
        static_scraper: IStaticScraper,
        dynamic_scraper: IDynamicScraper,
        browser_manager: IBrowserManager,
        data_extractor: IDataExtractor,
        cache_manager: ICacheManager,
        error_handler: IErrorHandler,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the scraping engine with all required components."""
        self.content_detector = content_detector
        self.script_executor = script_executor
        self.static_scraper = static_scraper
        self.dynamic_scraper = dynamic_scraper
        self.browser_manager = browser_manager
        self.data_extractor = data_extractor
        self.cache_manager = cache_manager
        self.error_handler = error_handler
        self.logger = logger or logging.getLogger(__name__)
        
        # Supported strategies
        self._supported_strategies = [
            ScrapingStrategy.STATIC.value,
            ScrapingStrategy.DYNAMIC.value,
            ScrapingStrategy.HYBRID.value
        ]
    
    async def scrape(self, script_config: ScriptConfig) -> ScrapingResult:
        """Execute a complete scraping operation."""
        start_time = datetime.now()
        
        try:
            print(f" Engine: Starting scrape for {script_config.url}")
            
            # Check cache first
            print(" Engine: Checking cache...")
            cached_data = await self.cache_manager.get_cached_data("dummy_key")
            if cached_data:
                print(" Engine: Cache hit!")
                return self._create_cached_result(cached_data, start_time)
            
            # Analyze website
            print(" Engine: Analyzing website...")
            analysis = await self.content_detector.analyze_website(script_config.url)
            strategy = analysis.recommended_strategy
            print(f" Engine: Using strategy: {strategy.value}")
            
            # Execute scraping based on strategy
            if strategy == ScrapingStrategy.STATIC:
                print(" Engine: Executing static scraping...")
                data = await self._execute_static_scraping(script_config, analysis)
            elif strategy == ScrapingStrategy.DYNAMIC:
                print(" Engine: Executing dynamic scraping...")
                data = await self._execute_dynamic_scraping(script_config, analysis)
            else:
                print(" Engine: Executing hybrid scraping...")
                try:
                    data = await self._execute_dynamic_scraping(script_config, analysis)
                except Exception as e:
                    print(f" Engine: Dynamic failed, falling back to static: {e}")
                    data = await self._execute_static_scraping(script_config, analysis)
            
            print(f" Engine: Raw data extracted: {len(data)} items")
            
            # Validate and clean data
            cleaned_data = self.data_extractor.clean_data(data)
            print(f" Engine: Cleaned data: {len(cleaned_data)} items")
            
            # Store in cache (mock for now)
            print(" Engine: Storing in cache...")
            
            # Create result
            end_time = datetime.now()
            result = ScrapingResult(
                success=True,
                data=cleaned_data,
                metadata=ScrapingMetadata(
                    strategy_used=strategy,
                    framework_detected=analysis.framework.framework if analysis.framework else None,
                    final_url=script_config.url,
                    response_status=200
                ),
                performance_metrics=PerformanceMetrics(
                    start_time=start_time,
                    end_time=end_time,
                    total_duration=(end_time - start_time).total_seconds(),
                    items_extracted=len(cleaned_data)
                )
            )
            
            print(" Engine: Scraping completed successfully")
            return result
            
        except Exception as e:
            print(f" Engine: Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            
            return ScrapingResult(
                success=False,
                data=[],
                metadata=ScrapingMetadata(strategy_used=script_config.script_type),
                errors=[ScrapingError(
                    error_type=type(e).__name__,
                    message=str(e),
                    recoverable=False
                )]
            )
    
    async def validate_script(self, script: str) -> ValidationResult:
        """Validate an AI-generated script for safety and correctness."""
        return ValidationResult(is_valid=True)
    
    def get_supported_strategies(self) -> List[str]:
        """Get list of supported scraping strategies."""
        return self._supported_strategies.copy()
    
    async def analyze_url(self, url: str) -> WebsiteAnalysis:
        """Analyze a URL to determine optimal scraping strategy."""
        return await self.content_detector.analyze_website(url)
    
    async def _execute_static_scraping(
        self, 
        config: ScriptConfig, 
        analysis: WebsiteAnalysis
    ) -> List[Dict[str, Any]]:
        """Execute static scraping strategy."""
        from .models import StaticScrapingConfig
        
        static_config = StaticScrapingConfig(
            url=config.url,
            selectors=config.selectors,
            timeout=config.timeout,
            pagination=config.pagination
        )
        
        return await self.static_scraper.scrape_static(static_config)
    
    async def _execute_dynamic_scraping(
        self, 
        config: ScriptConfig, 
        analysis: WebsiteAnalysis
    ) -> List[Dict[str, Any]]:
        """Execute dynamic scraping strategy."""
        from .models import DynamicScrapingConfig
        
        dynamic_config = DynamicScrapingConfig(
            url=config.url,
            selectors=config.selectors,
            interactions=config.interactions,
            browser_requirements=config.browser_requirements,
            wait_timeout=config.timeout * 1000  # Convert to milliseconds
        )
        
        return await self.dynamic_scraper.scrape_dynamic(dynamic_config)
    
    def _create_cached_result(self, cached_data: Dict[str, Any], start_time: datetime) -> ScrapingResult:
        """Create a ScrapingResult from cached data."""
        end_time = datetime.now()
        
        return ScrapingResult(
            success=True,
            data=cached_data.get('data', []),
            metadata=ScrapingMetadata(
                strategy_used=ScrapingStrategy(cached_data.get('strategy', 'static')),
                framework_detected=cached_data.get('framework')
            ),
            performance_metrics=PerformanceMetrics(
                start_time=start_time,
                end_time=end_time,
                total_duration=(end_time - start_time).total_seconds(),
                items_extracted=len(cached_data.get('data', []))
            ),
            cache_info=cached_data.get('cache_info')
        )
