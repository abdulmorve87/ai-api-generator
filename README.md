# AI-Powered API Generator

An automated API generation platform that bridges the gap between publicly available data and developer-ready API endpoints. Transform natural language requirements into production-ready APIs with intelligent web scraping.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up DeepSeek API key (required for AI features)
export DEEPSEEK_API_KEY=your_api_key_here

# Or create a .env file
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env

# Run the application
streamlit run app.py

# Test the scraping layer
python test_scraper.py https://example.com title=h1 description=p
```

## 📋 Features

### ✅ AI Response Generator (Phase 1 Complete)

- **DeepSeek AI Integration** - Generate realistic API responses using AI
- **Form Input Processing** - Convert user requirements to AI prompts
- **JSON Response Generation** - Create structured API responses
- **Response Validation** - Ensure valid JSON output
- **Error Handling** - Clear error messages with troubleshooting hints
- **UI Integration** - Display generated responses with metadata

### ✅ Universal Scraping Layer (Task 1 Complete)

- **Static website scraping** - HTTP requests + BeautifulSoup
- **CSS selector support** - Extract specific elements
- **Data cleaning** - HTML entity decoding, normalization
- **Error handling** - Graceful failure with detailed logging
- **Performance metrics** - Timing and extraction statistics
- **Configuration system** - Environment-based settings
- **Testing framework** - Property-based testing with Hypothesis

### 🚧 Upcoming Features

- **Dynamic website scraping** - JavaScript-rendered content (Playwright)
- **AI script generation** - Natural language to scraping scripts
- **API endpoint generation** - Automatic REST API creation
- **Caching system** - Redis/memory-based caching
- **Anti-bot handling** - User agent rotation, delays
- **Authentication** - Rate limiting and API keys

## 🏗️ Architecture

```
AI API Generator
├── 🌐 Streamlit UI          # User interface
├── 🤖 AI Processing Layer   # Requirement analysis + code generation
├── 🕷️ Universal Scraping Layer # Web scraping engine
├── 📊 Data Transformation   # Clean and validate data
└── 🚀 FastAPI Backend       # Serve generated endpoints
```

## 📁 Project Structure

```
├── 📄 README.md                    # This file
├── 📄 requirements.txt             # All dependencies
├── 📄 .env                         # Environment variables (create this)
├── 📄 test_scraper.py              # Quick test script
├── 📄 app.py                       # Main Streamlit app
├── 🤖 ai_layer/                    # AI Response Generator
│   ├── 📄 __init__.py              # Module exports
│   ├── 📄 config.py                # Configuration management
│   ├── 📄 deepseek_client.py      # DeepSeek API client
│   ├── 📄 response_generator.py   # Main orchestrator
│   ├── 📄 prompt_builder.py       # Prompt construction
│   ├── 📄 input_processor.py      # Form input processing
│   ├── 📄 response_validator.py   # JSON validation
│   ├── 📄 models.py                # Data models
│   └── 📄 exceptions.py            # Custom exceptions
├── 🕷️ scraping_layer/              # Universal Scraping Layer
│   ├── 📄 README.md                # Scraping layer docs
│   ├── 📄 engine.py                # Main orchestrator
│   ├── 📄 models.py                # Data models
│   ├── 📄 interfaces.py            # Abstract interfaces
│   ├── 📄 config.py                # Configuration
│   ├── 📁 examples/                # Test scripts
│   ├── 📁 docs/                    # Documentation
│   └── 📁 utils/                   # Utilities
├── 🧪 tests/                       # Unit tests
├── 📁 components/                  # UI components
├── 📁 utils/                       # UI utilities
└── 📁 data/                        # Mock data
```

## 🧪 Testing the Scraper

### Basic Usage

```bash
# Extract basic page info
python test_scraper.py https://example.com

# Extract specific fields
python test_scraper.py https://example.com title=h1 description=p

