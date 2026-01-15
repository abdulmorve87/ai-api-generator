# Universal Scraping Layer (Phase 1)

A simple, focused scraping system for extracting data from static HTML websites using HTTP requests and CSS selectors.

## 🚀 Quick Start

```python
from scraping_layer import ScrapingEngine, ScriptConfig
from scraping_layer.static_scraper import StaticScraper

# Create scraper and engine
scraper = StaticScraper()
engine = ScrapingEngine(static_scraper=scraper)

# Configure scraping
config = ScriptConfig(
    url="https://example.com",
    selectors={
        "title": "h1",
        "description": "p"
    }
)

# Execute scraping
result = await engine.scrape(config)

if result.success:
    print(f"Extracted {len(result.data)} items")
    for item in result.data:
        print(item)
```

## 📁 Project Structure

```
scraping_layer/
├── __init__.py              # Main package exports
├── models.py                # Data models (simplified)
├── interfaces.py            # Abstract interfaces (simplified)
├── engine.py                # Main orchestrator (simplified)
├── config.py                # Configuration (simplified)
├── static_scraper.py        # Static HTML scraper (TO BE IMPLEMENTED)
├── README.md                # This file
├── script_execution/        # Script execution wrapper
│   ├── __init__.py
│   ├── models.py
│   └── executor.py
└── utils/
    ├── __init__.py
    └── logging.py           # Logging utilities
```

## ✨ Features (Phase 1)

### Current Implementation

- ✅ **Static HTML scraping** - HTTP requests + BeautifulSoup
- ✅ **CSS selector support** - Extract specific elements
- ✅ **Simple configuration** - URL + selectors + timeout
- ✅ **Structured results** - ScrapingResult with metadata
- ✅ **Basic error handling** - Try/catch with error reporting

### Not Implemented (Future Phases)

- ❌ **Dynamic scraping** - JavaScript-rendered content (Phase 3)
- ❌ **Error retry logic** - Exponential backoff (Phase 2)
- ❌ **Data cleaning** - HTML entity decoding (Phase 2)
- ❌ **Caching** - Redis/memory-based caching (Phase 4)
- ❌ **Browser automation** - Playwright integration (Phase 3)

## 🔧 Configuration

The scraping layer uses environment variables for configuration:

```bash
# Network settings
export SCRAPING_REQUEST_TIMEOUT=30
export SCRAPING_USER_AGENT="Mozilla/5.0..."

# Logging
export SCRAPING_LOG_LEVEL=INFO
```

## 📋 Requirements

```
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
```

## 🧪 Testing

```bash
# Run basic test (once implemented)
python -m pytest tests/test_static_scraper.py -v
```

## 🏗️ Architecture

Simple two-layer architecture:

1. **Scraping Engine** - Orchestrates operations
2. **Static Scraper** - Fetches HTML and extracts data

## 🚦 Status

**Phase 1** 🚧 **IN PROGRESS**

- ✅ Spec simplified
- ✅ Models simplified
- ✅ Interfaces simplified
- ✅ Engine simplified
- ✅ Config simplified
- ⏳ StaticScraper implementation (NEXT)

**Next Steps:**

- Implement StaticScraper class
- Add HTTP fetching with aiohttp
- Add BeautifulSoup extraction
- Write basic tests

## 📄 License

Part of the AI API Generator project.
