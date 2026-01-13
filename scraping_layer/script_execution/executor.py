"""
Script Executor - Executes pre-written scraping scripts.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import ScrapingScript, ScriptResult, ScriptMetadata, ScriptStatus
from ..models import ScriptConfig, BrowserRequirements
from ..engine import ScrapingEngine


class ScriptExecutor:
    """Executes pre-written scraping scripts using the scraping engine."""
    
    def __init__(self, scraping_engine: ScrapingEngine):
        """Initialize the script executor."""
        self.scraping_engine = scraping_engine
        self.logger = logging.getLogger(__name__)
        self.execution_history: Dict[str, ScriptResult] = {}
    
    async def execute_script(self, script: ScrapingScript) -> ScriptResult:
        """Execute a scraping script and return results."""
        
        execution_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        self.logger.info(f"Executing script '{script.name}' (ID: {script.script_id})")
        self.logger.info(f"Target URL: {script.url}")
        self.logger.info(f"Strategy: {script.strategy.value}")
        
        try:
            # Convert ScrapingScript to ScriptConfig
            script_config = self._convert_to_script_config(script)
            
            # Execute scraping using the engine
            self.logger.info("Starting scraping operation...")
            scraping_result = await self.scraping_engine.scrape(script_config)
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Create metadata
            metadata = ScriptMetadata(
                script_id=script.script_id,
                execution_id=execution_id,
                strategy_used=script.strategy,
                url_processed=script.url,
                items_found=len(scraping_result.data),
                execution_time=execution_time,
                timestamp=end_time
            )
            
            # Create result
            result = ScriptResult(
                success=scraping_result.success,
                script_id=script.script_id,
                execution_id=execution_id,
                data=scraping_result.data,
                metadata=metadata,
                errors=[error.message for error in scraping_result.errors],
                total_items=len(scraping_result.data),
                execution_time=execution_time
            )
            
            # Validate expected fields if specified
            if script.expected_fields and scraping_result.data:
                missing_fields = self._validate_expected_fields(
                    scraping_result.data, script.expected_fields
                )
                if missing_fields:
                    result.warnings.append(
                        f"Missing expected fields: {', '.join(missing_fields)}"
                    )
            
            # Store in history
            self.execution_history[execution_id] = result
            
            # Log results
            if result.success:
                self.logger.info(f"Script execution completed successfully")
                self.logger.info(f"Items extracted: {result.total_items}")
                self.logger.info(f"Execution time: {result.execution_time:.2f} seconds")
            else:
                self.logger.error(f"Script execution failed: {result.errors}")
            
            return result
            
        except Exception as e:
            # Handle unexpected errors
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Unexpected error during script execution: {e}")
            
            metadata = ScriptMetadata(
                script_id=script.script_id,
                execution_id=execution_id,
                strategy_used=script.strategy,
                url_processed=script.url,
                items_found=0,
                execution_time=execution_time,
                timestamp=end_time
            )
            
            result = ScriptResult(
                success=False,
                script_id=script.script_id,
                execution_id=execution_id,
                data=[],
                metadata=metadata,
                errors=[f"Execution failed: {str(e)}"],
                total_items=0,
                execution_time=execution_time
            )
            
            self.execution_history[execution_id] = result
            return result
    
    def _convert_to_script_config(self, script: ScrapingScript) -> ScriptConfig:
        """Convert ScrapingScript to ScriptConfig for the engine."""
        
        return ScriptConfig(
            url=script.url,
            script_type=script.strategy,
            selectors=script.selectors,
            pagination=script.pagination,
            interactions=script.interactions,
            timeout=script.timeout,
            cache_ttl=0,  # No caching for direct script execution
            browser_requirements=BrowserRequirements(
                headless=True,
                javascript_enabled=script.strategy.value != 'static'
            )
        )
    
    def _validate_expected_fields(
        self, 
        data: List[Dict[str, Any]], 
        expected_fields: List[str]
    ) -> List[str]:
        """Validate that extracted data contains expected fields."""
        
        if not data:
            return expected_fields
        
        # Check first item for expected fields
        first_item = data[0]
        missing_fields = []
        
        for field in expected_fields:
            if field not in first_item:
                missing_fields.append(field)
        
        return missing_fields
    
    def get_execution_history(self, script_id: Optional[str] = None) -> List[ScriptResult]:
        """Get execution history, optionally filtered by script ID."""
        
        if script_id:
            return [
                result for result in self.execution_history.values()
                if result.script_id == script_id
            ]
        
        return list(self.execution_history.values())
    
    def get_execution_result(self, execution_id: str) -> Optional[ScriptResult]:
        """Get a specific execution result by ID."""
        
        return self.execution_history.get(execution_id)
    
    def clear_history(self, older_than_hours: int = 24):
        """Clear execution history older than specified hours."""
        
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
        
        to_remove = []
        for execution_id, result in self.execution_history.items():
            if result.metadata.timestamp.timestamp() < cutoff_time:
                to_remove.append(execution_id)
        
        for execution_id in to_remove:
            del self.execution_history[execution_id]
        
        self.logger.info(f"Cleared {len(to_remove)} old execution records")