"""
Script Executor - Executes pre-written scraping scripts (Phase 1: Static Scraping).
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import ScrapingScript, ScriptResult, ScriptMetadata
from ..models import ScriptConfig
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
        
        try:
            # Convert ScrapingScript to ScriptConfig
            script_config = ScriptConfig(
                url=script.url,
                selectors=script.selectors,
                timeout=script.timeout
            )
            
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