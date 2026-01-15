"""
APIServer - FastAPI-based HTTP server for serving API endpoints.

This module provides the APIServer class that runs a FastAPI server
to serve stored JSON data via RESTful HTTP endpoints.
"""

import threading
import socket
import time
from typing import Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from api_server.models import (
    EndpointNotFoundError,
    ServerStartError
)
from api_server.data_store import DataStore


# Global reference to data store (set by APIServer)
_data_store: Optional[DataStore] = None
_base_url: str = "http://127.0.0.1:8080"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    yield


# Create FastAPI app
app = FastAPI(
    title="API Endpoint Server",
    description="Serves parsed JSON data as HTTP endpoints",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-endpoint-server"}


@app.get("/api/data/{endpoint_id}")
async def get_endpoint_data(
    endpoint_id: str,
    metadata: bool = Query(False, description="Include parsing metadata in response")
):
    """
    Retrieve JSON data for a specific endpoint.
    
    Args:
        endpoint_id: The unique endpoint identifier
        metadata: If true, include parsing metadata in response
        
    Returns:
        JSON data stored for the endpoint
    """
    if _data_store is None:
        raise HTTPException(status_code=500, detail="Data store not initialized")
    
    endpoint_data = _data_store.get_endpoint(endpoint_id)
    
    if endpoint_data is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "Endpoint not found", "endpoint_id": endpoint_id}
        )
    
    if metadata:
        return JSONResponse(
            content={
                "data": endpoint_data.json_data,
                "metadata": endpoint_data.metadata.to_dict(),
                "endpoint_id": endpoint_id,
                "created_at": endpoint_data.created_at.isoformat()
            },
            media_type="application/json"
        )
    
    return JSONResponse(
        content=endpoint_data.json_data,
        media_type="application/json"
    )


@app.get("/api/endpoints")
async def list_endpoints():
    """
    List all available endpoints.
    
    Returns:
        List of endpoint information including IDs and access URLs
    """
    if _data_store is None:
        raise HTTPException(status_code=500, detail="Data store not initialized")
    
    endpoints = _data_store.list_endpoints()
    
    # Build response with access URLs
    result = []
    for ep in endpoints:
        result.append({
            "endpoint_id": ep.endpoint_id,
            "access_url": f"{_base_url}/api/data/{ep.endpoint_id}",
            "description": ep.description,
            "created_at": ep.created_at.isoformat(),
            "records_count": ep.records_count
        })
    
    return JSONResponse(content={"endpoints": result}, media_type="application/json")


@app.delete("/api/endpoints/{endpoint_id}")
async def delete_endpoint(endpoint_id: str):
    """
    Delete an endpoint.
    
    Args:
        endpoint_id: The unique endpoint identifier to delete
        
    Returns:
        Confirmation message
    """
    if _data_store is None:
        raise HTTPException(status_code=500, detail="Data store not initialized")
    
    deleted = _data_store.delete_endpoint(endpoint_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={"error": "Endpoint not found", "endpoint_id": endpoint_id}
        )
    
    return JSONResponse(
        content={"message": "Endpoint deleted successfully", "endpoint_id": endpoint_id},
        media_type="application/json"
    )


