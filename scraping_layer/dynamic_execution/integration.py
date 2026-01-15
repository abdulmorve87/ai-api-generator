"""
AI-Scraping Integration - Main orchestrator connecting AI and scraping layers.

This module provides the AIScrapingIntegration class that ties together
script generation, execution, and result formatting.
"""

import logging
from typing import Dict, Any, Optional, List

from .models import ExecutionConfig, ExecutionResult
from .executor import DynamicScriptExecutor
from .formatter import ConsoleOutputFormatter


class AIScrapingIntegration:
    """
    Main integration class connecting AI layer with scraping layer.
    
    This class orchestrates the flow from form input to script generation
    to execution and result display.
    
    Usage:
        integration = AIScrapingIntegration()
        
        # Option 1: Execute a pre-generated script
        result = integration.execute_script(generated_script)
        integration.display_results(result)
        
        # Option 2: Execute raw script code
        result = integration.execute_code(script_code, target_url)
        integration.display_results(result)
        
        # Option 3: Generate and execute (requires AI layer)
        result = integration.generate_and_execute(form_input)
        integration.display_results(result)
    """
    
    def __init__(
        self,
        script_generator: 'ScraperScriptGenerator' = None,
        executor: DynamicScriptExecutor = None,
        formatter: ConsoleOutputFormatter = None,
        config: ExecutionConfig = None,
        logger: logging.Logger = None
    ):
        """
        Initialize the AI-Scraping Integration.
        
        Args:
            script_generator: Optional ScraperScriptGenerator from AI layer
            executor: Optional DynamicScriptExecutor instance
            formatter: Optional ConsoleOutputFormatter instance
            config: Optional ExecutionConfig
            logger: Optional logger instance
        """
        self.config = config or ExecutionConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        self.script_generator = script_generator
        self.executor = executor or DynamicScriptExecutor(self.config, self.logger)
        self.formatter = formatter or ConsoleOutputFormatter()
    
    def generate_and_execute(self, form_input: Dict[str, Any]) -> ExecutionResult:
        """
        Generate a scraper script from form input and execute it.
        
        Args:
            form_input: User form input containing:
                - data_description: str
                - data_source: str (URL)
                - desired_fields: str (optional)
                - response_structure: str (optional)
                - update_frequency: str
                
        Returns:
            ExecutionResult with scraped data
            
        Raises:
            RuntimeError: If script_generator is not configured
        """
        if self.script_generator is None:
            raise RuntimeError(
                "Script generator not configured. "
                "Initialize AIScrapingIntegration with a ScraperScriptGenerator."
            )
        
        self.logger.info("Generating scraper script from form input...")
        
        # Generate script using AI layer
        generated_script = self.script_generator.generate_script(form_input)
        
        self.logger.info(
            f"Script generated in {generated_script.metadata.generation_time_ms}ms"
        )
        
        # Execute the generated script
        return self.execute_script(generated_script)
    
    def execute_script(self, generated_script: 'GeneratedScript') -> ExecutionResult:
        """
        Execute an already-generated script.
        
        Args:
            generated_script: GeneratedScript from AI layer
            
        Returns:
            ExecutionResult with scraped data
        """
        self.logger.info("Executing generated script...")
        
        result = self.executor.execute(generated_script)
        
        self.logger.info(
            f"Execution completed: {len(result.data)} records in {result.execution_time_ms}ms"
        )
        
        return result
    
    def execute_code(
        self,
        script_code: str,
        target_url: str = None,
        target_urls: List[str] = None
    ) -> ExecutionResult:
        """
        Execute raw Python script code.
        
        Args:
            script_code: Python code as string
            target_url: Single URL to scrape (for single-source)
            target_urls: List of URLs to scrape (for multi-source)
            
        Returns:
            ExecutionResult with scraped data
        """
        if target_urls and len(target_urls) > 1:
            self.logger.info(f"Executing script against {len(target_urls)} sources...")
            return self.executor.execute_multi_source(script_code, target_urls)
        else:
            url = target_url or (target_urls[0] if target_urls else None)
            self.logger.info(f"Executing script against single source: {url}")
            return self.executor.execute_code(script_code, url)
    
    def display_results(
        self,
        result: ExecutionResult,
        format_type: str = 'console'
    ) -> None:
        """
        Display execution results.
        
        Args:
            result: ExecutionResult to display
            format_type: Output format ('console' or 'json')
        """
        if format_type == 'json':
            self.formatter.print_json(result)
        else:
            self.formatter.print_result(result)
    
    def get_formatted_result(
        self,
        result: ExecutionResult,
        format_type: str = 'console'
    ) -> str:
        """
        Get formatted result as string.
        
        Args:
            result: ExecutionResult to format
            format_type: Output format ('console' or 'json')
            
        Returns:
            Formatted string
        """
        if format_type == 'json':
            return self.formatter.format_json(result)
        else:
            return self.formatter.format_result(result)
    
    def execute_and_display(
        self,
        script_code: str,
        target_url: str = None,
        target_urls: List[str] = None,
        format_type: str = 'console'
    ) -> ExecutionResult:
        """
        Execute script and display results in one call.
        
        Args:
            script_code: Python code as string
            target_url: Single URL to scrape
            target_urls: List of URLs to scrape
            format_type: Output format ('console' or 'json')
            
        Returns:
            ExecutionResult with scraped data
        """
        result = self.execute_code(script_code, target_url, target_urls)
        self.display_results(result, format_type)
        return result


def create_integration(
    with_ai_layer: bool = False,
    timeout_seconds: int = 60,
    max_records_display: int = 10,
    use_colors: bool = True
) -> AIScrapingIntegration:
    """
    Factory function to create AIScrapingIntegration with common configurations.
    
    Args:
        with_ai_layer: Whether to initialize with AI layer (requires API key)
        timeout_seconds: Script execution timeout
        max_records_display: Max records to show in console output
        use_colors: Whether to use ANSI colors in output
        
    Returns:
        Configured AIScrapingIntegration instance
    """
    config = ExecutionConfig(timeout_seconds=timeout_seconds)
    formatter = ConsoleOutputFormatter(
        max_records_display=max_records_display,
        use_colors=use_colors
    )
    
    script_generator = None
    if with_ai_layer:
        try:
            from ai_layer.scraper_script_generator import ScraperScriptGenerator
            from ai_layer.deepseek_client import DeepSeekClient
            from scraping_layer.config import ScrapingConfig
            
            client = DeepSeekClient()
            scraping_config = ScrapingConfig()
            script_generator = ScraperScriptGenerator(client, scraping_config)
        except ImportError as e:
            logging.warning(f"Could not initialize AI layer: {e}")
        except Exception as e:
            logging.warning(f"AI layer initialization failed: {e}")
    
    return AIScrapingIntegration(
        script_generator=script_generator,
        config=config,
        formatter=formatter
    )
