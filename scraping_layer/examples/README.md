# Scraping Layer Examples

This directory contains example scripts and utilities for testing the Universal Scraping Layer.

## Files

### `test_scraper.py`

Interactive test script for trying the scraper with real URLs.

**Usage:**

```bash
# Basic usage - extracts title, headings, paragraphs
python test_scraper.py https://example.com

# With custom selectors
python test_scraper.py https://example.com title=h1 description=p

# Multiple selectors
python test_scraper.py https://httpbin.org/html title=h1 content=p
```

### `debug_scraper.py`

Comprehensive debug script that tests individual components step by step.

**Usage:**

```bash
python debug_scraper.py
```

This script runs three tests:

1. Direct HTTP request and BeautifulSoup parsing
2. StaticScraper class functionality
3. Full engine integration

## Quick Examples

```bash
# Test basic functionality
python test_scraper.py https://example.com

# Test with news site
python test_scraper.py https://httpbin.org/html title=h1 content=p

# Test with complex site
python test_scraper.py https://github.com title=h1 description=p

# Debug any issues
python debug_scraper.py
```

## Expected Output

```
🚀 Universal Scraping Layer Test
==================================================
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

## Troubleshooting

If you encounter issues:

1. **Import errors**: Make sure you're running from the project root directory
2. **Network errors**: Check your internet connection and try different URLs
3. **Parsing errors**: Use the debug script to see detailed error information
4. **Missing dependencies**: Install requirements with `pip install -r requirements.txt` (from project root)

## Adding New Examples

To add new example scripts:

1. Create a new `.py` file in this directory
2. Import from `scraping_layer` modules
3. Follow the pattern of existing examples
4. Add documentation to this README
