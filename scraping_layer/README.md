# Universal Scraping Layer

A comprehensive scraping system that handles both static and dynamic websites with direct script execution, intelligent strategy selection, and robust error handling.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test basic scraping
python test_scraper.py https://example.com title=h1 description=p

# Test script execution layer
python test_script_execution.py

# Run advanced script tests
python scraping_layer/examples/test_script_execution_advanced.py --single
```

## 📁 Project Structure

```
scraping_layer/
├── __init__.py              # Main package exports
├── models.py                # Data models and types
├── interfaces.py            # Abstract interfaces
├── engine.py                # Main orchestrator
├── config.py                # Configuration management
├── README.md                # This file
├── script_execution/        # Direct script execution layer
│   ├── __init__.py
│   ├── models.py            # Script execution models
│   └── executor.py          # Script executor
├── utils/
│   ├── __init__.py
│   └── logging.py           # Logging utilities
├── examples/
│   ├── README.md            # Examples documentation
│   ├── test_scraper.py      # Interactive test script
│   ├── debug_scraper.py     # Debug and diagnostics
│   └── test_script_execution_advanced.py  # Advanced script tests
└── docs/
    ├── USAGE.md             # Detailed usage guide
    └── SCRIPT_EXECUTION.md  # Script execution documentation
```

## ✨ Features

### Current Implementation

- ✅ **Static website scraping** - HTTP requests + BeautifulSoup
- ✅ **CSS selector support** - Extract specific elements
- ✅ **Script execution layer** - Direct execution of pre-written scripts
- ✅ **Form-based script generation** - Convert form inputs to scraping scripts
- ✅ **Data cleaning** - HTML entity decoding, whitespace normalization
- ✅ **Error handling** - Graceful failure with detailed logging
- ✅ **Performance metrics** - Timing and extraction statistics
- ✅ **Execution history** - Track all scraping operations
- ✅ **Configuration system** - Environment-based configuration
- ✅ **Structured logging** - JSON logs with context
- ✅ **Testing framework** - Comprehensive test coverage

### Upcoming Features

- 🚧 **Dynamic website scraping** - Playwright browser automation
- 🚧 **Content detection** - Framework identification
- 🚧 **Anti-bot handling** - User agent rotation, delays
- 🚧 **Caching system** - Redis/memory-based caching
- 🚧 **Browser management** - Instance pooling and cleanup

## 🧪 Testing

```bash
# Test basic scraping functionality
python test_scraper.py https://example.com

# Test script execution layer (form-based flow)
python test_script_execution.py

# Run advanced script execution tests
python scraping_layer/examples/test_script_execution_advanced.py

# Run single quick test
python scraping_layer/examples/test_script_execution_advanced.py --single

# Run unit tests
python -m pytest tests/ -v
```

## 📖 Documentation

- **[Script Execution Guide](docs/SCRIPT_EXECUTION.md)** - Direct script execution documentation
- **[Usage Guide](docs/USAGE.md)** - Detailed usage instructions
- **[Examples](examples/README.md)** - Example scripts and patterns
- **[Requirements](../docs/kiro-spec.md)** - Original project specification

## 🔧 Configuration

The scraping layer uses environment variables for configuration:

```bash
# Security settings
export SCRAPING_MAX_EXECUTION_TIME=300
export SCRAPING_MAX_MEMORY_MB=512

# Browser settings
export SCRAPING_MAX_BROWSERS=5
export SCRAPING_HEADLESS=true

# Cache settings
export SCRAPING_CACHE_BACKEND=memory
export SCRAPING_CACHE_TTL=3600

# Logging
export SCRAPING_LOG_LEVEL=INFO
```

## 🏗️ Architecture

The system follows a layered architecture:

1. **API Layer** - ScrapingEngine (main interface)
2. **Detection Layer** - ContentDetector (website analysis)
3. **Execution Layer** - StaticScraper, DynamicScraper
4. **Support Services** - BrowserManager, CacheManager, ErrorHandler
5. **Data Layer** - DataExtractor, validation, cleaning

## 🤝 Integration

The scraping layer integrates with form-based UIs and provides direct script execution:

```python
from scraping_layer.script_execution import ScrapingScript, ScriptExecutor
from scraping_layer.models import ScrapingStrategy

# Create script from form data
script = ScrapingScript(
    script_id="user_script_001",
    name="User Generated Script",
    description="Extract data based on user requirements",
    url="https://example.com",
    strategy=ScrapingStrategy.STATIC,
    selectors={"title": "h1", "content": "p"},
    expected_fields=["title", "content"]
)

# Execute script
executor = ScriptExecutor(scraping_engine)
result = await executor.execute_script(script)

# Use extracted data
if result.success:
    data = result.data
    # Serve via API endpoints or display in UI
```

## 📋 Requirements

All dependencies are listed in the main project `requirements.txt` file.

**Core dependencies:**

- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `playwright` - Browser automation
- `aiohttp` - Async HTTP
- `pytest` - Testing framework

Install all dependencies from the project root:

```bash
pip install -r requirements.txt
```

## 🚦 Status

**Script Execution Layer** ✅ **COMPLETE**

- Direct script execution without AI generation
- Form-based script creation
- Comprehensive error handling and validation
- Execution history tracking
- Integration with existing scraping engine

**Core Scraping Engine** ✅ **COMPLETE**

- Static website scraping
- CSS selector support
- Data cleaning and validation
- Performance metrics
- Configuration system

**Next Steps** - Dynamic scraping and browser automation

## 📄 License

Part of the AI API Generator project.
