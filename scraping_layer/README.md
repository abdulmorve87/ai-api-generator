# Universal Scraping Layer

A comprehensive scraping system that handles both static and dynamic websites with AI-generated script execution, security sandboxing, and intelligent strategy selection.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test the scraper (from project root)
python test_scraper.py https://example.com title=h1 description=p

# Or run directly from examples directory
cd scraping_layer/examples
python test_scraper.py https://example.com title=h1 description=p
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
├── utils/
│   ├── __init__.py
│   └── logging.py           # Logging utilities
├── examples/
│   ├── README.md            # Examples documentation
│   ├── test_scraper.py      # Interactive test script
│   └── debug_scraper.py     # Debug and diagnostics
└── docs/
    └── USAGE.md             # Detailed usage guide
```

## ✨ Features

### Current (Task 1 Complete)

- ✅ **Static website scraping** - HTTP requests + BeautifulSoup
- ✅ **CSS selector support** - Extract specific elements
- ✅ **Data cleaning** - HTML entity decoding, whitespace normalization
- ✅ **Error handling** - Graceful failure with detailed logging
- ✅ **Performance metrics** - Timing and extraction statistics
- ✅ **Configuration system** - Environment-based configuration
- ✅ **Structured logging** - JSON logs with context
- ✅ **Testing framework** - Property-based testing with Hypothesis

### Upcoming (Tasks 2-15)

- 🚧 **Dynamic website scraping** - Playwright browser automation
- 🚧 **AI script execution** - Sandboxed execution environment
- 🚧 **Content detection** - Framework identification
- 🚧 **Anti-bot handling** - User agent rotation, delays
- 🚧 **Caching system** - Redis/memory-based caching
- 🚧 **Browser management** - Instance pooling and cleanup
- 🚧 **Template system** - BeautifulSoup/Playwright templates

## 🧪 Testing

```bash
# Run basic tests
cd scraping_layer/examples
python test_scraper.py https://example.com

# Run debug tests
python debug_scraper.py

# Run unit tests
cd ../..
python -m pytest tests/ -v
```

## 📖 Documentation

- **[Usage Guide](docs/USAGE.md)** - Detailed usage instructions
- **[Examples](examples/README.md)** - Example scripts and patterns
- **[Requirements](../docs/kiro-spec.md)** - Original project specification
- **[Design](../.kiro/specs/universal-scraping-layer/design.md)** - Architecture and design
- **[Tasks](../.kiro/specs/universal-scraping-layer/tasks.md)** - Implementation roadmap

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

The scraping layer integrates with the main AI API Generator:

```python
from scraping_layer import ScrapingEngine, ScriptConfig, ScrapingStrategy

# Create configuration
config = ScriptConfig(
    url="https://example.com",
    script_type=ScrapingStrategy.STATIC,
    selectors={"title": "h1", "content": "p"}
)

# Execute scraping
engine = ScrapingEngine(...)  # Inject dependencies
result = await engine.scrape(config)

# Use extracted data
if result.success:
    data = result.data
    # Serve via API endpoints
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

**Task 1: Project Setup** ✅ **COMPLETE**

- Core interfaces and models
- Configuration system
- Logging framework
- Basic static scraping
- Testing infrastructure

**Next: Task 2** - Content Detector implementation

## 📄 License

Part of the AI API Generator project.
