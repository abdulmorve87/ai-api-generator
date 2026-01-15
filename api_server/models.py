"""
Data models for the API Endpoint Server.

This module defines dataclasses for endpoint data, metadata, and exceptions
used throughout the API server.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


@dataclass
class EndpointMetadata:
    """Metadata about the endpoint."""
    
    description: str
    source_urls: List[str]
    records_count: int
    fields: List[str]
    parsing_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'description': self.description,
            'source_urls': self.source_urls,
            'records_count': self.records_count,
            'fields': self.fields,
            'parsing_timestamp': self.parsing_timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EndpointMetadata':
        """Create from dictionary."""
        parsing_timestamp = data.get('parsing_timestamp')
        if isinstance(parsing_timestamp, str):
            parsing_timestamp = datetime.fromisoformat(parsing_timestamp)
        elif parsing_timestamp is None:
            parsing_timestamp = datetime.utcnow()
            
        return cls(
            description=data.get('description', ''),
            source_urls=data.get('source_urls', []),
            records_count=data.get('records_count', 0),
            fields=data.get('fields', []),
            parsing_timestamp=parsing_timestamp
        )


@dataclass
class EndpointData:
    """Complete endpoint data including JSON payload."""
    
    endpoint_id: str
    json_data: Dict[str, Any]
    metadata: EndpointMetadata
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'endpoint_id': self.endpoint_id,
            'json_data': self.json_data,
            'metadata': self.metadata.to_dict(),
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EndpointData':
        """Create from dictionary (deserialization)."""
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()
            
        metadata_dict = data.get('metadata', {})
        if isinstance(metadata_dict, dict):
            metadata = EndpointMetadata.from_dict(metadata_dict)
        else:
            metadata = metadata_dict
            
        return cls(
            endpoint_id=data.get('endpoint_id', ''),
            json_data=data.get('json_data', {}),
            metadata=metadata,
            created_at=created_at
        )
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


@dataclass
class EndpointInfo:
    """Summary information about an endpoint (for listing)."""
    
    endpoint_id: str
    access_url: str
    description: str
    created_at: datetime
    records_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'endpoint_id': self.endpoint_id,
            'access_url': self.access_url,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'records_count': self.records_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EndpointInfo':
        """Create from dictionary."""
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.utcnow()
            
        return cls(
            endpoint_id=data.get('endpoint_id', ''),
            access_url=data.get('access_url', ''),
            description=data.get('description', ''),
            created_at=created_at,
            records_count=data.get('records_count', 0)
        )


# Exception classes

class EndpointCreationError(Exception):
    """Raised when endpoint creation fails."""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.details = details


class EndpointNotFoundError(Exception):
    """Raised when endpoint is not found."""
    
    def __init__(self, endpoint_id: str):
        super().__init__(f"Endpoint not found: {endpoint_id}")
        self.endpoint_id = endpoint_id


class ServerStartError(Exception):
    """Raised when server fails to start."""
    
    def __init__(self, message: str, port: int = None):
        super().__init__(message)
        self.port = port
