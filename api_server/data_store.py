"""
DataStore - SQLite-based persistence layer for endpoint data.

This module provides the DataStore class that handles all database
operations for storing and retrieving API endpoint data.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from api_server.models import (
    EndpointData,
    EndpointMetadata,
    EndpointInfo,
    EndpointCreationError
)


class DataStore:
    """SQLite-based storage for endpoint data."""
    
    DEFAULT_DB_PATH = "data/endpoints.db"
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection and create tables.
        
        Args:
            db_path: Path to SQLite database file. Defaults to data/endpoints.db
        """
        self.db_path = db_path or self.DEFAULT_DB_PATH
        
        # Ensure directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        self._connection = None
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def _init_database(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS endpoints (
                endpoint_id TEXT PRIMARY KEY,
                json_data TEXT NOT NULL,
                description TEXT,
                source_urls TEXT,
                records_count INTEGER,
                fields TEXT,
                parsing_timestamp TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON endpoints(created_at)
        ''')
        
        conn.commit()
    
    def store_endpoint(self, endpoint_data: EndpointData) -> str:
        """
        Store endpoint data and return the endpoint_id.
        
        Args:
            endpoint_data: The endpoint data to store
            
        Returns:
            The endpoint_id
            
        Raises:
            EndpointCreationError: If storage fails
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO endpoints (
                    endpoint_id, json_data, description, source_urls,
                    records_count, fields, parsing_timestamp, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                endpoint_data.endpoint_id,
                json.dumps(endpoint_data.json_data, default=str),
                endpoint_data.metadata.description,
                json.dumps(endpoint_data.metadata.source_urls),
                endpoint_data.metadata.records_count,
                json.dumps(endpoint_data.metadata.fields),
                endpoint_data.metadata.parsing_timestamp.isoformat(),
                endpoint_data.created_at.isoformat()
            ))
            
            conn.commit()
            return endpoint_data.endpoint_id
            
        except sqlite3.Error as e:
            raise EndpointCreationError(
                f"Failed to store endpoint: {str(e)}",
                details=str(e)
            )
    
    def get_endpoint(self, endpoint_id: str) -> Optional[EndpointData]:
        """
        Retrieve endpoint data by ID.
        
        Args:
            endpoint_id: The endpoint ID to retrieve
            
        Returns:
            EndpointData if found, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM endpoints WHERE endpoint_id = ?',
            (endpoint_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        return self._row_to_endpoint_data(row)
    
    def list_endpoints(self) -> List[EndpointInfo]:
        """
        List all stored endpoints (metadata only).
        
        Returns:
            List of EndpointInfo objects
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT endpoint_id, description, records_count, created_at
            FROM endpoints
            ORDER BY created_at DESC
        ''')
        
        endpoints = []
        for row in cursor.fetchall():
            endpoints.append(EndpointInfo(
                endpoint_id=row['endpoint_id'],
                access_url='',  # Will be set by EndpointManager
                description=row['description'] or '',
                created_at=datetime.fromisoformat(row['created_at']),
                records_count=row['records_count'] or 0
            ))
        
        return endpoints
    
    def delete_endpoint(self, endpoint_id: str) -> bool:
        """
        Delete endpoint by ID.
        
        Args:
            endpoint_id: The endpoint ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM endpoints WHERE endpoint_id = ?',
            (endpoint_id,)
        )
        
        conn.commit()
        return cursor.rowcount > 0
    
    def _row_to_endpoint_data(self, row: sqlite3.Row) -> EndpointData:
        """Convert database row to EndpointData object."""
        metadata = EndpointMetadata(
            description=row['description'] or '',
            source_urls=json.loads(row['source_urls'] or '[]'),
            records_count=row['records_count'] or 0,
            fields=json.loads(row['fields'] or '[]'),
            parsing_timestamp=datetime.fromisoformat(row['parsing_timestamp'])
        )
        
        return EndpointData(
            endpoint_id=row['endpoint_id'],
            json_data=json.loads(row['json_data']),
            metadata=metadata,
            created_at=datetime.fromisoformat(row['created_at'])
        )
    
    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    @staticmethod
    def generate_endpoint_id() -> str:
        """Generate a unique endpoint ID."""
        return str(uuid.uuid4())[:8]
