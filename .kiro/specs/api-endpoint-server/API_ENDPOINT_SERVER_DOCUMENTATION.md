# API Endpoint Server Documentation

## Overview

The API Endpoint Server is a dynamic REST API system that creates and serves API endpoints **while the application is running**. It uses FastAPI and SQLite to store parsed data and mount new endpoints on-the-fly without requiring server restarts.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit App (app.py)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ User Input   │→ │ AI Scraping  │→ │ Data Parser          │  │
│  │ (Form)       │  │ & Execution  │  │ (Structured JSON)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                              ↓                    │
│                                    ┌─────────────────────┐       │
│                                    │ EndpointManager     │       │
│                                    │ .create_endpoint()  │       │
│                                    └─────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    API Server Layer                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    DataStore (SQLite)                     │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  endpoints table:                                   │  │  │
│  │  │  - endpoint_id (PK)                                 │  │  │
│  │  │  - json_data (TEXT)                                 │  │  │
│  │  │  - description, metadata, timestamps                │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             ↕                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         APIServer (FastAPI + Uvicorn)                    │  │
│  │  Running in background thread (daemon)                   │  │
│  │  Port: 8080 (auto-finds available port)                  │  │
│  │                                                           │  │
│  │  Routes:                                                  │  │
│  │  • GET  /health                                          │  │
│  │  • GET  /api/data/{endpoint_id}  ← Dynamic data serving │  │
│  │  • GET  /api/endpoints           ← List all endpoints   │  │
│  │  • DELETE /api/endpoints/{id}    ← Delete endpoint      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                ↓
                    ┌───────────────────────┐
                    │  External Consumers   │
                    │  (HTTP Clients, Apps) │
                    └───────────────────────┘
```

## Core Components

### 1. APIServer (`api_server/server.py`)

The main FastAPI server that runs in a background thread.

**Key Features:**

- Runs on `127.0.0.1:8080` (auto-finds available port if busy)
- Starts in a daemon thread so it stops when the main app stops
- Uses global `_data_store` reference to access data
- Health check endpoint for monitoring

**Initialization Flow:**

```python
# In app.py
@st.cache_resource
def initialize_api_server():
    data_store = DataStore()              # 1. Create SQLite store
    endpoint_manager = EndpointManager()  # 2. Create manager
    api_server = APIServer(data_store)    # 3. Create server
    base_url = api_server.start()         # 4. Start in background thread
    return api_server, endpoint_manager
```

**Server Startup Process:**

```
start() called
    ↓
Find available port (8080, 8081, 8082...)
    ↓
Create Uvicorn config
    ↓
Start background thread (daemon=True)
    ↓
Wait for health check to pass
    ↓
