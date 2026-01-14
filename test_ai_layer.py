"""
Quick test script for the AI Layer.

This script tests the AI Response Generator with sample form inputs.
Requires DEEPSEEK_API_KEY environment variable to be set.
"""

import sys
from ai_layer import (
    DeepSeekConfig,
    DeepSeekClient,
    AIResponseGenerator,
    ConfigurationError
)


def test_ai_layer():
    """Test the AI layer with sample form input."""
    
    print("🤖 AI Layer Test\n")
    
    # Step 1: Load configuration
    print("1️⃣ Loading configuration...")
    try:
        config = DeepSeekConfig.from_env()
        print(f"   ✅ Configuration loaded")
        print(f"   - Base URL: {config.base_url}")
        print(f"   - Model: {config.model}")
        print(f"   - Temperature: {config.temperature}")
        print(f"   - Max Tokens: {config.max_tokens}")
    except ConfigurationError as e:
        print(f"   ❌ Configuration error: {e}")
        print("\n💡 Tip: Set DEEPSEEK_API_KEY environment variable or create a .env file")
        sys.exit(1)
    
    # Step 2: Initialize client
    print("\n2️⃣ Initializing DeepSeek client...")
    try:
        client = DeepSeekClient(config.api_key, config.base_url)
        print("   ✅ Client initialized")
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")
        sys.exit(1)
    
    # Step 3: Initialize generator
    print("\n3️⃣ Initializing AI Response Generator...")
    generator = AIResponseGenerator(client)
    print("   ✅ Generator initialized")
    
    # Step 4: Test with sample form input
    print("\n4️⃣ Testing with sample form input...")
    sample_input = {
        'data_description': 'Current weather information for major cities',
        'data_source': 'Weather API',
        'desired_fields': 'city\ntemperature\nhumidity\ncondition',
        'response_structure': '',
        'update_frequency': 'Hourly'
    }
    
    print(f"   Input: {sample_input['data_description']}")
    print(f"   Source: {sample_input['data_source']}")
    print(f"   Fields: {sample_input['desired_fields'].replace(chr(10), ', ')}")
    
    try:
        print("\n   🔄 Generating response...")
        response = generator.generate_response(sample_input)
        
        print("\n   ✅ Response generated successfully!")
        print(f"\n📊 Metadata:")
        print(f"   - Model: {response.metadata.model}")
        print(f"   - Tokens: {response.metadata.tokens_used}")
        print(f"   - Time: {response.metadata.generation_time_ms}ms")
        print(f"   - Timestamp: {response.metadata.timestamp}")
        
        print(f"\n📋 Generated JSON:")
        import json
        print(json.dumps(response.data, indent=2))
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n   ❌ Generation failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    test_ai_layer()
