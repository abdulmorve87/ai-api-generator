"""
Generic Web Scraper - Scrape multiple URLs and display complete HTML content.

Usage:
    python scraping_layer/test/test_script_executor.py <url1> <url2> <url3> ...

Example:
    python scraping_layer/test/test_script_executor.py https://example.com https://httpbin.org/html
"""

import asyncio
import sys
import logging
from datetime import datetime
from typing import List
from pathlib import Path

# Add parent directory to path so we can import scraping_layer
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scraping_layer import StaticScraper, ScrapingEngine
from scraping_layer.script_execution import ScriptExecutor
from scraping_layer.script_execution.models import ScrapingScript
from scraping_layer.models import ScrapingStrategy


# Configure logging to only show errors
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def scrape_url(executor: ScriptExecutor, url: str, script_num: int) -> None:
    """Scrape a single URL and display the complete output."""
    
    print(f"\n{'='*80}")
    print(f"SCRAPING URL #{script_num}: {url}")
    print(f"{'='*80}")
    
    # Create a script for this URL
    script = ScrapingScript(
        script_id=f"script-{script_num:03d}",
        name=f"Scraper #{script_num}",
        description=f"Generic scraper for {url}",
        url=url,
        strategy=ScrapingStrategy.STATIC,
        selectors={
            "html_content": "body"  # Get entire body content
        },
        timeout=30,
        created_at=datetime.now(),
        created_by="cli_user",
        tags=["cli", "generic"]
    )
    
    # Execute the script
    print(f"🚀 Fetching content...")
    result = await executor.execute_script(script)
    
    # Display results
    print(f"\n{'─'*80}")
    print(f"RESULTS")
    print(f"{'─'*80}")
    print(f"✅ Success: {result.success}")
    print(f"⏱️  Execution Time: {result.execution_time:.2f}s")
    print(f"📊 Items Extracted: {result.total_items}")
    
    if result.errors:
        print(f"\n❌ ERRORS:")
        for error in result.errors:
            print(f"   {error}")
        return
    
    if result.data:
        print(f"\n{'─'*80}")
        print(f"SCRAPED CONTENT")
        print(f"{'─'*80}\n")
        
        for i, item in enumerate(result.data, 1):
            print(f"Item {i}:")
            for key, value in item.items():
                print(f"\n{key}:")
                print(f"{'-'*80}")
                print(value)
                print(f"{'-'*80}")
    else:
        print(f"\n⚠️  No data extracted from {url}")


async def scrape_multiple_urls(urls: List[str]) -> None:
    """Scrape multiple URLs and display results."""
    
    print("=" * 80)
    print("GENERIC WEB SCRAPER")
    print("=" * 80)
    print(f"\n📋 URLs to scrape: {len(urls)}")
    for i, url in enumerate(urls, 1):
        print(f"   {i}. {url}")
    
    # Create components
    scraper = StaticScraper()
    engine = ScrapingEngine(static_scraper=scraper)
    executor = ScriptExecutor(scraping_engine=engine)
    
    # Scrape each URL
    for i, url in enumerate(urls, 1):
        await scrape_url(executor, url, i)
    
    # Display execution summary
    print(f"\n{'='*80}")
    print(f"EXECUTION SUMMARY")
    print(f"{'='*80}")
    
    history = executor.get_execution_history()
    print(f"\nTotal executions: {len(history)}")
    
    successful = sum(1 for r in history if r.success)
    failed = len(history) - successful
    
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    print(f"\nDetailed History:")
    for exec_result in history:
        status = "✅" if exec_result.success else "❌"
        print(f"\n   {status} Execution ID: {exec_result.execution_id}")
        print(f"      URL: {exec_result.metadata.url_processed}")
        print(f"      Items: {exec_result.total_items}")
        print(f"      Time: {exec_result.execution_time:.2f}s")
        if exec_result.errors:
            print(f"      Errors: {', '.join(exec_result.errors)}")
    
    print(f"\n{'='*80}")
    print(f"✅ SCRAPING COMPLETE!")
    print(f"{'='*80}\n")


def main():
    """Main entry point."""
    
    # Check if URLs were provided
    if len(sys.argv) < 2:
        print("=" * 80)
        print("GENERIC WEB SCRAPER")
        print("=" * 80)
        print("\nUsage:")
        print(f"    python {sys.argv[0]} <url1> <url2> <url3> ...")
        print("\nExample:")
        print(f"    python {sys.argv[0]} https://example.com https://httpbin.org/html")
        print("\nDescription:")
        print("    Scrapes the provided URLs and displays the complete HTML content.")
        print("    No specific selectors are used - the entire page body is extracted.")
        print("=" * 80)
        sys.exit(1)
    
    # Get URLs from command line arguments
    urls = sys.argv[1:]
    
    # Run the scraper
    asyncio.run(scrape_multiple_urls(urls))


if __name__ == "__main__":
    main()
