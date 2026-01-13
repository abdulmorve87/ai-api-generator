import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for API data storage"""
    
    def __init__(self, db_path: str = "api_data.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # APIs table - stores API metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS apis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    endpoint TEXT NOT NULL,
                    schema_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_source TEXT,
                    update_frequency TEXT,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            # API Data table - stores actual data for each API
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_id INTEGER NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_info TEXT,
                    FOREIGN KEY (api_id) REFERENCES apis (id)
                )
            """)
            
            # API Stats table - stores usage statistics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_id INTEGER NOT NULL,
                    endpoint_path TEXT,
                    method TEXT,
                    response_time_ms INTEGER,
                    status_code INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (api_id) REFERENCES apis (id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def create_api(self, name: str, description: str, endpoint: str, 
                   schema: Dict[str, Any], data_source: str = None, 
                   update_frequency: str = "daily") -> int:
        """Create a new API entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO apis (name, description, endpoint, schema_json, 
                                data_source, update_frequency)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, description, endpoint, json.dumps(schema), 
                  data_source, update_frequency))
            conn.commit()
            api_id = cursor.lastrowid
            logger.info(f"Created API: {name} with ID: {api_id}")
            return api_id
    
    def get_api_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get API by name"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM apis WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                api_data = dict(row)
                api_data['schema_json'] = json.loads(api_data['schema_json'])
                return api_data
            return None
    
    def get_all_apis(self) -> List[Dict[str, Any]]:
        """Get all APIs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM apis WHERE status = 'active' ORDER BY created_at DESC")
            rows = cursor.fetchall()
            apis = []
            for row in rows:
                api_data = dict(row)
                api_data['schema_json'] = json.loads(api_data['schema_json'])
                apis.append(api_data)
            return apis
    
    def store_api_data(self, api_id: int, data: List[Dict[str, Any]], 
                       source_info: str = None) -> bool:
        """Store data for an API"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing data for this API
                cursor.execute("DELETE FROM api_data WHERE api_id = ?", (api_id,))
                
                # Insert new data
                for item in data:
                    cursor.execute("""
                        INSERT INTO api_data (api_id, data_json, source_info)
                        VALUES (?, ?, ?)
                    """, (api_id, json.dumps(item), source_info))
                
                # Update API timestamp
                cursor.execute("""
                    UPDATE apis SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
                """, (api_id,))
                
                conn.commit()
                logger.info(f"Stored {len(data)} records for API ID: {api_id}")
                return True
        except Exception as e:
            logger.error(f"Error storing API data: {e}")
            return False
    
    def get_api_data(self, api_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get data for an API with pagination"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data_json, created_at, source_info 
                FROM api_data 
                WHERE api_id = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (api_id, limit, offset))
            rows = cursor.fetchall()
            
            data = []
            for row in rows:
                item = json.loads(row['data_json'])
                item['_metadata'] = {
                    'created_at': row['created_at'],
                    'source_info': row['source_info']
                }
                data.append(item)
            return data
    
    def get_api_data_count(self, api_id: int) -> int:
        """Get total count of data records for an API"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM api_data WHERE api_id = ?", (api_id,))
            return cursor.fetchone()['count']
    
    def log_api_request(self, api_id: int, endpoint_path: str, method: str, 
                       response_time_ms: int, status_code: int):
        """Log API request for statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_stats (api_id, endpoint_path, method, 
                                     response_time_ms, status_code)
                VALUES (?, ?, ?, ?, ?)
            """, (api_id, endpoint_path, method, response_time_ms, status_code))
            conn.commit()
    
    def get_api_stats(self, api_id: int) -> Dict[str, Any]:
        """Get statistics for an API"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_requests,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(CASE WHEN status_code = 200 THEN 1 END) as successful_requests
                FROM api_stats 
                WHERE api_id = ?
            """, (api_id,))
            stats = dict(cursor.fetchone())
            
            # Get data count
            stats['total_records'] = self.get_api_data_count(api_id)
            
            # Get last update time
            cursor.execute("""
                SELECT updated_at FROM apis WHERE id = ?
            """, (api_id,))
            result = cursor.fetchone()
            stats['last_updated'] = result['updated_at'] if result else None
            
            return stats
    
    def search_api_data(self, api_id: int, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search within API data (basic text search)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data_json, created_at, source_info 
                FROM api_data 
                WHERE api_id = ? AND data_json LIKE ?
                ORDER BY created_at DESC 
                LIMIT ?
            """, (api_id, f'%{search_term}%', limit))
            rows = cursor.fetchall()
            
            data = []
            for row in rows:
                item = json.loads(row['data_json'])
                item['_metadata'] = {
                    'created_at': row['created_at'],
                    'source_info': row['source_info']
                }
                data.append(item)
            return data

# Global database instance
db = DatabaseManager()