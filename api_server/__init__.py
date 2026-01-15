"""
API Endpoint Server - Exposes parsed JSON data as HTTP endpoints.

This module provides a local API server that serves parsed data from
the Scraped Data Parser via RESTful HTTP endpoints.
"""

from api_server.models import (
    EndpointData,
    EndpointMetadata,
    EndpointInfo,
    EndpointCreationError,
    EndpointNotFoundError,
    ServerStartError
)
from api_server.data_store import DataStore
from api_server.endpoint_manager import EndpointManager
from api_server.server import APIServer

__all__ = [
    # Data Models
    'EndpointData',
    'EndpointMetadata', 
    'EndpointInfo',
    # Exceptions
    'EndpointCreationError',
    'EndpointNotFoundError',
    'ServerStartError',
    # Components
    'DataStore',
    'EndpointManager',
    'APIServer'
]