# Test with different sites
python test_scraper.py https://httpbin.org/html title=h1 content=p
```

### Expected Output

```
🚀 Universal Scraping Layer Test
Target URL: https://example.com
Selectors: {'title': 'h1', 'description': 'p'}

📊 SCRAPING RESULTS
Success: True
Items extracted: 1
Strategy used: static
Duration: 0.86 seconds

📋 EXTRACTED DATA:
Item 1:
  title: Example Domain
  description: This domain is for use in documentation...
```

## 🛠️ Development

### Running the Main App

```bash
# Start the Streamlit UI
streamlit run app.py
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run scraping layer tests specifically
python -m pytest tests/test_setup.py -v
```

### Debug Mode

```bash
# Detailed scraping diagnostics
python scraping_layer/examples/debug_scraper.py
```

## 📖 Documentation

- **[Scraping Layer](scraping_layer/README.md)** - Universal scraping system
- **[Usage Guide](scraping_layer/docs/USAGE.md)** - Detailed usage instructions
- **[Examples](scraping_layer/examples/README.md)** - Example scripts
- **[Original Spec](docs/kiro-spec.md)** - Project specification
- **[Design Docs](.kiro/specs/universal-scraping-layer/)** - Architecture and tasks

## 🔧 Configuration

Configure via environment variables or `.env` file:

### AI Layer Configuration

```bash
# Required: DeepSeek API key
export DEEPSEEK_API_KEY=your_api_key_here

# Optional: DeepSeek API settings
export DEEPSEEK_BASE_URL=https://api.deepseek.com  # Default
export DEEPSEEK_MODEL=deepseek-chat                # Default
export DEEPSEEK_TEMPERATURE=0.7                    # Default (0.0-1.0)
export DEEPSEEK_MAX_TOKENS=2000                    # Default
```

### Scraping Layer Configuration

```bash
# Scraping settings
export SCRAPING_MAX_EXECUTION_TIME=300
export SCRAPING_MAX_MEMORY_MB=512
export SCRAPING_LOG_LEVEL=INFO

# Browser settings
export SCRAPING_MAX_BROWSERS=5
export SCRAPING_HEADLESS=true

# Cache settings
export SCRAPING_CACHE_BACKEND=memory
export SCRAPING_CACHE_TTL=3600
```

### Getting Your DeepSeek API Key

1. Visit [DeepSeek Platform](https://platform.deepseek.com)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Click "Generate New Key"
5. Copy the key and add it to your `.env` file

### Troubleshooting

**Configuration Error: DEEPSEEK_API_KEY not found**

- Ensure you've created a `.env` file in the project root
- Verify the API key is correctly set: `DEEPSEEK_API_KEY=sk-...`
- Restart the application after adding the key

**Authentication Failed**

- Verify your API key is correct and hasn't expired
- Check that you haven't exceeded your API quota
- Get a new key from the DeepSeek platform if needed

**Rate Limit Exceeded**

- Wait for the specified retry period
- Consider upgrading your API plan for higher limits
- Reduce the frequency of requests

**Connection Error**

- Check your internet connection
- Verify you can access https://api.deepseek.com
- Check if a firewall is blocking the connection

## 🚦 Status

**✅ Task 1: Project Setup & Static Scraping** - COMPLETE

- Core interfaces and models
- Configuration system
- Logging framework
- Static website scraping
- Testing infrastructure

**🚧 Next: Task 2** - Content Detector implementation

## 🤝 How It Works

1. **📝 User Input** - Describe data needs in natural language
2. **🤖 AI Analysis** - Extract URLs, fields, and scraping strategy
3. **🕷️ Web Scraping** - Execute scraping with appropriate strategy
4. **🧹 Data Cleaning** - Normalize and validate extracted data
5. **🚀 API Generation** - Create REST endpoints serving the data
6. **📊 Monitoring** - Track performance and data quality

## 📄 License

Built for Hackathon 2025 | Powered by AI