Return base URL (http://127.0.0.1:8080)
```

### 2. DataStore (`api_server/data_store.py`)

SQLite-based persistence layer that stores endpoint data.

**Database Schema:**

```sql
CREATE TABLE endpoints (
    endpoint_id TEXT PRIMARY KEY,      -- e.g., "ipo-data-a3f2"
    json_data TEXT NOT NULL,           -- Serialized JSON payload
    description TEXT,                  -- User-friendly description
    source_urls TEXT,                  -- JSON array of source URLs
    records_count INTEGER,             -- Number of records
    fields TEXT,                       -- JSON array of field names
    parsing_timestamp TEXT,            -- When data was parsed
    created_at TEXT NOT NULL           -- When endpoint was created
);
```

**Key Methods:**

- `store_endpoint(endpoint_data)` - Persist new endpoint
- `get_endpoint(endpoint_id)` - Retrieve endpoint data
- `list_endpoints()` - Get all endpoints (metadata only)
- `delete_endpoint(endpoint_id)` - Remove endpoint
- `generate_endpoint_id(description)` - Create semantic IDs

**Endpoint ID Generation:**

```python
# Input: "Get IPO data from stock market"
# Output: "ipo-stock-market-a3f2"

# Algorithm:
# 1. Extract keywords (remove stop words)
# 2. Take first 2-3 meaningful words
# 3. Add 4-char UUID suffix for uniqueness
```

### 3. EndpointManager (`api_server/endpoint_manager.py`)

Orchestrates endpoint creation and lifecycle management.

**Key Responsibilities:**

- Validates parsed data before storage
- Generates endpoint IDs and access URLs
- Coordinates between DataStore and APIServer
- Provides high-level API for endpoint operations

**Endpoint Creation Flow:**

```
create_endpoint(parsed_response, description)
    ↓
Validate parsed_response.data is not empty
    ↓
Generate semantic endpoint_id
    ↓
Extract metadata (fields, record count, sources)
    ↓
Create EndpointData object
    ↓
Store in DataStore (SQLite)
    ↓
Generate access URL
    ↓
Return EndpointInfo (id, url, metadata)
```

### 4. Data Models (`api_server/models.py`)

**EndpointData:**

- Complete endpoint information including JSON payload
- Used for storage and retrieval

**EndpointMetadata:**

- Parsing metadata (sources, fields, timestamps)
- Attached to each endpoint

**EndpointInfo:**

- Summary information for listing endpoints
- Includes access URL and basic stats

## Dynamic Endpoint Mounting

### How It Works

The system doesn't actually "mount" new routes dynamically. Instead, it uses a **data-driven approach**:

1. **Single Generic Route:** One route handles all endpoints

   ```python
   @app.get("/api/data/{endpoint_id}")
   async def get_endpoint_data(endpoint_id: str):
       # Look up data in database
       endpoint_data = _data_store.get_endpoint(endpoint_id)
       return endpoint_data.json_data
   ```

2. **Database Lookup:** Each request queries SQLite for the endpoint_id

   ```
   Request: GET /api/data/ipo-stock-market-a3f2
       ↓
   Extract endpoint_id = "ipo-stock-market-a3f2"
       ↓
   Query: SELECT * FROM endpoints WHERE endpoint_id = ?
       ↓
   Return json_data if found, 404 if not
   ```

3. **No Server Restart Required:** New endpoints are just new database rows

### Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ Client Request: GET /api/data/ipo-stock-market-a3f2             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ FastAPI Route Handler: get_endpoint_data(endpoint_id)           │
│  • Extract endpoint_id from URL path                            │
│  • Check if _data_store is initialized                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ DataStore.get_endpoint(endpoint_id)                             │
│  • Execute SQL: SELECT * FROM endpoints WHERE endpoint_id = ?   │
│  • Deserialize json_data from TEXT to dict                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────────────┐
                    │ Found?        │
                    └───────────────┘
                     ↙            ↘
              YES                    NO
               ↓                      ↓
    ┌──────────────────┐    ┌──────────────────┐
    │ Return JSON data │    │ Return 404 error │
    │ Status: 200      │    │ Status: 404      │
    └──────────────────┘    └──────────────────┘
```

### Complete Lifecycle Example

```
User Action: Submit form with "Get IPO data"
    ↓
AI generates scraper script
    ↓
Script executes and scrapes data
    ↓
AI parses scraped data into structured JSON
    ↓
User clicks "Create Endpoint"
    ↓
┌─────────────────────────────────────────────────────────────┐
│ EndpointManager.create_endpoint()                           │
│  1. Validate parsed data                                    │
│  2. Generate ID: "ipo-data-a3f2"                           │
│  3. Create EndpointData object                              │
│  4. DataStore.store_endpoint()                              │
│     → INSERT INTO endpoints VALUES (...)                    │
│  5. Return EndpointInfo with URL                            │
│     → http://127.0.0.1:8080/api/data/ipo-data-a3f2         │
└─────────────────────────────────────────────────────────────┘
    ↓
Endpoint is immediately accessible!
    ↓
External client: GET http://127.0.0.1:8080/api/data/ipo-data-a3f2
    ↓
FastAPI route handler queries database
    ↓
Returns JSON data (200 OK)
```

## Threading Model

### Why Background Thread?

The APIServer runs in a separate thread to avoid blocking the Streamlit app:

```python
self._server_thread = threading.Thread(
    target=self._run_server,
    daemon=True,  # Dies when main app exits
    name="APIServerThread"
)
self._server_thread.start()
```

**Benefits:**

- Streamlit UI remains responsive
- Server runs continuously in background
- Automatic cleanup when app stops

**Thread Safety:**

- SQLite connection uses `check_same_thread=False`
- FastAPI/Uvicorn handles concurrent requests
- Global `_data_store` reference is set once at startup

### Server Lifecycle

```
App Startup
    ↓
initialize_api_server() called (cached by Streamlit)
    ↓
APIServer.start()
    ↓
Background thread starts
    ↓
Uvicorn server runs in thread
    ↓
Health check passes
    ↓
Server ready to accept requests
    ↓
... (server runs continuously) ...
    ↓
App shutdown
    ↓
Daemon thread automatically terminates
```

## API Endpoints

### 1. Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "api-endpoint-server"
}
```

### 2. Get Endpoint Data

```http
GET /api/data/{endpoint_id}?metadata=false
```

**Parameters:**

- `endpoint_id` (path): Unique endpoint identifier
- `metadata` (query): Include parsing metadata (default: false)

**Response (metadata=false):**

```json
{
  "data": [
    { "company": "Acme Corp", "ipo_date": "2025-01-15", "price": 25.5 },
    { "company": "TechStart", "ipo_date": "2025-01-20", "price": 18.0 }
  ]
}
```

**Response (metadata=true):**

```json
{
  "data": [...],
  "metadata": {
    "description": "IPO data from stock market",
    "source_urls": ["https://example.com/ipos"],
    "records_count": 2,
    "fields": ["company", "ipo_date", "price"],
    "parsing_timestamp": "2025-01-15T10:30:00"
  },
  "endpoint_id": "ipo-data-a3f2",
  "created_at": "2025-01-15T10:30:05"
}
```

### 3. List All Endpoints

```http
GET /api/endpoints
```

**Response:**

```json
{
  "endpoints": [
    {
      "endpoint_id": "ipo-data-a3f2",
      "access_url": "http://127.0.0.1:8080/api/data/ipo-data-a3f2",
      "description": "IPO data from stock market",
      "created_at": "2025-01-15T10:30:05",
      "records_count": 2
    }
  ]
}
```

### 4. Delete Endpoint

```http
DELETE /api/endpoints/{endpoint_id}
```

**Response:**

```json
{
  "message": "Endpoint deleted successfully",
  "endpoint_id": "ipo-data-a3f2"
}
```

## Integration with Main App

### In app.py

```python
# 1. Initialize server (runs once, cached by Streamlit)
api_server, endpoint_manager, error = initialize_api_server()