class APIServer:
    """FastAPI server wrapper for serving API endpoints."""
    
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 8080
    MAX_PORT_ATTEMPTS = 10
    
    def __init__(
        self,
        data_store: DataStore,
        host: str = None,
        port: int = None
    ):
        """
        Initialize the API server.
        
        Args:
            data_store: DataStore instance for data access
            host: Host to bind to (default: 127.0.0.1)
            port: Port to bind to (default: 8080)
        """
        global _data_store, _base_url
        
        self.data_store = data_store
        self.host = host or self.DEFAULT_HOST
        self.port = port or self.DEFAULT_PORT
        self._server_thread: Optional[threading.Thread] = None
        self._server: Optional[uvicorn.Server] = None
        self._running = False
        self._started_successfully = False
        
        # Set global data store reference
        _data_store = data_store
        _base_url = f"http://{self.host}:{self.port}"
        
        print(f"[APIServer] Initialized with host={self.host}, port={self.port}")
    
    def start(self) -> str:
        """
        Start the server in a background thread.
        
        Returns:
            The base URL of the running server
            
        Raises:
            ServerStartError: If server fails to start
        """
        print(f"[APIServer] start() called, _running={self._running}")
        
        if self._running and self._started_successfully:
            print(f"[APIServer] Server already running at {self.get_base_url()}")
            return self.get_base_url()
        
        # Find available port
        print(f"[APIServer] Finding available port starting from {self.port}...")
        actual_port = self._find_available_port()
        self.port = actual_port
        print(f"[APIServer] Using port {self.port}")
        
        global _base_url
        _base_url = f"http://{self.host}:{self.port}"
        
        # Configure uvicorn with keep-alive settings
        config = uvicorn.Config(
            app=app,
            host=self.host,
            port=self.port,
            log_level="info",  # Changed to info for more visibility
            access_log=True
        )
        self._server = uvicorn.Server(config)
        
        # Start in background thread - daemon=False to keep it alive
        print(f"[APIServer] Starting server thread...")
        self._server_thread = threading.Thread(
            target=self._run_server,
            daemon=True,  # Daemon so it stops when main app stops
            name="APIServerThread"
        )
        self._server_thread.start()
        print(f"[APIServer] Server thread started (thread id: {self._server_thread.ident})")
        
        # Wait for server to start
        self._wait_for_startup()
        
        self._running = True
        self._started_successfully = True
        
        print(f"🚀 API Server started at {self.get_base_url()}")
        print(f"📚 API docs available at {self.get_base_url()}/docs")
        print(f"[APIServer] Server is now accepting connections")
        
        return self.get_base_url()
    
    def _run_server(self):
        """Run the uvicorn server (called in background thread)."""
        print(f"[APIServer] _run_server() starting in thread {threading.current_thread().name}")
        try:
            self._server.run()
            print(f"[APIServer] _run_server() completed normally")
        except Exception as e:
            print(f"[APIServer] _run_server() ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print(f"[APIServer] _run_server() exiting")
    
    def _find_available_port(self) -> int:
        """Find an available port starting from configured port."""
        for offset in range(self.MAX_PORT_ATTEMPTS):
            port = self.port + offset
            if self._is_port_available(port):
                return port
        
        raise ServerStartError(
            f"Could not find available port after {self.MAX_PORT_ATTEMPTS} attempts",
            port=self.port
        )
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.host, port))
                return True
            except OSError:
                return False
    
    def _wait_for_startup(self, timeout: float = 10.0):
        """Wait for server to be ready."""
        import requests
        
        start_time = time.time()
        health_url = f"http://{self.host}:{self.port}/health"
        
        while time.time() - start_time < timeout:
            # Check if server thread is alive
            if self._server_thread and not self._server_thread.is_alive():
                # Thread died, server failed to start
                time.sleep(0.5)  # Give it a moment
                if not self._server_thread.is_alive():
                    print("⚠️ Server thread died during startup")
                    break
            
            # Try to connect to health endpoint
            try:
                response = requests.get(health_url, timeout=1)
                if response.status_code == 200:
                    print(f"✓ Server health check passed")
                    return
            except requests.exceptions.ConnectionError:
                pass  # Server not ready yet
            except Exception as e:
                print(f"Health check error: {e}")
            
            time.sleep(0.2)
        
        # If we get here, server might still be starting - mark as running anyway
        print("⚠️ Server startup timeout - proceeding anyway")
    
    def stop(self):
        """Stop the server gracefully."""
        print(f"[APIServer] stop() called")
        if self._server and self._running:
            self._server.should_exit = True
            self._running = False
            self._started_successfully = False
            print("🛑 API Server stopped")
        else:
            print(f"[APIServer] Server was not running (running={self._running})")
    
    def is_running(self) -> bool:
        """Check if server is currently running."""
        # Also check if thread is alive
        thread_alive = self._server_thread is not None and self._server_thread.is_alive()
        
        if self._running and not thread_alive:
            print(f"[APIServer] WARNING: _running=True but thread is dead!")
            self._running = False
            self._started_successfully = False
        
        return self._running and thread_alive
    
    def get_base_url(self) -> str:
        """Get the base URL of the server."""
        return f"http://{self.host}:{self.port}"
