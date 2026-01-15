"""
Data models for the Scraper Script Generator.

This module defines data classes for representing generated scripts,
validation results, and metadata used throughout the script generation process.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


@dataclass
class ScriptMetadata:
    """Metadata about the script generation process."""
    
    timestamp: datetime
    model: str
    tokens_used: int
    generation_time_ms: int
    target_url: str
    required_fields: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary with ISO format timestamp."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'model': self.model,
            'tokens_used': self.tokens_used,
            'generation_time_ms': self.generation_time_ms,
            'target_url': self.target_url,
            'required_fields': self.required_fields
        }


@dataclass
class ScriptValidationResult:
    """Result of script validation checks."""
    
    is_valid: bool
    syntax_valid: bool
    imports_valid: bool
    no_forbidden_ops: bool
    function_signature_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            'is_valid': self.is_valid,
            'syntax_valid': self.syntax_valid,
            'imports_valid': self.imports_valid,
            'no_forbidden_ops': self.no_forbidden_ops,
            'function_signature_valid': self.function_signature_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def add_error(self, error: str) -> None:
        """Add an error message to the validation result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message to the validation result."""
        self.warnings.append(warning)


@dataclass
class GeneratedScript:
    """Container for AI-generated scraper script."""
    
    script_code: str
    metadata: ScriptMetadata
    validation_result: ScriptValidationResult
    raw_output: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert generated script to dictionary."""
        return {
            'script_code': self.script_code,
            'metadata': self.metadata.to_dict(),
            'validation_result': self.validation_result.to_dict(),
            'raw_output': self.raw_output
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert generated script to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @property
    def is_valid(self) -> bool:
        """Check if the script passed validation."""
        return self.validation_result.is_valid


# Exception Classes

class ScriptValidationError(Exception):
    """Raised when script validation fails."""
    
    def __init__(self, message: str, validation_result: Optional[ScriptValidationResult] = None):
        """
        Initialize script validation error.
        
        Args:
            message: Error message
            validation_result: Optional validation result with details
        """
        super().__init__(message)
        self.validation_result = validation_result


class ScriptExecutionError(Exception):
    """Raised when script execution fails."""
    
    def __init__(self, message: str, script_code: Optional[str] = None, error_details: Optional[Dict[str, Any]] = None):
        """
        Initialize script execution error.
        
        Args:
            message: Error message
            script_code: Optional script code that failed
            error_details: Optional dictionary with error details
        """
        super().__init__(message)
        self.script_code = script_code
        self.error_details = error_details or {}


class ScriptGenerationError(Exception):
    """Raised when script generation fails."""
    
    def __init__(self, message: str, form_input: Optional[Dict[str, Any]] = None):
        """
        Initialize script generation error.
        
        Args:
            message: Error message
            form_input: Optional form input that caused the error
        """
        super().__init__(message)
        self.form_input = form_input
