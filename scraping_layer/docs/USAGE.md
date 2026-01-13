# Universal Scraping Layer - Usage Guide

## Quick Start

The Universal Scraping Layer is now ready for testing! You can run the scraper with real URLs and see the results.

## Running the Test Scraper

### Basic Usage

```bash
# Navigate to the examples directory
cd scraping_layer/examples

# Test with a URL (extracts basic page info)
python test_scraper.py https://example.com

# Test with custom selectors
python test_scraper.py https://example.com title=h1 description=p

# Test with multiple selectors
python test_scraper.py https://httpbin.org/html title=h1 content=p author=.author
```

### Example Commands

```bash
# Example.com - Simple static site
python test_scraper.py https://example.com title=h1 description=p

# HTTPBin HTML page - Test HTML content
python test_scraper.py https://httpbin.org/html title=h1 content=p

# Wikipedia page - Complex content
python test_scraper.py https://en.wikipedia.org/wiki/Web_scraping title=h1 summary=p

# GitHub page - Real-world example
python test_scraper.py https://github.com title=h1 description=p
```

## What the Scraper Does

1. **🔍 Analyzes the website** - Determines if it's static or dynamic
2. **📄 Chooses strategy** - Uses static scraping for most sites, dynamic for SPAs
3. **🌐 Makes HTTP request** - Fetches the webpage content
4. **🎯 Extracts data** - Uses CSS selectors to find specific content
5. **🧹 Cleans data** - Removes extra whitespace and decodes HTML entities
6. **📊 Returns results** - Structured data with metadata and performance info

## Selector Examples

| Selector | Description            | Example                 |
| -------- | ---------------------- | ----------------------- |
| `h1`     | First heading          | `title=h1`              |
| `p`      | First paragraph        | `description=p`         |
| `.class` | Element with class     | `content=.main-content` |
| `#id`    | Element with ID        | `header=#main-header`   |
| `[attr]` | Element with attribute | `link=[href]`           |

## Output Format

The scraper returns structured data:

```
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

## Current Features ✅

- ✅ **Static website scraping** - Works with regular HTML sites
- ✅ **CSS selector support** - Extract specific elements
- ✅ **Data cleaning** - Removes whitespace, decodes HTML entities
- ✅ **Error handling** - Graceful failure with error messages
- ✅ **Performance metrics** - Timing and extraction statistics
- ✅ **Flexible selectors** - Multiple field extraction
- ✅ **Basic page extraction** - Automatic title/content extraction

## Upcoming Features 🚧

- 🚧 **Dynamic website scraping** - JavaScript-rendered content (Playwright)
- 🚧 **Anti-bot handling** - User agent rotation, delays
- 🚧 **Caching system** - Store results to avoid re-scraping
- 🚧 **Pagination support** - Multi-page scraping
- 🚧 **Form submission** - Interactive scraping
- 🚧 **AI script execution** - Run AI-generated scraping scripts

## Debug Mode

For detailed debugging, use the debug script:

```bash
cd scraping_layer/examples
python debug_scraper.py
```

This runs comprehensive tests and shows exactly what's happening at each step.

## Integration with Main App

The scraping layer is designed to integrate with the main AI API Generator app. Once complete, users will be able to:

1. Describe their data needs in natural language
2. AI will generate appropriate selectors and scraping strategy
3. The scraping layer will execute the plan and return clean data
4. Data will be served via automatically generated API endpoints

## Project Structure

```
scraping_layer/
├── __init__.py              # Main package exports
├── models.py                # Data models and types
├── interfaces.py            # Abstract interfaces
├── engine.py                # Main orchestrator
├── config.py                # Configuration management
├── utils/
│   ├── __init__.py
│   └── logging.py           # Logging utilities
├── examples/
│   ├── test_scraper.py      # Interactive test script
│   └── debug_scraper.py     # Debug and diagnostics
└── docs/
    └── USAGE.md             # This file
```

## Dependencies

The scraping layer requires these packages (all included in main `requirements.txt`):

```
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
playwright>=1.40.0
aiohttp>=3.9.0
```

Install with:

```bash
# From project root
pip install -r requirements.txt
```

## Need Help?

- Check the console output for detailed step-by-step information
- Use the debug script to see what's happening internally
- All errors are logged with context for easy troubleshooting
- Review the examples in `scraping_layer/examples/` for usage patterns
