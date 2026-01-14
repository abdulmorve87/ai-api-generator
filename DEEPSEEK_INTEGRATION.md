# DeepSeek AI + API Layer Integration Guide

This document explains how the DeepSeek AI layer is integrated with the API server to generate and serve dynamic APIs.

## Architecture Overview

```
User Input (Streamlit UI)
    ↓
AI Layer (DeepSeek)
    ↓
API Integration Layer
    ↓
API Server (FastAPI)
    ↓
Database (SQLite)
```

## Components

### 1. AI Layer (`ai_layer/`)

The AI layer handles all DeepSeek API interactions:

- **`deepseek_client.py`**: Low-level DeepSeek API client with retry logic and error handling
- **`config.py`**: Configuration management from environment variables
- **`prompt_builder.py`**: Constructs optimized prompts for DeepSeek
- **`input_processor.py`**: Validates and processes user form inputs
- **`response_generator.py`**: Orchestrates the entire AI generation process
- **`response_validator.py`**: Validates and parses AI-generated JSON
- **`models.py`**: Data models for responses and metadata
- **`exceptions.py`**: Custom exception classes

### 2. Integration Layer (`ai_integration.py`)

Bridges the AI layer and API server:

- Receives AI-generated data
- Formats it for the API server
- Creates/updates API endpoints
- Handles batch operations

### 3. API Server (`api_server.py`)

FastAPI server that:

- Stores generated APIs in database
- Serves API endpoints dynamically
- Provides statistics and metadata
- Handles authentication and rate limiting

### 4. UI Layer (`app.py`)

Streamlit interface that:

- Collects user requirements
- Triggers AI generation
- Displays results
- Shows available APIs

## Data Flow

### Step 1: User Input
User fills out form with:
- Data description (e.g., "cryptocurrency prices")
- Desired fields (optional)
- Update frequency
- Custom structure (optional)

### Step 2: AI Generation
```python
# In data/mock_data.py
from ai_layer import AIResponseGenerator, DeepSeekClient, DeepSeekConfig

# Initialize
config = DeepSeekConfig.from_env()
client = DeepSeekClient(config.api_key)
generator = AIResponseGenerator(client)

# Generate
response = generator.generate_response(form_data)
```

### Step 3: API Creation
```python
# In ai_integration.py
api_payload = {
    "api_name": "cryptocurrency_prices",
    "description": "Real-time crypto data",
    "data": [...],  # AI-generated data
    "schema": {...},  # Inferred schema
    "data_source": "DeepSeek AI",
    "update_frequency": "real-time"
}

result = ai_integration.receive_ai_data(api_payload)
```

### Step 4: API Storage
```python
# In api_server.py
@app.post("/apis")
async def create_api(request: APICreateRequest):
    # Store in database
    api_id = db.create_api(...)
    db.store_api_data(api_id, data)
    return {"endpoint": f"/api/{api_name}"}
```

### Step 5: API Access
```bash
# Access the generated API
curl http://localhost:8000/api/cryptocurrency_prices
```

## Configuration

### Environment Variables

Create a `.env` file:

```bash
# Required
DEEPSEEK_API_KEY=sk-your-api-key-here

# Optional (with defaults)
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.3
DEEPSEEK_MAX_TOKENS=8000
```

### Get DeepSeek API Key

1. Visit https://platform.deepseek.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into `.env` file

## Running the System

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY
```

### 3. Start API Server
```bash
python api_server.py
```

### 4. Start Streamlit UI
```bash
streamlit run app.py
```

### 5. Access the Application
- UI: http://localhost:8501
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Endpoints

### Create API (Internal)
```http
POST /apis
Content-Type: application/json

{
  "name": "cryptocurrency_prices",
  "description": "Real-time crypto data",
  "data": [...],
  "schema": {...},
  "data_source": "DeepSeek AI",
  "update_frequency": "real-time"
}
```

### List APIs
```http
GET /apis
```

### Get API Data
```http
GET /api/{api_name}?limit=100&offset=0&search=bitcoin
```

### Get API Statistics
```http
GET /apis/{api_name}/stats
```

### Get API Schema
```http
GET /api/{api_name}/schema
```

## Error Handling

The integration includes comprehensive error handling:

### Configuration Errors
```python
try:
    config = DeepSeekConfig.from_env()
except ConfigurationError as e:
    # Handle missing API key
    print(f"Configuration error: {e}")
```

### API Errors
```python
try:
    response = generator.generate_response(form_data)
except DeepSeekAuthError:
    # Invalid API key
except DeepSeekRateLimitError:
    # Rate limit exceeded
except DeepSeekConnectionError:
    # Network issues
except GenerationError:
    # Invalid JSON or generation failed
```

## Testing

### Test AI Layer
```bash
python -m pytest ai_layer/test/
```

### Test Integration
```python
from ai_integration import ai_integration

# Test with sample data
result = ai_integration.receive_ai_data({
    "api_name": "test_api",
    "description": "Test API",
    "data": [{"id": 1, "name": "Test"}],
    "schema": {"type": "object", "properties": {...}}
})

print(result)
```

### Manual Test
```bash
# Run the integration test
python ai_integration.py
```

## Performance Optimization

### AI Layer
- Temperature: 0.3 (faster, more consistent)
- Max tokens: 8000 (supports large datasets)
- Retry logic with exponential backoff
- Request timeout: 60 seconds

### API Server
- Database indexing on api_name
- Pagination support (limit/offset)
- Response caching (optional)
- Connection pooling

### Database
- SQLite for development
- Easily upgradable to PostgreSQL for production
- Automatic schema migrations

## Monitoring

### Check API Server Health
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
# API Server logs
tail -f api_server.log

# AI Layer logs
tail -f ai_layer.log
```

### Database Stats
```python
from database import db

# Get all APIs
apis = db.get_all_apis()
print(f"Total APIs: {len(apis)}")

# Get API stats
stats = db.get_api_stats(api_id)
print(f"Total requests: {stats['total_requests']}")
```

## Troubleshooting

### Issue: "DEEPSEEK_API_KEY not set"
**Solution**: Create `.env` file with your API key

### Issue: "API Server not running"
**Solution**: Start API server with `python api_server.py`

### Issue: "Rate limit exceeded"
**Solution**: Wait for rate limit reset or upgrade DeepSeek plan

### Issue: "Invalid JSON response"
**Solution**: Check AI layer logs, may need to adjust prompt

### Issue: "Connection timeout"
**Solution**: Check internet connection, increase timeout in config

## Production Deployment

### Environment Variables
```bash
# Production settings
DEEPSEEK_API_KEY=sk-prod-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Scaling Considerations
- Use PostgreSQL instead of SQLite
- Add Redis for caching
- Deploy API server behind load balancer
- Use async workers for AI generation
- Implement request queuing

## Security

### API Key Management
- Never commit `.env` file
- Use environment variables in production
- Rotate API keys regularly
- Monitor API usage

### API Server Security
- Add authentication middleware
- Implement rate limiting
- Validate all inputs
- Use HTTPS in production
- Enable CORS appropriately

## Next Steps

1. **Add Authentication**: Implement API key authentication
2. **Add Caching**: Use Redis for response caching
3. **Add Monitoring**: Integrate with monitoring tools
4. **Add Tests**: Expand test coverage
5. **Add Documentation**: Auto-generate API docs
6. **Add Webhooks**: Notify on API updates
7. **Add Versioning**: Support API versioning

## Support

For issues or questions:
- Check logs in `api_server.log` and `ai_layer.log`
- Review DeepSeek API documentation
- Check database with `python database.py`
- Test integration with `python ai_integration.py`
