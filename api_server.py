from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import logging
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Generated API Platform",
    description="Dynamic API endpoints generated from AI-processed data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class APICreateRequest(BaseModel):
    name: str
    description: str
    data: List[Dict[str, Any]]
    schema: Dict[str, Any]
    data_source: Optional[str] = None
    update_frequency: Optional[str] = "daily"

class APIResponse(BaseModel):
    status: str
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class APIListResponse(BaseModel):
    status: str
    apis: List[Dict[str, Any]]

class APIStatsResponse(BaseModel):
    status: str
    stats: Dict[str, Any]

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI-Generated API Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "available_endpoints": [
            "/apis - List all APIs",
            "/api/{api_name} - Get API data",
            "/apis/{api_name}/stats - Get API statistics"
        ]
    }

@app.get("/apis", response_model=APIListResponse, tags=["APIs"])
async def list_apis():
    """List all available APIs"""
    start_time = time.time()
    
    try:
        apis = db.get_all_apis()
        response_time = int((time.time() - start_time) * 1000)
        
        return APIListResponse(
            status="success",
            apis=apis
        )
    except Exception as e:
        logger.error(f"Error listing APIs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/apis", tags=["APIs"])
async def create_api(request: APICreateRequest):
    """Create a new API endpoint (called by AI layer)"""
    start_time = time.time()
    
    try:
        # Check if API already exists
        existing_api = db.get_api_by_name(request.name)
        if existing_api:
            # Update existing API data
            api_id = existing_api['id']
            success = db.store_api_data(
                api_id, 
                request.data, 
                request.data_source or "AI Layer"
            )
        else:
            # Create new API
            endpoint = f"/api/{request.name.lower().replace(' ', '_')}"
            api_id = db.create_api(
                name=request.name,
                description=request.description,
                endpoint=endpoint,
                schema=request.schema,
                data_source=request.data_source or "AI Layer",
                update_frequency=request.update_frequency
            )
            
            # Store initial data
            success = db.store_api_data(
                api_id, 
                request.data, 
                request.data_source or "AI Layer"
            )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store API data")
        
        response_time = int((time.time() - start_time) * 1000)
        
        return {
            "status": "success",
            "message": f"API '{request.name}' created/updated successfully",
            "api_id": api_id,
            "endpoint": f"/api/{request.name.lower().replace(' ', '_')}",
            "response_time_ms": response_time
        }
        
    except Exception as e:
        logger.error(f"Error creating API: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/{api_name}", response_model=APIResponse, tags=["Data"])
async def get_api_data(
    api_name: str = Path(..., description="Name of the API"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    search: Optional[str] = Query(None, description="Search term")
):
    """Get data from a specific API endpoint"""
    start_time = time.time()
    
    try:
        # Get API info
        api_info = db.get_api_by_name(api_name)
        if not api_info:
            raise HTTPException(status_code=404, detail=f"API '{api_name}' not found")
        
        api_id = api_info['id']
        
        # Get data
        if search:
            data = db.search_api_data(api_id, search, limit)
            total_count = len(data)  # Approximate for search
        else:
            data = db.get_api_data(api_id, limit, offset)
            total_count = db.get_api_data_count(api_id)
        
        response_time = int((time.time() - start_time) * 1000)
        
        # Log request
        db.log_api_request(api_id, f"/api/{api_name}", "GET", response_time, 200)
        
        return APIResponse(
            status="success",
            data=data,
            metadata={
                "total_count": total_count,
                "returned_count": len(data),
                "limit": limit,
                "offset": offset,
                "search": search,
                "response_time_ms": response_time,
                "api_info": {
                    "name": api_info['name'],
                    "description": api_info['description'],
                    "data_source": api_info['data_source'],
                    "last_updated": api_info['updated_at']
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting API data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/{api_name}/{record_id}", tags=["Data"])
async def get_api_record(
    api_name: str = Path(..., description="Name of the API"),
    record_id: int = Path(..., description="ID of the specific record")
):
    """Get a specific record from an API"""
    start_time = time.time()
    
    try:
        # Get API info
        api_info = db.get_api_by_name(api_name)
        if not api_info:
            raise HTTPException(status_code=404, detail=f"API '{api_name}' not found")
        
        api_id = api_info['id']
        
        # Get all data and find the specific record
        all_data = db.get_api_data(api_id, limit=1000)  # Adjust as needed
        
        if record_id >= len(all_data) or record_id < 0:
            raise HTTPException(status_code=404, detail=f"Record {record_id} not found")
        
        record = all_data[record_id]
        response_time = int((time.time() - start_time) * 1000)
        
        # Log request
        db.log_api_request(api_id, f"/api/{api_name}/{record_id}", "GET", response_time, 200)
        
        return {
            "status": "success",
            "data": record,
            "metadata": {
                "record_id": record_id,
                "response_time_ms": response_time,
                "api_info": {
                    "name": api_info['name'],
                    "description": api_info['description']
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting API record: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/apis/{api_name}/stats", response_model=APIStatsResponse, tags=["Statistics"])
async def get_api_stats(api_name: str = Path(..., description="Name of the API")):
    """Get statistics for a specific API"""
    start_time = time.time()
    
    try:
        # Get API info
        api_info = db.get_api_by_name(api_name)
        if not api_info:
            raise HTTPException(status_code=404, detail=f"API '{api_name}' not found")
        
        api_id = api_info['id']
        stats = db.get_api_stats(api_id)
        
        response_time = int((time.time() - start_time) * 1000)
        
        return APIStatsResponse(
            status="success",
            stats={
                **stats,
                "api_name": api_name,
                "response_time_ms": response_time
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/{api_name}/schema", tags=["Schema"])
async def get_api_schema(api_name: str = Path(..., description="Name of the API")):
    """Get the JSON schema for a specific API"""
    try:
        api_info = db.get_api_by_name(api_name)
        if not api_info:
            raise HTTPException(status_code=404, detail=f"API '{api_name}' not found")
        
        return {
            "status": "success",
            "schema": api_info['schema_json'],
            "api_info": {
                "name": api_info['name'],
                "description": api_info['description'],
                "endpoint": api_info['endpoint']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting API schema: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)