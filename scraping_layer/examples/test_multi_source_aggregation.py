"""
Test to verify that multi-source execution properly aggregates data from all sources.

This test ensures that when multiple URLs are provided, the executor:
1. Executes the script against ALL URLs
2. Aggregates data from ALL successful sources
3. Returns combined results, not just the last source

Usage:
    python -m scraping_layer.examples.test_multi_source_aggregation
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scraping_layer.dynamic_execution import (
    DynamicScriptExecutor,
    ExecutionConfig,
)


def test_multi_source_aggregation():
    """Test that data from all sources is aggregated."""
    print("\n" + "=" * 70)
    print("TEST: Multi-Source Data Aggregation")
    print("=" * 70 + "\n")
    
    # Script that returns different data based on URL
    script_code = '''
def scrape_data(url: str = None):
    """Return different data based on URL to verify aggregation."""
    
    # Simulate different sources returning different data
    if 'source1' in url:
        data = [
            {'id': 1, 'source': 'source1', 'title': 'Item 1 from Source 1'},
            {'id': 2, 'source': 'source1', 'title': 'Item 2 from Source 1'},
        ]
    elif 'source2' in url:
        data = [
            {'id': 3, 'source': 'source2', 'title': 'Item 1 from Source 2'},
            {'id': 4, 'source': 'source2', 'title': 'Item 2 from Source 2'},
            {'id': 5, 'source': 'source2', 'title': 'Item 3 from Source 2'},
        ]
    elif 'source3' in url:
        data = [
            {'id': 6, 'source': 'source3', 'title': 'Item 1 from Source 3'},
        ]
    else:
        data = []
    
    return {
        'data': data,
        'metadata': {
            'source_url': url,
            'total_count': len(data),
            'scraping_method': 'test',
            'confidence': 'high'
        }
    }
'''
    
    config = ExecutionConfig(timeout_seconds=30)
    executor = DynamicScriptExecutor(config)
    
    # Test URLs
    test_urls = [
        'https://example.com/source1',
        'https://example.com/source2',
        'https://example.com/source3',
    ]
    
    print(f"Testing with {len(test_urls)} sources:")
    for i, url in enumerate(test_urls, 1):
        print(f"  {i}. {url}")
    print()
    
    try:
        # Execute against multiple sources
        result = executor.execute_multi_source(
            script_code=script_code,
            target_urls=test_urls
        )
        
        if not result.success:
            print("❌ FAILED: Execution was not successful")
            for error in result.errors:
                print(f"   Error: {error}")
            return False
        
        # Verify all sources were processed
        print("Source Results:")
        for sr in result.source_results:
            status = "✓" if sr.success else "✗"
            print(f"  {status} {sr.source_url}: {sr.record_count} records")
        
        # Expected: 2 + 3 + 1 = 6 total records
        expected_total = 6
        actual_total = len(result.data)
        
        print(f"\nData Aggregation:")
        print(f"  Expected total records: {expected_total}")
        print(f"  Actual total records: {actual_total}")
        
        if actual_total != expected_total:
            print(f"\n❌ FAILED: Expected {expected_total} records but got {actual_total}")
            print("\nReceived data:")
            for record in result.data:
                print(f"  - {record}")
            return False
        
        # Verify data from all sources is present
        sources_in_data = set(record.get('source') for record in result.data)
        expected_sources = {'source1', 'source2', 'source3'}
        
        print(f"\nSources in aggregated data: {sources_in_data}")
        print(f"Expected sources: {expected_sources}")
        
        if sources_in_data != expected_sources:
            print(f"\n❌ FAILED: Not all sources present in data")
            print(f"   Missing: {expected_sources - sources_in_data}")
            return False
        
        # Verify metadata
        print(f"\nMetadata:")
        print(f"  Total count: {result.metadata.total_count}")
        print(f"  Source URLs: {len(result.metadata.target_urls)}")
        print(f"  Execution time: {result.execution_time_ms}ms")
        
        print("\n✅ SUCCESS: All sources aggregated correctly!")
        print(f"   - All {len(test_urls)} sources were processed")
        print(f"   - All {expected_total} records were aggregated")
        print(f"   - Data from all sources is present")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_vs_multi_source():
    """Compare single-source vs multi-source execution."""
    print("\n" + "=" * 70)
    print("TEST: Single vs Multi-Source Execution")
    print("=" * 70 + "\n")
    
    script_code = '''
def scrape_data(url: str = None):
    """Return test data."""
    data = [{'url': url, 'item': 'test'}]
    return {
        'data': data,
        'metadata': {
            'source_url': url,
            'total_count': len(data),
            'scraping_method': 'test',
            'confidence': 'high'
        }
    }
'''
    
    config = ExecutionConfig(timeout_seconds=30)
    executor = DynamicScriptExecutor(config)
    
    # Test 1: Single source
    print("Test 1: Single source execution")
    result_single = executor.execute_code(
        script_code=script_code,
        target_url='https://example.com/single'
    )
    print(f"  Records: {len(result_single.data)}")
    print(f"  Source results: {len(result_single.source_results) if result_single.source_results else 0}")
    
    # Test 2: Multi source
    print("\nTest 2: Multi-source execution")
    result_multi = executor.execute_multi_source(
        script_code=script_code,
        target_urls=['https://example.com/multi1', 'https://example.com/multi2']
    )
    print(f"  Records: {len(result_multi.data)}")
    print(f"  Source results: {len(result_multi.source_results)}")
    
    # Verify
    if len(result_multi.data) == 2 and len(result_multi.source_results) == 2:
        print("\n✅ SUCCESS: Multi-source execution works correctly")
        return True
    else:
        print("\n❌ FAILED: Multi-source execution not working as expected")
        return False


def main():
    """Run all multi-source aggregation tests."""
    print("=" * 70)
    print("MULTI-SOURCE AGGREGATION TESTS")
    print("=" * 70)
    print("\nThese tests verify that the executor properly aggregates")
    print("data from ALL provided sources, not just the last one.")
    
    results = []
    results.append(("Multi-source aggregation", test_multi_source_aggregation()))
    results.append(("Single vs multi-source", test_single_vs_multi_source()))
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("   Multi-source execution properly aggregates data from all sources.")
    else:
        print("\n⚠️  Some tests failed.")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
