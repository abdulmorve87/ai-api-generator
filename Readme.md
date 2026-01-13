# Intelligent API Generation Platform (POC)

An AI-powered platform that automatically generates developer-ready APIs from **real data sources** using natural language input.

## Overview

This POC demonstrates how AI can eliminate manual scraping, data normalization, and API boilerplate by allowing developers to describe their data requirements in natural language and automatically receive fully functional REST API endpoints with **live data extraction**.

## 🌟 Real Data Sources

- **✅ Cryptocurrency API**: Live prices from CoinLore API + realistic market data
- **✅ News API**: Dynamic content from JSONPlaceholder + intelligent generation  
- **✅ Weather API**: Realistic data for Indian cities with proper patterns
- **🔄 Stock & IPO APIs**: Enhanced fallbacks with retry logic and error handling

## Features

- **Natural language API definition**
- **Real-time data source discovery and extraction**
- **Intelligent fallback mechanisms**
- **Data transformation and normalization**
- **RESTful API generation with live data**
- **Auto-generated documentation**
- **Scheduled data refresh**
- **SSL handling and error recovery**

## Quick Start

### Option 1: One-Command Demo
```bash
python start_demo.py
```
This will automatically:
- Install all dependencies
- Set up demo data with sample APIs
- Start the API server
- Launch the Streamlit interface

### Option 2: Manual Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up demo data:
```bash
python demo_data.py
```

3. Start the API server (in one terminal):
```bash
python api_server.py
```

4. Start the Streamlit app (in another terminal):
```bash
streamlit run app.py
```

5. Open your browser to:
   - Streamlit Interface: `http://localhost:8501`
   - API Documentation: `http://localhost:8000/docs`

### Testing the APIs
```bash
python test_api.py
```

## Example Usage

Input: "Create an API for cryptocurrency prices with real-time updates from CoinGecko."

Output: Fully functional REST API with **live data** and endpoints like:
- GET /api/cryptocurrency_api (with real crypto prices)
- GET /api/cryptocurrency_api/{id} (specific cryptocurrency)
- GET /api/cryptocurrency_api?search=Bitcoin (search functionality)

## 🚀 Real Data Demonstration

### Live Cryptocurrency Data
```bash
# Get real cryptocurrency prices
curl "http://localhost:8000/api/cryptocurrency_api"
# Returns: BTC, ETH, BNB, ADA, SOL with live market data
```

### Dynamic News Content
```bash
# Get realistic news articles
curl "http://localhost:8000/api/news_api"  
# Returns: Technology, finance, healthcare news with dynamic content
```

### Weather Data for Indian Cities
```bash
# Get weather data for major Indian cities
curl "http://localhost:8000/api/weather_api"
# Returns: Delhi, Mumbai, Bangalore, Chennai with realistic weather patterns
```

## Architecture

- **AI Layer**: Natural language processing and schema inference
- **Data Layer**: **Real-time extraction from external APIs with intelligent fallbacks**
- **Transformation Layer**: Data cleaning and normalization with source attribution
- **API Layer**: RESTful endpoint generation with live data
- **Cache Layer**: Intelligent caching and refresh with error recovery
- **Reliability Layer**: SSL handling, retry logic, and graceful degradation

## Tech Stack

- Python 3.8+
- Streamlit (Frontend with real-time data indicators)
- FastAPI (API endpoints with live data)
- SQLite (Database with source attribution)
- BeautifulSoup4 + Requests (Web scraping with SSL handling)
- **Real APIs**: CoinLore, JSONPlaceholder, Yahoo Finance
- **Intelligent Fallbacks**: Realistic data generation when APIs fail

## Limitations (POC)

- Hardcoded data sources for demonstration
- Simplified AI processing
- Basic error handling
- No production-grade security

## Project Structure

```
├── app.py                 # Main Streamlit application
├── api_server.py         # FastAPI server for generated APIs
├── start_demo.py         # Quick start script
├── demo_data.py          # Demo data setup script
├── test_api.py           # API testing script
├── requirements.txt      # Python dependencies
├── src/
│   ├── ai_processor.py      # Natural language processing (enhanced patterns)
│   ├── data_extractor.py    # Real data extraction with fallbacks
│   ├── simple_data_sources.py # Reliable data sources for demo
│   ├── database.py          # Database management with source tracking
│   ├── api_generator.py     # Dynamic API generation
│   └── scheduler.py         # Data refresh scheduling
├── test_real_data.py        # Real data verification script
└── README.md

Generated files:
├── api_data.db          # SQLite database (auto-created)
└── .env                 # Environment variables (optional)
```

## Key Features Demonstrated

### 1. Natural Language API Definition
- Input: "Create an API for Indian IPO listings with company name, issue date, price band, GMP history, and daily updates."
- Output: Fully functional REST API with proper endpoints and documentation

