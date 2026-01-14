"""
Data models for the AI Layer.

This module defines data classes for representing generated responses,
metadata, and other data structures used throughout the AI Response Generator.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any
import json


@dataclass
class ResponseMetadata:
    """Metadata about the AI generation process."""
    
    timestamp: datetime
    model: str
    tokens_used: int
    generation_time_ms: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary with ISO format timestamp."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'model': self.model,
            'tokens_used': self.tokens_used,
            'generation_time_ms': self.generation_time_ms
        }


@dataclass
class GeneratedResponse:
    """Container for AI-generated API response."""
    
    data: Dict[str, Any]
    metadata: ResponseMetadata
    raw_output: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'data': self.data,
            'metadata': self.metadata.to_dict(),
            'raw_output': self.raw_output
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert response to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
