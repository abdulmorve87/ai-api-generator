# DeepSeek AI + API Layer Integration

Complete integration of DeepSeek AI with the API server for dynamic API generation.

## 🎯 What This Does

This system allows you to:
1. **Describe** what data you want (e.g., "cryptocurrency prices")
2. **Generate** realistic data using DeepSeek AI
3. **Store** the data in a database
4. **Serve** it as a REST API endpoint
5. **Access** the API with full documentation

## 🏗️ Architecture

```
┌─────────────────┐
│  Streamlit UI   │  ← User describes data requirements
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Layer      │  ← DeepSeek generates JSON data
│  (DeepSeek)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Integration    │  ← Formats and validates data
│     Layer       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Server     │  ← Stores and serves data
│   (FastAPI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │  ← Persistent storage
│   (SQLite)      │
└─────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure DeepSeek API

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# Get your key from: https://platform.deepseek.com/
```

Your `.env` should look like:
```bash
DEEPSEEK_API_KEY=sk-your-actual-api-key-here
```

### 3. Start Everything

**Option A: Automatic (Recommended)**
```bash
python start_all.py
```

**Option B: Manual**
```bash
# Terminal 1: Start API Server
python api_server.py

# Terminal 2: Start Streamlit UI
streamlit run app.py
```

### 4. Access the Application

- **UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🧪 Test the Integration

Run the comprehensive test suite:

```bash
python test_integration.py
```

This will test:
- ✅ Configuration
- ✅ API Server connectivity
- ✅ AI generation with DeepSeek
- ✅ Data integration
- ✅ API endpoint access

## 📝 Usage Example

### Via UI (Streamlit)

1. Open http://localhost:8501
2. Fill in the form:
   - **Data Description**: "Top 10 programming languages with popularity metrics"
   - **Desired Fields**: name, rank, popularity_score, use_cases
   - **Update Frequency**: monthly
3. Click "Generate API"
4. Wait 10-30 seconds for AI generation
5. View your generated API endpoint and data

### Via Code

```python
from ai_layer import DeepSeekConfig, DeepSeekClient, AIResponseGenerator

# Initialize
config = DeepSeekConfig.from_env()
client = DeepSeekClient(config.api_key)
generator = AIResponseGenerator(client)

# Generate data
form_data = {
    "data_description": "cryptocurrency prices",
    "desired_fields": "symbol\nname\nprice\nchange_24h",
    "update_frequency": "real-time"
}

response = generator.generate_response(form_data)
print(response.data)
```

### Via API Integration

```python
from ai_integration import ai_integration

# Prepare data
api_payload = {
    "api_name": "crypto_prices",
    "description": "Real-time cryptocurrency prices",
    "data": [
        {"symbol": "BTC", "price": 45000, "change_24h": 2.5},
        {"symbol": "ETH", "price": 3200, "change_24h": -1.2}
    ],
    "schema": {
        "type": "object",
        "properties": {
            "symbol": {"type": "string"},
            "price": {"type": "number"},
            "change_24h": {"type": "number"}
        }
    },
    "data_source": "DeepSeek AI",
    "update_frequency": "real-time"
}

# Send to API server
result = ai_integration.receive_ai_data(api_payload)
print(result)
# Output: {"status": "success", "api_endpoint": "/api/crypto_prices"}
```

### Access Generated API

```bash
# List all APIs
curl http://localhost:8000/apis

# Get data from specific API
curl http://localhost:8000/api/crypto_prices

# Get with pagination
curl "http://localhost:8000/api/crypto_prices?limit=10&offset=0"

# Search data
curl "http://localhost:8000/api/crypto_prices?search=bitcoin"

# Get API statistics
curl http://localhost:8000/apis/crypto_prices/stats

# Get API schema
curl http://localhost:8000/api/crypto_prices/schema
```

## 📦 Components

### AI Layer (`ai_layer/`)

| File | Purpose |
|------|---------|
| `deepseek_client.py` | DeepSeek API client with retry logic |
| `config.py` | Configuration from environment variables |
| `prompt_builder.py` | Constructs optimized prompts |
| `input_processor.py` | Validates form inputs |
| `response_generator.py` | Orchestrates AI generation |
| `response_validator.py` | Validates and parses JSON |
| `models.py` | Data models |
| `exceptions.py` | Custom exceptions |

### Integration Layer

| File | Purpose |
|------|---------|
| `ai_integration.py` | Bridges AI layer and API server |
| `data/mock_data.py` | AI-powered data generation |

### API Layer

| File | Purpose |
|------|---------|
| `api_server.py` | FastAPI server |
| `database.py` | Database operations |

### UI Layer

| File | Purpose |
|------|---------|
| `app.py` | Streamlit interface |
| `components/` | UI components |

## 🔧 Configuration

### Environment Variables