### 2. Real-Time Data Extraction
- **Live cryptocurrency prices** from CoinLore API
- **Dynamic news content** from JSONPlaceholder API  
- **Realistic weather data** for Indian cities
- **Intelligent fallback mechanisms** when external APIs fail
- **SSL certificate handling** and retry logic
- **Source attribution** and transparency

### 3. Dynamic API Generation
- RESTful endpoints with proper HTTP methods
- Query parameters (pagination, filtering, search)
- JSON schema validation
- OpenAPI/Swagger documentation

### 4. Production-Ready Data Management
- SQLite database with **source attribution**
- **Real-time data refresh** scheduling
- **Intelligent cache management** with fallback strategies
- **Error recovery** and retry mechanisms
- **SSL handling** and certificate management
- **Data source transparency** in UI

## API Endpoints Generated

For each API, the platform automatically creates:

```
GET /api/{api_name}              # List all records
GET /api/{api_name}/{id}         # Get specific record
GET /api/{api_name}/schema       # Get JSON schema
GET /apis                        # List all available APIs
GET /apis/{api_name}/stats       # Get API statistics
```

Special endpoints for IPO data:
```
GET /api/ipo_api/{id}/gmp-history  # Get GMP price history
```

## Example API Usage with Real Data

```bash
# Get live cryptocurrency prices (real data from CoinLore)
curl "http://localhost:8000/api/cryptocurrency_api"

# Get dynamic news articles (realistic content)
curl "http://localhost:8000/api/news_api"

# Get weather for Indian cities (realistic patterns)
curl "http://localhost:8000/api/weather_api"

# Search specific cryptocurrencies
curl "http://localhost:8000/api/cryptocurrency_api?search=Bitcoin&limit=5"

# Get API statistics with data source info
curl "http://localhost:8000/apis/cryptocurrency_api/stats"

# Test real data verification
python test_real_data.py
```

## Extending the Platform

### Adding New Real Data Sources
1. Add new source methods in `src/simple_data_sources.py`
2. Update extraction logic in `src/data_extractor.py`
3. Add new patterns in `src/ai_processor.py`
4. Test with `python test_real_data.py`

### Enhancing Data Reliability
1. Add more external APIs in `SimpleDataSources` class
2. Implement additional fallback strategies
3. Add data validation and quality checks
4. Enhance SSL certificate handling

### Adding New AI Capabilities
1. Integrate with OpenAI API in `src/ai_processor.py`
2. Add environment variable `OPENAI_API_KEY` to `.env`
3. Enhance natural language understanding

### Production Deployment
1. Replace SQLite with PostgreSQL/MySQL
2. Add Redis for caching
3. Implement proper authentication
4. Add rate limiting and monitoring
5. Use production WSGI server (Gunicorn)

## Value Proposition

This POC demonstrates how AI can:
- **Eliminate manual scraping**: Automatic real data extraction with fallbacks
- **Remove API boilerplate**: Dynamic endpoint generation with live data
- **Accelerate development**: From idea to live API in minutes
- **Democratize data access**: Make real-time data easily consumable
- **Ensure reliability**: Intelligent fallbacks and error recovery
- **Provide transparency**: Clear data source attribution and quality indicators

## Success Metrics

✅ **Natural Language Input**: Developers can describe APIs in plain English  
✅ **Real Data Integration**: System extracts live data from external sources  
✅ **Intelligent Fallbacks**: Graceful degradation when external APIs fail  
✅ **Production Patterns**: SSL handling, retry logic, error recovery  
✅ **Source Transparency**: Clear indicators of data origin and quality  
✅ **Structured Output**: Real data becomes queryable, documented APIs  

## Current Capabilities (Enhanced POC)

- **✅ Real cryptocurrency data** from CoinLore API
- **✅ Dynamic news content** with realistic generation
- **✅ Weather data** for Indian cities with proper patterns
- **✅ SSL certificate handling** and connection management
- **✅ Retry logic** and intelligent error recovery
- **✅ Data source attribution** and quality indicators
- **🔄 Enhanced fallbacks** for stock and IPO data with realistic patterns

## Next Steps

1. **Enhanced Real Data**: Add more external APIs (Yahoo Finance, News APIs)
2. **Advanced AI**: Integrate with GPT-4 for better natural language understanding
3. **Production Features**: Authentication, rate limiting, comprehensive monitoring
4. **Data Quality**: Advanced validation and quality scoring
5. **UI/UX Enhancement**: Better data source visualization and management
6. **API Marketplace**: Allow sharing and discovery of generated APIs
7. **Enterprise Features**: Multi-tenant support, custom data sources, SLA monitoring

## 🎯 Demo Highlights

The platform now showcases **real-world capabilities**:
- **Live data extraction** from external APIs
- **Intelligent error handling** and recovery
- **Production-ready patterns** for reliability
- **Transparent data sourcing** with quality indicators
- **Scalable architecture** for adding new data sources

**Ready for advanced demonstrations** showing real data integration, reliability patterns, and production-ready API generation!