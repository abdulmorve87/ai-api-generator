"""
EndpointManager - Orchestrates creation and management of API endpoints.

This module provides the EndpointManager class that coordinates between
the data store and API server for endpoint lifecycle management.
"""

from datetime import datetime
from typing import Optional, List

from ai_layer.parsing_models import ParsedDataResponse
from api_server.models import (
    EndpointData,
    EndpointMetadata,
    EndpointInfo,
    EndpointCreationError,
    EndpointNotFoundError
)
from api_server.data_store import DataStore

# Import console logger for colorful output
try:
    from utils.console_logger import logger as console_logger
    HAS_CONSOLE_LOGGER = True
except ImportError:
    HAS_CONSOLE_LOGGER = False
    console_logger = None


class EndpointManager:
    """Manages creation and lifecycle of API endpoints."""
    
    def __init__(self, data_store: DataStore, base_url: str = "http://127.0.0.1:8080"):
        """
        Initialize with a data store instance.
        
        Args:
            data_store: DataStore instance for persistence
            base_url: Base URL for generating access URLs
        """
        self.data_store = data_store
        self.base_url = base_url.rstrip('/')
    
    def create_endpoint(
        self,
        parsed_response: ParsedDataResponse,
        description: str = None
    ) -> EndpointInfo:
        """
        Create a new API endpoint from parsed data.
        
        Args:
            parsed_response: The parsed data from ScrapedDataParser
            description: Optional description for the endpoint
            
        Returns:
            EndpointInfo with endpoint_id and access_url
            
        Raises:
            EndpointCreationError: If data is invalid or storage fails
        """
        # Log with colorful console if available
        if HAS_CONSOLE_LOGGER and console_logger:
            console_logger.log_endpoint_creation_start(description or "API Endpoint")
        
        print(f"[EndpointManager] create_endpoint() called")
        
        # Validate input
        if parsed_response is None:
            error_msg = "ParsedDataResponse cannot be None"
            if HAS_CONSOLE_LOGGER and console_logger:
                console_logger.error(error_msg)
            print(f"[EndpointManager] ERROR: ParsedDataResponse is None")
            raise EndpointCreationError(error_msg)
        
        if not parsed_response.data:
            error_msg = "ParsedDataResponse contains no data"
            if HAS_CONSOLE_LOGGER and console_logger:
                console_logger.error(error_msg)
            print(f"[EndpointManager] ERROR: ParsedDataResponse.data is empty")
            raise EndpointCreationError(
                error_msg,
                details="The data field is empty or None"
            )
        
        if HAS_CONSOLE_LOGGER and console_logger:
            console_logger.info(f"Validated input - data has {len(str(parsed_response.data))} chars")
        print(f"[EndpointManager] Validated input - data has {len(str(parsed_response.data))} chars")
        
        # Generate unique endpoint ID with keywords from description
        endpoint_id = DataStore.generate_endpoint_id(description)
        if HAS_CONSOLE_LOGGER and console_logger:
            console_logger.key_value("Endpoint ID", endpoint_id)
        print(f"[EndpointManager] Generated endpoint_id: {endpoint_id}")
        
        # Extract metadata from parsed response
        metadata = EndpointMetadata(
            description=description or parsed_response.metadata.model or "API Endpoint",
            source_urls=parsed_response.metadata.data_sources,
            records_count=parsed_response.metadata.records_parsed,
            fields=parsed_response.metadata.fields_extracted,
            parsing_timestamp=parsed_response.metadata.timestamp
        )
        if HAS_CONSOLE_LOGGER and console_logger:
            console_logger.info(f"Created metadata: records={metadata.records_count}, fields={len(metadata.fields)}")
        print(f"[EndpointManager] Created metadata: records={metadata.records_count}, fields={len(metadata.fields)}")
        
        # Create endpoint data
        endpoint_data = EndpointData(
            endpoint_id=endpoint_id,
            json_data=parsed_response.data,
            metadata=metadata,
            created_at=datetime.utcnow()
        )
        
        # Store in database
        if HAS_CONSOLE_LOGGER and console_logger:
            console_logger.info("Storing endpoint in database...")
        print(f"[EndpointManager] Storing endpoint in database...")
        self.data_store.store_endpoint(endpoint_data)
        print(f"[EndpointManager] Endpoint stored successfully")
        
        # Return endpoint info
        access_url = self.get_access_url(endpoint_id)
        
        result = EndpointInfo(
            endpoint_id=endpoint_id,
            access_url=access_url,
            description=metadata.description,
            created_at=endpoint_data.created_at,
            records_count=metadata.records_count
        )
        
        # Log success with colorful console
        if HAS_CONSOLE_LOGGER and console_logger:
            console_logger.log_endpoint_creation_complete(result)
        
        print(f"[EndpointManager] ✅ Endpoint created: {access_url}")
        return result
    
    def get_endpoint(self, endpoint_id: str) -> Optional[EndpointData]:
        """
        Retrieve endpoint data by ID.
        
        Args:
            endpoint_id: The endpoint ID to retrieve
            
        Returns:
            EndpointData if found, None otherwise
        """
        return self.data_store.get_endpoint(endpoint_id)
    
    def list_endpoints(self) -> List[EndpointInfo]:
        """
        List all available endpoints.
        
        Returns:
            List of EndpointInfo objects with access URLs populated
        """
        endpoints = self.data_store.list_endpoints()
        
        # Populate access URLs
        for endpoint in endpoints:
            endpoint.access_url = self.get_access_url(endpoint.endpoint_id)
        
        return endpoints
    
    def delete_endpoint(self, endpoint_id: str) -> bool:
        """
        Delete an endpoint by ID.
        
        Args:
            endpoint_id: The endpoint ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        return self.data_store.delete_endpoint(endpoint_id)
    
    def get_access_url(self, endpoint_id: str) -> str:
        """
        Generate the full access URL for an endpoint.
        
        Args:
            endpoint_id: The endpoint ID
            
        Returns:
            Full HTTP URL for accessing the endpoint
        """
        return f"{self.base_url}/api/data/{endpoint_id}"
    
    def set_base_url(self, base_url: str):
        """
        Update the base URL for access URLs.
        
        Args:
            base_url: New base URL
        """
        self.base_url = base_url.rstrip('/')