# 2. After data parsing completes
if parsed_response:
    st.session_state['last_parsed_response'] = parsed_response
    st.session_state['show_create_endpoint'] = True

# 3. User clicks "Create Endpoint" button
if create_clicked:
    endpoint_info = endpoint_manager.create_endpoint(
        parsed_response=parsed_response,
        description=endpoint_desc
    )
    st.success(f"Endpoint created: {endpoint_info.access_url}")

# 4. Endpoint is immediately accessible via HTTP
```

### Sidebar Status Display

The sidebar shows real-time server status:

```python
with st.sidebar:
    if api_server.is_running():
        st.success(f"✅ Running at {api_server.get_base_url()}")

        # List existing endpoints
        endpoints = endpoint_manager.list_endpoints()
        for ep in endpoints:
            st.write(f"🔗 {ep.description}")
            st.code(ep.access_url)
```

## Error Handling

### Server Startup Errors

```python
try:
    api_server.start()
except ServerStartError as e:
    # Port unavailable after 10 attempts
    st.error(f"Failed to start server: {e}")
```

### Endpoint Creation Errors

```python
try:
    endpoint_manager.create_endpoint(parsed_response)
except EndpointCreationError as e:
    # Invalid data or storage failure
    st.error(f"Failed to create endpoint: {e}")
