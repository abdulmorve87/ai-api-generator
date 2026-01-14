# Generic Web Scraper - Usage Guide

## Overview

The `test_script_executor.py` script is a command-line tool that scrapes multiple URLs and displays the complete HTML content from each page. It uses the Phase 1 Static Scraping Layer to fetch and extract content.

## Features

✅ **Multiple URL Support** - Scrape multiple websites in one command  
✅ **Complete Content Extraction** - Gets entire page body (no specific selectors)  
✅ **Execution History** - Tracks all scraping operations  
✅ **Performance Metrics** - Shows execution time for each URL  
✅ **Error Handling** - Gracefully handles failed requests  
✅ **Clean Output** - Well-formatted display of scraped content

## Usage

### Basic Syntax

```bash
python test_script_executor.py <url1> <url2> <url3> ...
```

### Examples

#### Scrape a Single URL

```bash
python test_script_executor.py https://example.com
```

#### Scrape Multiple URLs

```bash
python test_script_executor.py https://example.com https://httpbin.org/html
```

#### Scrape Three URLs

```bash
python test_script_executor.py https://example.com https://httpbin.org/html https://www.formula1.com/en/racing/2025
```

### Help Message

Run without arguments to see usage instructions:

```bash
python test_script_executor.py
```

Output:

```
================================================================================
GENERIC WEB SCRAPER
================================================================================

Usage:
    python test_script_executor.py <url1> <url2> <url3> ...

Example:
    python test_script_executor.py https://example.com https://httpbin.org/html

Description:
    Scrapes the provided URLs and displays the complete HTML content.
    No specific selectors are used - the entire page body is extracted.
================================================================================
```

## Output Format

### For Each URL

```
================================================================================
SCRAPING URL #1: https://example.com
================================================================================
🚀 Fetching content...

────────────────────────────────────────────────────────────────────────────────
RESULTS
────────────────────────────────────────────────────────────────────────────────
✅ Success: True
⏱️  Execution Time: 0.15s
📊 Items Extracted: 1

────────────────────────────────────────────────────────────────────────────────
SCRAPED CONTENT
────────────────────────────────────────────────────────────────────────────────

Item 1:

html_content:
--------------------------------------------------------------------------------
[Complete HTML content from the page body]
--------------------------------------------------------------------------------
```

### Execution Summary

After all URLs are scraped, you'll see a summary:

```
================================================================================
EXECUTION SUMMARY
================================================================================

Total executions: 3
✅ Successful: 3
❌ Failed: 0

Detailed History:

   ✅ Execution ID: b9a4c294-f11b-4fac-926b-1d707a4f1990
      URL: https://example.com
      Items: 1
      Time: 0.17s

   ✅ Execution ID: 5c621c8e-2a25-4429-a784-fe7ca76ff22e
      URL: https://httpbin.org/html
      Items: 1
      Time: 0.92s

   ✅ Execution ID: bcbca5aa-5f00-4554-bf13-370be3a9f99c
      URL: https://www.formula1.com/en/racing/2025
      Items: 1
      Time: 0.53s

================================================================================
✅ SCRAPING COMPLETE!
================================================================================
```

## How It Works

1. **URL Input** - Takes URLs from command line arguments
2. **Script Creation** - Creates a scraping script for each URL
3. **Execution** - Uses ScriptExecutor to run each script
4. **Content Extraction** - Extracts entire `<body>` content using CSS selector
5. **Display** - Shows complete HTML content for each URL
6. **Summary** - Provides execution statistics and history

## Technical Details

### Components Used

- **StaticScraper** - Fetches HTML using aiohttp
- **ScrapingEngine** - Orchestrates scraping operations
- **ScriptExecutor** - Executes scraping scripts and tracks history

### Selector Used

The script uses a single CSS selector:

- `body` - Extracts all content from the page body

This means you get the complete text content of the page without any specific filtering.

### Timeout

Default timeout: **30 seconds** per URL

## Limitations

### Static Content Only

This scraper only works with **static HTML content**. It cannot:

- Execute JavaScript
- Render dynamic content (React, Vue, Angular apps)
- Interact with pages (clicks, scrolls)
- Handle authentication

For JavaScript-heavy sites like Formula 1, you'll only get the initial HTML, not the dynamically loaded content.

### Example: Formula 1 Website

When scraping `https://www.formula1.com/en/racing/2025`:

- ✅ Gets initial HTML structure
- ✅ Gets static text content
- ❌ Misses JavaScript-rendered race data
- ❌ Misses dynamically loaded components

**Recommendation:** For dynamic sites, use Phase 3 (Dynamic Scraper with Playwright) when available.

## Error Handling

If a URL fails to scrape, you'll see:

```
────────────────────────────────────────────────────────────────────────────────
RESULTS
────────────────────────────────────────────────────────────────────────────────
✅ Success: False
⏱️  Execution Time: 0.50s
📊 Items Extracted: 0

❌ ERRORS:
   HTTP request failed: 404 Not Found
```

The script will continue scraping remaining URLs even if one fails.

## Performance

Typical execution times:

- **Simple pages** (example.com): 0.1-0.2s
- **Medium pages** (httpbin.org): 0.5-1.0s
- **Complex pages** (formula1.com): 0.5-1.5s

Times vary based on:

- Network latency
- Page size
- Server response time

## Use Cases

### 1. Quick Content Inspection

```bash
python test_script_executor.py https://example.com
```

Quickly see what content is available on a page.

### 2. Batch Scraping

```bash
python test_script_executor.py \
  https://site1.com \
  https://site2.com \
  https://site3.com
```

Scrape multiple sites in one command.

### 3. Content Comparison

```bash
python test_script_executor.py \
  https://site1.com/page \
  https://site2.com/page
```

Compare content from different sources.

### 4. Testing Scraper

```bash
python test_script_executor.py https://httpbin.org/html
```

Test the scraper with a known-good URL.

## Integration with Your App

You can use the same components in your Streamlit app:

```python
import asyncio
from scraping_layer import StaticScraper, ScrapingEngine
from scraping_layer.script_execution import ScriptExecutor
from scraping_layer.script_execution.models import ScrapingScript
from scraping_layer.models import ScrapingStrategy

# Initialize
scraper = StaticScraper()
engine = ScrapingEngine(static_scraper=scraper)
executor = ScriptExecutor(scraping_engine=engine)

# Create script
script = ScrapingScript(
    script_id="my-script",
    name="My Scraper",
    description="Scrape website",
    url="https://example.com",
    strategy=ScrapingStrategy.STATIC,
    selectors={"html_content": "body"}
)

# Execute
result = asyncio.run(executor.execute_script(script))

# Use data
if result.success:
    content = result.data[0]["html_content"]
    st.write(content)
```

## Troubleshooting

### Issue: "No module named 'scraping_layer'"

**Solution:** Make sure you're in the correct directory:

```bash
cd /path/to/ai-api-generator
python test_script_executor.py <url>
```

### Issue: Timeout errors

**Solution:** Increase timeout in the script (line 48):

```python
timeout=60,  # Increase from 30 to 60 seconds
```

### Issue: Empty content

**Solution:** The page might be JavaScript-rendered. Try:

1. View page source in browser
2. If mostly empty, the site uses JavaScript
3. Wait for Phase 3 (Dynamic Scraper)

## Next Steps

### Phase 2: Enhanced Features

- Data cleaning and validation
- Retry logic
- Response caching
- Rate limiting

### Phase 3: Dynamic Scraping

- JavaScript rendering with Playwright
- Browser automation
- Dynamic content extraction
- Interaction support

---

**Happy Scraping! 🚀**

_Last Updated: January 14, 2026_
