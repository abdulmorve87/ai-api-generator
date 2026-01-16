"""
Dynamic Script Executor - Executes AI-generated scraper scripts safely.

This module provides the DynamicScriptExecutor class that executes
AI-generated Python code strings in a sandboxed environment with
timeout enforcement and comprehensive error handling.
"""

import logging
import threading
import traceback
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from .models import (
    ExecutionConfig, ExecutionResult, ExecutionMetadata, SourceResult
)
from .exceptions import (
    ScriptExecutionError, SecurityError, ScriptTimeoutError,
    ScriptSyntaxError, ScriptRuntimeError
)
from .sandbox import ScriptSandbox

# Import console logger for colorful output
try:
    from utils.console_logger import logger as console_logger
    HAS_CONSOLE_LOGGER = True
except ImportError:
    HAS_CONSOLE_LOGGER = False
    console_logger = None


class DynamicScriptExecutor:
    """Executes AI-generated Python scraper scripts dynamically."""
    
    DEFAULT_ENTRY_FUNCTION = 'scrape_data'
    
    def __init__(
        self,
        config: ExecutionConfig = None,
        logger: logging.Logger = None
    ):
        """
        Initialize the Dynamic Script Executor.
        
        Args:
            config: Execution configuration
            logger: Optional logger instance
        """
        self.config = config or ExecutionConfig()
        self.logger = logger or logging.getLogger(__name__)
        self.sandbox = ScriptSandbox(self.config, self.logger)
        self.execution_history: Dict[str, ExecutionResult] = {}
    
    def execute(self, generated_script: 'GeneratedScript') -> ExecutionResult:
        """
        Execute a GeneratedScript from the AI layer.
        
        Args:
            generated_script: GeneratedScript object from AI layer
            
        Returns:
            ExecutionResult with data and metadata
        """
        script_id = str(uuid.uuid4())[:8]
        target_url = generated_script.metadata.target_url
        
        self.logger.info(f"[{script_id}] Executing GeneratedScript")
        self.logger.info(f"[{script_id}] Target URL: {target_url}")
        
        # Log warning if script validation failed
        if not generated_script.is_valid:
            self.logger.warning(
                f"[{script_id}] Script validation indicated invalid, "
                f"attempting execution anyway. Errors: {generated_script.validation_result.errors}"
            )
        
        # Execute the script code
        result = self.execute_code(
            script_code=generated_script.script_code,
            target_url=target_url,
            script_id=script_id
        )
        
        # Merge AI generation metadata
        if generated_script.metadata:
            result.metadata.generation_time_ms = generated_script.metadata.generation_time_ms
            result.metadata.model_used = generated_script.metadata.model
        
        return result
    
    def execute_code(
        self,
        script_code: str,
        target_url: str = None,
        script_id: str = None
    ) -> ExecutionResult:
        """
        Execute raw Python code string.
        
        Args:
            script_code: Python code as string
            target_url: Optional URL to pass to scrape_data function
            script_id: Optional script ID for logging
            
        Returns:
            ExecutionResult with data and metadata
        """
        script_id = script_id or str(uuid.uuid4())[:8]
        start_time = time.time()
        scraped_at = datetime.utcnow()
        
        self.logger.info(f"[{script_id}] Starting script execution")
        if target_url:
            self.logger.info(f"[{script_id}] Target URL: {target_url}")
        
        # Preprocess script to remove if __name__ == '__main__' block
        script_code = self._preprocess_script(script_code)
        
        # Initialize result structure
        metadata = ExecutionMetadata(
            script_id=script_id,
            target_urls=[target_url] if target_url else []
        )
        
        try:
            # Execute with timeout
            result_data = self._execute_with_timeout(
                script_code=script_code,
                target_url=target_url,
                script_id=script_id
            )
            
            # Process the result
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            return self._process_success_result(
                result_data=result_data,
                metadata=metadata,
                execution_time_ms=execution_time_ms,
                scraped_at=scraped_at,
                script_id=script_id,
                target_url=target_url
            )
            
        except ScriptTimeoutError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.error(f"[{script_id}] Execution timed out after {e.timeout_seconds}s")
            
            return ExecutionResult(
                success=False,
                data=e.partial_results,
                metadata=metadata,
                errors=[str(e)],
                execution_time_ms=execution_time_ms,
                scraped_at=scraped_at
            )
            
        except SecurityError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.error(f"[{script_id}] Security violation: {e.forbidden_operation}")
            
            return ExecutionResult(
                success=False,
                data=[],
                metadata=metadata,
                errors=[f"Security error: {str(e)}"],
                execution_time_ms=execution_time_ms,
                scraped_at=scraped_at
            )
            
        except ScriptSyntaxError as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Syntax error at line {e.line_number}: {str(e)}"
            self.logger.error(f"[{script_id}] {error_msg}")
            
            return ExecutionResult(
                success=False,
                data=[],
                metadata=metadata,
                errors=[error_msg],
                execution_time_ms=execution_time_ms,
                scraped_at=scraped_at
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            tb_str = traceback.format_exc()
            error_msg = f"Runtime error ({type(e).__name__}): {str(e)}"
            self.logger.error(f"[{script_id}] {error_msg}")
            self.logger.debug(f"[{script_id}] Traceback:\n{tb_str}")
            
            return ExecutionResult(
                success=False,
                data=[],
                metadata=metadata,
                errors=[error_msg, f"Traceback: {tb_str}"],
                execution_time_ms=execution_time_ms,
                scraped_at=scraped_at
            )
    
    def _execute_with_timeout(
        self,
        script_code: str,
        target_url: str,
        script_id: str
    ) -> Dict[str, Any]:
        """
        Execute script with timeout enforcement.
        
        Args:
            script_code: Python code to execute
            target_url: URL to pass to the script
            script_id: Script ID for logging
            
        Returns:
            Result dictionary from script execution
            
        Raises:
            ScriptTimeoutError: If execution exceeds timeout
        """
        result_container = {'result': None, 'error': None}
        
        def execute_in_thread():
            try:
                result = self.sandbox.execute(
                    script_code=script_code,
                    entry_function=self.DEFAULT_ENTRY_FUNCTION,
                    args=(target_url,) if target_url else ()
                )
                result_container['result'] = result
            except Exception as e:
                result_container['error'] = e
        
        # Use ThreadPoolExecutor for timeout
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(execute_in_thread)
            
            try:
                future.result(timeout=self.config.timeout_seconds)
            except FuturesTimeoutError:
                raise ScriptTimeoutError(
                    timeout_seconds=self.config.timeout_seconds,
                    partial_results=[]
                )
        
        if result_container['error']:
            raise result_container['error']
        
        return result_container['result']
    
    def _preprocess_script(self, script_code: str) -> str:
        """
        Preprocess script to remove problematic sections and fix namespace issues.
        
        This removes the `if __name__ == '__main__':` block which often
        contains `import sys` and other code not needed for direct execution.
        Also fixes datetime import to avoid namespace conflicts in sandbox.
        
        Args:
            script_code: Original Python code
            
        Returns:
            Cleaned Python code safe for sandbox execution
        """
        import re
        
        # Remove the if __name__ == '__main__': block entirely
        # This pattern matches the block and everything indented under it
        patterns = [
            # Match: if __name__ == '__main__':
            r"if\s+__name__\s*==\s*['\"]__main__['\"]\s*:\s*\n(?:[ \t]+.+\n?)*",
            # Match: if __name__ == "__main__":
            r'if\s+__name__\s*==\s*["\']__main__["\']\s*:\s*\n(?:[ \t]+.+\n?)*',
        ]
        
        cleaned_code = script_code
        for pattern in patterns:
            cleaned_code = re.sub(pattern, '', cleaned_code, flags=re.MULTILINE)
        
        # Remove any standalone `import sys` that might be at module level
        cleaned_code = re.sub(r'^import\s+sys\s*$', '', cleaned_code, flags=re.MULTILINE)
        cleaned_code = re.sub(r'^from\s+sys\s+import\s+.+$', '', cleaned_code, flags=re.MULTILINE)
        
        # Fix datetime namespace conflict:
        # Replace "from datetime import datetime" with "import datetime"
        # and "datetime.utcnow()" with "datetime.datetime.utcnow()"
        if 'from datetime import datetime' in cleaned_code:
            cleaned_code = re.sub(
                r'^from\s+datetime\s+import\s+datetime\s*$',
                'import datetime',
                cleaned_code,
                flags=re.MULTILINE
            )
            # Fix all datetime.method() calls to datetime.datetime.method()
            # But avoid double-fixing datetime.datetime.method()
            cleaned_code = re.sub(
                r'\bdatetime\.(?!datetime\.)(\w+)\(',
                r'datetime.datetime.\1(',
                cleaned_code
            )
        
        return cleaned_code.strip()
    
    def _process_success_result(
        self,
        result_data: Any,
        metadata: ExecutionMetadata,
        execution_time_ms: int,
        scraped_at: datetime,
        script_id: str,
        target_url: str
    ) -> ExecutionResult:
        """
        Process successful script execution result.
        
        Args:
            result_data: Raw result from script
            metadata: Execution metadata
            execution_time_ms: Execution time in milliseconds
            scraped_at: Timestamp of scraping
            script_id: Script ID for logging
            target_url: Target URL that was scraped
            
        Returns:
            ExecutionResult with processed data
        """
        # Handle different result formats
        if result_data is None:
            self.logger.warning(f"[{script_id}] Script returned None")
            return ExecutionResult(
                success=False,
                data=[],
                metadata=metadata,
                errors=["Script returned None"],
                execution_time_ms=execution_time_ms,
                scraped_at=scraped_at
            )
        
        # Extract data and metadata from result
        if isinstance(result_data, dict):
            data = result_data.get('data', [])
            result_metadata = result_data.get('metadata', {})
            
            # Update metadata from script result
            metadata.total_count = result_metadata.get('total_count', len(data))
            metadata.filtered_count = result_metadata.get('filtered_count', 0)
            metadata.duplicate_count = result_metadata.get('duplicate_count', 0)
            metadata.scraping_method = result_metadata.get('scraping_method', 'unknown')
            metadata.confidence = result_metadata.get('confidence', 'low')
            metadata.update_frequency = result_metadata.get('update_frequency')
            
            # Check for errors in result
            if result_metadata.get('error'):
                return ExecutionResult(
                    success=False,
                    data=data if isinstance(data, list) else [],
                    metadata=metadata,
                    errors=[result_metadata['error']],
                    execution_time_ms=execution_time_ms,
                    scraped_at=scraped_at
                )
            
            # Create source result
            source_result = SourceResult(
                source_url=target_url or result_metadata.get('source_url', 'unknown'),
                success=True,
                record_count=len(data) if isinstance(data, list) else 0,
                filtered_count=metadata.filtered_count,
                duplicate_count=metadata.duplicate_count,
                execution_time_ms=execution_time_ms,
                scraping_method=metadata.scraping_method,
                confidence=metadata.confidence
            )
            
            self.logger.info(
                f"[{script_id}] Execution completed successfully. "
                f"Records: {source_result.record_count}, "
                f"Time: {execution_time_ms}ms"
            )
            
            return ExecutionResult(
                success=True,
                data=data if isinstance(data, list) else [data],
                metadata=metadata,
                errors=[],
                source_results=[source_result],
                execution_time_ms=execution_time_ms,
                scraped_at=scraped_at
            )
        
        elif isinstance(result_data, list):
            # Script returned a list directly
            metadata.total_count = len(result_data)
            
            source_result = SourceResult(
                source_url=target_url or 'unknown',
                success=True,
                record_count=len(result_data),
                execution_time_ms=execution_time_ms
            )
            
            self.logger.info(
                f"[{script_id}] Execution completed. Records: {len(result_data)}"
            )
            
            return ExecutionResult(
                success=True,
                data=result_data,
                metadata=metadata,
                errors=[],
                source_results=[source_result],
                execution_time_ms=execution_time_ms,
                scraped_at=scraped_at
            )
        
        else:
            # Unexpected result type
            self.logger.warning(
                f"[{script_id}] Unexpected result type: {type(result_data)}"
            )
            return ExecutionResult(
                success=False,
                data=[],
                metadata=metadata,
                errors=[f"Unexpected result type: {type(result_data).__name__}"],
                execution_time_ms=execution_time_ms,
                scraped_at=scraped_at
            )
    
    def execute_multi_source(
        self,
        script_code: str,
        target_urls: List[str],
        script_id: str = None
    ) -> ExecutionResult:
        """
        Execute script against multiple data sources.
        
        Args:
            script_code: Python code as string
            target_urls: List of URLs to scrape
            script_id: Optional script ID for logging
            
        Returns:
            ExecutionResult with aggregated data from all sources
        """
        script_id = script_id or str(uuid.uuid4())[:8]
        start_time = time.time()
        scraped_at = datetime.utcnow()
        
        self.logger.info(f"[{script_id}] Starting multi-source execution")
        self.logger.info(f"[{script_id}] Sources: {len(target_urls)} URLs")
        
        # Initialize aggregated results
        all_data: List[Dict[str, Any]] = []
        all_errors: List[str] = []
        source_results: List[SourceResult] = []
        
        total_filtered = 0
        total_duplicates = 0
        
        # Use colorful progress logging if available
        if HAS_CONSOLE_LOGGER and console_logger:
            with console_logger.scraping_progress(target_urls) as progress:
                for idx, url in enumerate(target_urls):
                    progress.start_url(url, idx)
                    source_start = time.time()
                    
                    try:
                        # Execute script for this URL
                        result_data = self._execute_with_timeout(
                            script_code=script_code,
                            target_url=url,
                            script_id=f"{script_id}-{idx}"
                        )
                        
                        source_time_ms = int((time.time() - source_start) * 1000)
                        
                        # Process source result
                        source_result = self._process_source_result(
                            result_data=result_data,
                            source_url=url,
                            execution_time_ms=source_time_ms
                        )
                        
                        source_results.append(source_result)
                        
                        if source_result.success:
                            # Extract data from result
                            if isinstance(result_data, dict):
                                data = result_data.get('data', [])
                                if isinstance(data, list):
                                    # Add source URL to each record
                                    for record in data:
                                        if isinstance(record, dict):
                                            record['_source_url'] = url
                                    all_data.extend(data)
                                
                                # Accumulate counts
                                metadata = result_data.get('metadata', {})
                                total_filtered += metadata.get('filtered_count', 0)
                                total_duplicates += metadata.get('duplicate_count', 0)
                            
                            progress.complete_url(url, source_result.record_count, success=True)
                        else:
                            all_errors.append(f"Source {url}: {source_result.error}")
                            progress.complete_url(url, 0, success=False)
                            
                    except ScriptTimeoutError as e:
                        source_time_ms = int((time.time() - source_start) * 1000)
                        source_results.append(SourceResult(
                            source_url=url,
                            success=False,
                            record_count=0,
                            error=f"Timeout after {e.timeout_seconds}s",
                            execution_time_ms=source_time_ms
                        ))
                        all_errors.append(f"Source {url}: Timeout")
                        progress.complete_url(url, 0, success=False)
                        
                    except Exception as e:
                        source_time_ms = int((time.time() - source_start) * 1000)
                        source_results.append(SourceResult(
                            source_url=url,
                            success=False,
                            record_count=0,
                            error=str(e),
                            execution_time_ms=source_time_ms
                        ))
                        all_errors.append(f"Source {url}: {str(e)}")
                        progress.complete_url(url, 0, success=False)
                
                progress.finish(len(all_data))
        else:
            # Fallback to original behavior without rich logging
            for idx, url in enumerate(target_urls):
                self.logger.info(f"[{script_id}] Processing source {idx + 1}/{len(target_urls)}: {url}")
                source_start = time.time()
                
                try:
                    # Execute script for this URL
                    result_data = self._execute_with_timeout(
                        script_code=script_code,
                        target_url=url,
                        script_id=f"{script_id}-{idx}"
                    )
                    
                    source_time_ms = int((time.time() - source_start) * 1000)
                    
                    # Process source result
                    source_result = self._process_source_result(
                        result_data=result_data,
                        source_url=url,
                        execution_time_ms=source_time_ms
                    )
                    
                    source_results.append(source_result)
                    
                    if source_result.success:
                        # Extract data from result
                        if isinstance(result_data, dict):
                            data = result_data.get('data', [])
                            if isinstance(data, list):
                                # Add source URL to each record
                                for record in data:
                                    if isinstance(record, dict):
                                        record['_source_url'] = url
                                all_data.extend(data)
                            
                            # Accumulate counts
                            metadata = result_data.get('metadata', {})
                            total_filtered += metadata.get('filtered_count', 0)
                            total_duplicates += metadata.get('duplicate_count', 0)
                        
                        self.logger.info(
                            f"[{script_id}] Source {idx + 1} completed: "
                            f"{source_result.record_count} records"
                        )
                    else:
                        all_errors.append(f"Source {url}: {source_result.error}")
                        self.logger.warning(
                            f"[{script_id}] Source {idx + 1} failed: {source_result.error}"
                        )
                        
                except ScriptTimeoutError as e:
                    source_time_ms = int((time.time() - source_start) * 1000)
                    source_results.append(SourceResult(
                        source_url=url,
                        success=False,
                        record_count=0,
                        error=f"Timeout after {e.timeout_seconds}s",
                        execution_time_ms=source_time_ms
                    ))
                    all_errors.append(f"Source {url}: Timeout")
                    self.logger.warning(f"[{script_id}] Source {idx + 1} timed out")
                    
                except Exception as e:
                    source_time_ms = int((time.time() - source_start) * 1000)
                    source_results.append(SourceResult(
                        source_url=url,
                        success=False,
                        record_count=0,
                        error=str(e),
                        execution_time_ms=source_time_ms
                    ))
                    all_errors.append(f"Source {url}: {str(e)}")
                    self.logger.warning(f"[{script_id}] Source {idx + 1} error: {str(e)}")
        
        # Calculate totals
        execution_time_ms = int((time.time() - start_time) * 1000)
        successful_sources = sum(1 for sr in source_results if sr.success)
        
        # Create metadata
        metadata = ExecutionMetadata(
            script_id=script_id,
            target_urls=target_urls,
            total_count=len(all_data),
            filtered_count=total_filtered,
            duplicate_count=total_duplicates
        )
        
        # Determine overall success
        success = successful_sources > 0
        
        self.logger.info(
            f"[{script_id}] Multi-source execution completed. "
            f"Sources: {successful_sources}/{len(target_urls)} successful, "
            f"Total records: {len(all_data)}, "
            f"Time: {execution_time_ms}ms"
        )
        
        return ExecutionResult(
            success=success,
            data=all_data,
            metadata=metadata,
            errors=all_errors,
            source_results=source_results,
            execution_time_ms=execution_time_ms,
            scraped_at=scraped_at
        )
    
    def _process_source_result(
        self,
        result_data: Any,
        source_url: str,
        execution_time_ms: int
    ) -> SourceResult:
        """
        Process result from a single source.
        
        Args:
            result_data: Raw result from script
            source_url: URL that was scraped
            execution_time_ms: Execution time in milliseconds
            
        Returns:
            SourceResult with processed data
        """
        if result_data is None:
            return SourceResult(
                source_url=source_url,
                success=False,
                record_count=0,
                error="Script returned None",
                execution_time_ms=execution_time_ms
            )
        
        if isinstance(result_data, dict):
            data = result_data.get('data', [])
            metadata = result_data.get('metadata', {})
            
            # Check for error in result
            if metadata.get('error'):
                return SourceResult(
                    source_url=source_url,
                    success=False,
                    record_count=0,
                    error=metadata['error'],
                    execution_time_ms=execution_time_ms
                )
            
            return SourceResult(
                source_url=source_url,
                success=True,
                record_count=len(data) if isinstance(data, list) else 0,
                filtered_count=metadata.get('filtered_count', 0),
                duplicate_count=metadata.get('duplicate_count', 0),
                execution_time_ms=execution_time_ms,
                scraping_method=metadata.get('scraping_method', 'unknown'),
                confidence=metadata.get('confidence', 'low')
            )
        
        elif isinstance(result_data, list):
            return SourceResult(
                source_url=source_url,
                success=True,
                record_count=len(result_data),
                execution_time_ms=execution_time_ms
            )
        
        else:
            return SourceResult(
                source_url=source_url,
                success=False,
                record_count=0,
                error=f"Unexpected result type: {type(result_data).__name__}",
                execution_time_ms=execution_time_ms
            )
    
    def get_execution_history(self) -> List[ExecutionResult]:
        """Get all execution results from history."""
        return list(self.execution_history.values())