```

### Request Errors

```python
@app.get("/api/data/{endpoint_id}")
async def get_endpoint_data(endpoint_id: str):
    endpoint_data = _data_store.get_endpoint(endpoint_id)

    if endpoint_data is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "Endpoint not found", "endpoint_id": endpoint_id}
        )

    return endpoint_data.json_data
```

## Performance Considerations

### Database Performance

- **Indexed Queries:** Primary key lookups are O(log n)
- **Connection Pooling:** Single persistent connection
- **JSON Storage:** TEXT column with JSON serialization

### Scalability

Current limitations:

- Single SQLite database (not suitable for high concurrency)
- In-memory server state (lost on restart)
- No authentication or rate limiting

For production:

- Use PostgreSQL or MongoDB
- Add Redis for caching
- Implement JWT authentication
- Add rate limiting middleware

## Security Considerations

### Current Implementation

⚠️ **Development Only** - Not production-ready:

- No authentication
- No rate limiting
- No input validation on endpoint_id
- No CORS configuration
- Binds to localhost only (127.0.0.1)

### Production Recommendations

1. **Authentication:**

   ```python
   from fastapi.security import HTTPBearer

   security = HTTPBearer()

   @app.get("/api/data/{endpoint_id}")
   async def get_endpoint_data(
       endpoint_id: str,
       credentials: HTTPAuthorizationCredentials = Depends(security)
   ):
       # Validate JWT token
       ...
   ```

2. **Rate Limiting:**

   ```python
   from slowapi import Limiter

   limiter = Limiter(key_func=get_remote_address)

   @app.get("/api/data/{endpoint_id}")
   @limiter.limit("100/minute")
   async def get_endpoint_data(...):
       ...
   ```

3. **Input Validation:**

   ```python
   from pydantic import BaseModel, validator

   class EndpointRequest(BaseModel):
       endpoint_id: str

       @validator('endpoint_id')
       def validate_id(cls, v):
           if not re.match(r'^[a-z0-9-]+$', v):
               raise ValueError('Invalid endpoint ID')
           return v
   ```

## Debugging

### Enable Verbose Logging

The code includes extensive print statements for debugging:

```python
print(f"[APIServer] start() called, _running={self._running}")
print(f"[DataStore] store_endpoint() called for id={endpoint_data.endpoint_id}")
print(f"[EndpointManager] ✅ Endpoint created: {access_url}")
```

### Check Server Status

```python
# In Python console or Streamlit
if api_server.is_running():
    print(f"Server running at {api_server.get_base_url()}")
else:
    print("Server not running")
```

### Test Endpoints

```bash
# Health check
curl http://127.0.0.1:8080/health

# List endpoints
curl http://127.0.0.1:8080/api/endpoints

# Get specific endpoint
curl http://127.0.0.1:8080/api/data/ipo-data-a3f2

# With metadata
curl "http://127.0.0.1:8080/api/data/ipo-data-a3f2?metadata=true"
```

## Summary

The API Endpoint Server achieves dynamic endpoint creation through:

1. **Data-Driven Architecture:** Single generic route + database lookup
2. **Background Threading:** Non-blocking server in daemon thread
3. **SQLite Persistence:** Lightweight storage for endpoint data
4. **Semantic IDs:** Human-readable endpoint identifiers
5. **Immediate Availability:** No server restart required

This design allows the Streamlit app to create and serve new API endpoints on-the-fly, making scraped data instantly accessible via REST API.
