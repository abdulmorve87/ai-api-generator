"""
Data models for the Dynamic Execution module.

This module defines data classes for execution configuration, results,
and metadata used throughout the dynamic script execution process.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


@dataclass
class ExecutionConfig:
    """Configuration for script execution."""
    
    timeout_seconds: int = 60
    max_memory_mb: int = 256
    allowed_imports: List[str] = None
    
    def __post_init__(self):
        if self.allowed_imports is None:
            self.allowed_imports = [
                'requests', 'bs4', 'BeautifulSoup', 're', 'json',
                'datetime', 'typing', 'urllib', 'html', 'collections'
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'timeout_seconds': self.timeout_seconds,
            'max_memory_mb': self.max_memory_mb,
            'allowed_imports': self.allowed_imports
        }


@dataclass
class SourceResult:
    """Result from scraping a single data source."""
    
    source_url: str
    success: bool
    record_count: int
    filtered_count: int = 0
    duplicate_count: int = 0
    error: Optional[str] = None
    execution_time_ms: int = 0
    scraping_method: str = 'unknown'
    confidence: str = 'low'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert source result to dictionary."""
        return {
            'source_url': self.source_url,
            'success': self.success,
            'record_count': self.record_count,
            'filtered_count': self.filtered_count,
            'duplicate_count': self.duplicate_count,
            'error': self.error,
            'execution_time_ms': self.execution_time_ms,
            'scraping_method': self.scraping_method,
            'confidence': self.confidence
        }


@dataclass
class ExecutionMetadata:
    """Metadata about the execution."""
    
    # Counts
    total_count: int = 0
    filtered_count: int = 0
    duplicate_count: int = 0
    
    # Script info
    script_id: Optional[str] = None
    target_urls: List[str] = field(default_factory=list)
    
    # AI generation info (if available)
    generation_time_ms: Optional[int] = None
    model_used: Optional[str] = None
    
    # Scraping method detected
    scraping_method: str = 'unknown'
    confidence: str = 'low'
    
    # Update frequency
    update_frequency: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'total_count': self.total_count,
            'filtered_count': self.filtered_count,
            'duplicate_count': self.duplicate_count,
            'script_id': self.script_id,
            'target_urls': self.target_urls,
            'generation_time_ms': self.generation_time_ms,
            'model_used': self.model_used,
            'scraping_method': self.scraping_method,
            'confidence': self.confidence,
            'update_frequency': self.update_frequency
        }


@dataclass
class ExecutionResult:
    """Complete result of script execution."""
    
    # Execution status
    success: bool
    
    # Extracted data
    data: List[Dict[str, Any]]
    
    # Execution metadata
    metadata: ExecutionMetadata
    
    # Errors encountered
    errors: List[str] = field(default_factory=list)
    
    # Per-source breakdown (for multi-source scripts)
    source_results: List[SourceResult] = field(default_factory=list)
    
    # Timing
    execution_time_ms: int = 0
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution result to dictionary."""
        return {
            'success': self.success,
            'data': self.data,
            'metadata': self.metadata.to_dict(),
            'errors': self.errors,
            'source_results': [sr.to_dict() for sr in self.source_results],
            'execution_time_ms': self.execution_time_ms,
            'scraped_at': self.scraped_at.isoformat()
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert execution result to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @property
    def total_records(self) -> int:
        """Get total number of records extracted."""
        return len(self.data)
    
    @property
    def has_errors(self) -> bool:
        """Check if execution had any errors."""
        return len(self.errors) > 0
    
    @property
    def partial_success(self) -> bool:
        """Check if execution had partial success (some sources succeeded)."""
        if not self.source_results:
            return False
        successes = sum(1 for sr in self.source_results if sr.success)
        return 0 < successes < len(self.source_results)
    
    def validate(self) -> tuple:
        """
        Validate the execution result structure.
        
        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        errors = []
        
        # Check required fields
        if self.data is None:
            errors.append("'data' field is None, should be a list")
        elif not isinstance(self.data, list):
            errors.append(f"'data' field should be a list, got {type(self.data).__name__}")
        
        if self.metadata is None:
            errors.append("'metadata' field is None")
        else:
            # Validate metadata
            meta_errors = self._validate_metadata()
            errors.extend(meta_errors)
        
        if self.errors is None:
            errors.append("'errors' field is None, should be a list")
        elif not isinstance(self.errors, list):
            errors.append(f"'errors' field should be a list, got {type(self.errors).__name__}")
        
        if self.execution_time_ms is None:
            errors.append("'execution_time_ms' field is None")
        elif self.execution_time_ms < 0:
            errors.append(f"'execution_time_ms' should be non-negative, got {self.execution_time_ms}")
        
        if self.scraped_at is None:
            errors.append("'scraped_at' field is None")
        
        # Validate source_results if present
        if self.source_results:
            for idx, sr in enumerate(self.source_results):
                sr_errors = self._validate_source_result(sr, idx)
                errors.extend(sr_errors)
        
        return (len(errors) == 0, errors)
    
    def _validate_metadata(self) -> List[str]:
        """Validate metadata structure."""
        errors = []
        
        if self.metadata.total_count is None:
            errors.append("metadata.total_count is None")
        elif self.metadata.total_count < 0:
            errors.append(f"metadata.total_count should be non-negative, got {self.metadata.total_count}")
        
        if self.metadata.filtered_count is None:
            errors.append("metadata.filtered_count is None")
        elif self.metadata.filtered_count < 0:
            errors.append(f"metadata.filtered_count should be non-negative")
        
        if self.metadata.duplicate_count is None:
            errors.append("metadata.duplicate_count is None")
        elif self.metadata.duplicate_count < 0:
            errors.append(f"metadata.duplicate_count should be non-negative")
        
        return errors
    
    def _validate_source_result(self, sr: 'SourceResult', idx: int) -> List[str]:
        """Validate a single source result."""
        errors = []
        prefix = f"source_results[{idx}]"
        
        if sr.source_url is None:
            errors.append(f"{prefix}.source_url is None")
        
        if sr.record_count is None:
            errors.append(f"{prefix}.record_count is None")
        elif sr.record_count < 0:
            errors.append(f"{prefix}.record_count should be non-negative")
        
        if sr.execution_time_ms is None:
            errors.append(f"{prefix}.execution_time_ms is None")
        elif sr.execution_time_ms < 0:
            errors.append(f"{prefix}.execution_time_ms should be non-negative")
        
        return errors
