#!/usr/bin/env python3
"""
Test script for DeepSeek AI + API Layer integration.

This script tests the complete flow:
1. AI Layer generates data using DeepSeek
2. Integration layer sends data to API server
3. API server stores and serves the data
"""

import sys
import time
import os
import requests

# Fix SSL certificate issues on Windows (PostgreSQL, Google Cloud SDK interference)
for var in ['SSL_CERT_FILE', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']:
    if var in os.environ:
        del os.environ[var]

from ai_integration import ai_integration
from ai_layer import (
    DeepSeekConfig,
    DeepSeekClient,
    AIResponseGenerator,
    ConfigurationError
)

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_configuration():
    """Test 1: Check configuration."""
    print_section("Test 1: Configuration Check")
    
    try:
        config = DeepSeekConfig.from_env()
        print("✅ Configuration loaded successfully")
        print(f"   - Base URL: {config.base_url}")
        print(f"   - Model: {config.model}")
        print(f"   - Temperature: {config.temperature}")
        print(f"   - Max Tokens: {config.max_tokens}")
        print(f"   - API Key: {'*' * 20}{config.api_key[-4:]}")
        return True
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Solution:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your DeepSeek API key to .env")
        print("   3. Get API key from: https://platform.deepseek.com/")
        return False

def test_api_server():
    """Test 2: Check API server."""
    print_section("Test 2: API Server Check")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            print(f"   - Status: {response.json()}")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        print("\n💡 Solution:")
        print("   Start the API server with: python api_server.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to API server: {e}")
        return False

def test_ai_generation():
    """Test 3: Generate data using AI."""
    print_section("Test 3: AI Generation Test")
    
    try:
        # Initialize AI generator
        config = DeepSeekConfig.from_env()
        client = DeepSeekClient(config.api_key, config.base_url)
        generator = AIResponseGenerator(client)
        
        print("🤖 Generating sample data with DeepSeek AI...")
        print("   (This may take 10-30 seconds)")
        
        # Sample form data
        form_data = {
            "data_description": "Top 10 programming languages with popularity metrics",
            "desired_fields": "name\nrank\npopularity_score\nuse_cases",
            "update_frequency": "monthly",
            "data_source": "Industry surveys and GitHub statistics"
        }
        
        start_time = time.time()
        response = generator.generate_response(form_data)
        elapsed = time.time() - start_time
        
        print(f"✅ AI generation successful!")
        print(f"   - Generation time: {elapsed:.2f}s")
        print(f"   - Model: {response.metadata.model}")
        print(f"   - Tokens used: ~{response.metadata.tokens_used}")
        
        # Show sample of generated data
        data = response.data
        if isinstance(data, dict) and 'data' in data:
            items = data['data']
            print(f"   - Records generated: {len(items)}")
            if items:
                print(f"   - Sample record: {items[0]}")
        
        return response.data
        
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        return None
    except Exception as e:
        print(f"❌ AI generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_integration(ai_data):
    """Test 4: Send data to API server."""
    print_section("Test 4: Integration Test")
    
    if not ai_data:
        print("⏭️  Skipping (no AI data available)")
        return False
    
    try:
        # Extract data items
        data_items = ai_data.get('data', [])
        if isinstance(data_items, dict):
            data_items = [data_items]
        
        # Infer schema
        schema = {"type": "object", "properties": {}}
        if data_items:
            first_item = data_items[0]
            schema_properties = {}
            for key, value in first_item.items():
                if isinstance(value, int):
                    schema_properties[key] = {"type": "integer"}
                elif isinstance(value, float):
                    schema_properties[key] = {"type": "number"}
                elif isinstance(value, bool):
                    schema_properties[key] = {"type": "boolean"}
                elif isinstance(value, list):
                    schema_properties[key] = {"type": "array"}
                else:
                    schema_properties[key] = {"type": "string"}
            schema["properties"] = schema_properties
        
        # Create API payload
        api_payload = {
            "api_name": "test_programming_languages",
            "description": "Top programming languages with metrics (Test API)",
            "data": data_items,
            "schema": schema,
            "data_source": "DeepSeek AI (Test)",
            "update_frequency": "monthly"
        }
        
        print("📤 Sending data to API server...")
        result = ai_integration.receive_ai_data(api_payload)
        
        if result["status"] == "success":
            print("✅ Integration successful!")
            print(f"   - API endpoint: {result.get('api_endpoint')}")
            print(f"   - Records processed: {result.get('records_processed')}")
            return result.get('api_endpoint')
        else:
            print(f"❌ Integration failed: {result.get('message')}")
            return None
            
    except Exception as e:
        print(f"❌ Integration error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_api_access(endpoint):
    """Test 5: Access the generated API."""
    print_section("Test 5: API Access Test")
    
    if not endpoint:
        print("⏭️  Skipping (no endpoint available)")
        return False
    
    try:
        url = f"http://localhost:8000{endpoint}"
        print(f"📥 Fetching data from: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API access successful!")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Records returned: {len(data.get('data', []))}")
            print(f"   - Response time: {data.get('metadata', {}).get('response_time_ms')}ms")
            
            # Show sample record
            if data.get('data'):
                print(f"   - Sample record: {data['data'][0]}")
            
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API access error: {e}")
        return False

def main():
    """Run all integration tests."""
    print("\n" + "🚀 DeepSeek AI + API Layer Integration Test")
    print("=" * 60)
    
    # Track results
    results = {
        "configuration": False,
        "api_server": False,
        "ai_generation": False,
        "integration": False,
        "api_access": False
    }
    
    # Test 1: Configuration
    results["configuration"] = test_configuration()
    if not results["configuration"]:
        print("\n❌ Cannot proceed without valid configuration")
        sys.exit(1)
    
    # Test 2: API Server
    results["api_server"] = test_api_server()
    if not results["api_server"]:
        print("\n⚠️  Some tests will be skipped without API server")
    
    # Test 3: AI Generation
    ai_data = test_ai_generation()
    results["ai_generation"] = ai_data is not None
    
    # Test 4: Integration (only if API server is running)
    endpoint = None
    if results["api_server"] and results["ai_generation"]:
        endpoint = test_integration(ai_data)
        results["integration"] = endpoint is not None
    else:
        print_section("Test 4: Integration Test")
        print("⏭️  Skipping (prerequisites not met)")
    
    # Test 5: API Access (only if integration succeeded)
    if results["integration"]:
        results["api_access"] = test_api_access(endpoint)
    else:
        print_section("Test 5: API Access Test")
        print("⏭️  Skipping (prerequisites not met)")
    
    # Summary
    print_section("Test Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test.replace('_', ' ').title()}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Integration is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Start the Streamlit UI: streamlit run app.py")
        print("   2. Access the UI at: http://localhost:8501")
        print("   3. Try generating your own APIs!")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