```bash
# Required
DEEPSEEK_API_KEY=sk-your-key-here

# Optional (with defaults)
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.3
DEEPSEEK_MAX_TOKENS=8000
```

### Performance Tuning

**For faster responses:**
```bash
DEEPSEEK_TEMPERATURE=0.1  # More deterministic
DEEPSEEK_MAX_TOKENS=4000  # Smaller responses
```

**For larger datasets:**
```bash
DEEPSEEK_TEMPERATURE=0.3  # Balanced
DEEPSEEK_MAX_TOKENS=16000  # Larger responses
```

## 🐛 Troubleshooting

### Issue: "DEEPSEEK_API_KEY not set"

**Solution:**
```bash
# Create .env file
cp .env.example .env

# Edit .env and add your key
# Get key from: https://platform.deepseek.com/
```

### Issue: "API Server not running"

**Solution:**
```bash
# Check if port 8000 is in use
netstat -an | grep 8000  # Linux/Mac
netstat -an | findstr 8000  # Windows

# Start API server
python api_server.py
```

### Issue: "Rate limit exceeded"

**Solution:**
- Wait for rate limit to reset (check response headers)
- Upgrade your DeepSeek plan
- Reduce request frequency

### Issue: "Invalid JSON response"

**Solution:**
- Check AI layer logs
- Simplify your data description
- Provide explicit field names
- Add custom structure example

### Issue: "Connection timeout"

**Solution:**
```bash
# Increase timeout in config
DEEPSEEK_REQUEST_TIMEOUT=120  # seconds
```

## 📊 Monitoring

### Check System Health

```bash
# API Server health
curl http://localhost:8000/health

# List all APIs
curl http://localhost:8000/apis

# Get API statistics
curl http://localhost:8000/apis/{api_name}/stats
```

### View Logs

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
```

### Database Inspection

```python
from database import db

# Get all APIs
apis = db.get_all_apis()
print(f"Total APIs: {len(apis)}")

# Get API data count
count = db.get_api_data_count(api_id)
print(f"Records: {count}")
```

## 🔒 Security

### API Key Management
- ✅ Never commit `.env` file
- ✅ Use environment variables in production
- ✅ Rotate API keys regularly
- ✅ Monitor API usage

### API Server Security
- ✅ Add authentication middleware
- ✅ Implement rate limiting
- ✅ Validate all inputs
- ✅ Use HTTPS in production
- ✅ Configure CORS appropriately

## 🚢 Production Deployment

### Environment Setup

```bash
# Production environment variables
DEEPSEEK_API_KEY=sk-prod-key
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "start_all.py"]
```

Build and run:
```bash
docker build -t ai-api-generator .
docker run -p 8000:8000 -p 8501:8501 --env-file .env ai-api-generator
```

### Scaling

For production scale:
1. Use PostgreSQL instead of SQLite
2. Add Redis for caching
3. Deploy behind load balancer
4. Use async workers for AI generation
5. Implement request queuing
6. Add monitoring (Prometheus, Grafana)

## 📚 API Documentation

### Create API

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

Response:
```json
{
  "status": "success",
  "apis": [
    {
      "id": 1,
      "name": "cryptocurrency_prices",
      "description": "Real-time crypto data",
      "endpoint": "/api/cryptocurrency_prices",
      "created_at": "2025-01-14T10:00:00Z"
    }
  ]
}
```

### Get API Data

```http
GET /api/{api_name}?limit=100&offset=0&search=bitcoin
```

Response:
```json
{
  "status": "success",
  "data": [...],
  "metadata": {
    "total_count": 100,
    "returned_count": 10,
    "response_time_ms": 45
  }
}
```

## 🎓 Examples

### Example 1: Weather Data

```python
form_data = {
    "data_description": "Weather data for major cities",
    "desired_fields": "city\ntemperature\nhumidity\ncondition",
    "update_frequency": "hourly"
}

response = generator.generate_response(form_data)
```

### Example 2: Stock Prices

```python
form_data = {
    "data_description": "Stock prices for tech companies",
    "desired_fields": "symbol\ncompany\nprice\nvolume\nmarket_cap",
    "update_frequency": "real-time"
}

response = generator.generate_response(form_data)
```

### Example 3: Product Catalog

```python
form_data = {
    "data_description": "E-commerce product catalog",
    "desired_fields": "id\nname\nprice\ncategory\nrating\nstock",
    "update_frequency": "daily"
}

response = generator.generate_response(form_data)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: See `DEEPSEEK_INTEGRATION.md`
- **Issues**: Check logs in `api_server.log`
- **Testing**: Run `python test_integration.py`
- **DeepSeek Docs**: https://platform.deepseek.com/docs

## 🎉 Success!

If everything is working:
- ✅ Configuration loaded
- ✅ API server running
- ✅ AI generation working
- ✅ Data integration successful
- ✅ API endpoints accessible

You're ready to generate APIs! 🚀
