"""
Test generating 25 records with the AI layer.
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_layer import DeepSeekConfig, DeepSeekClient, AIResponseGenerator
import json

def test_25_records():
    """Test generating a response with 25 records."""
    
    print("🧪 Testing AI Layer with 25 Records Request\n")
    
    # Initialize
    config = DeepSeekConfig.from_env()
    client = DeepSeekClient(config.api_key, config.base_url)
    generator = AIResponseGenerator(client)
    
    # Sample input requesting 25 records
    form_input = {
        'data_description': 'Generate 25 sample user profiles with realistic data',
        'data_source': 'User Database',
        'desired_fields': 'id\nname\nemail\nage\ncity\ncountry\nregistration_date',
        'response_structure': '',
        'update_frequency': 'Daily'
    }
    
    print("📝 Request:")
    print(f"   Description: {form_input['data_description']}")
    print(f"   Fields: {form_input['desired_fields'].replace(chr(10), ', ')}")
    
    print("\n⏳ Generating response...")
    
    try:
        response = generator.generate_response(form_input)
        
        print("\n✅ Response generated successfully!")
        print(f"\n📊 Metadata:")
        print(f"   Model: {response.metadata.model}")
        print(f"   Tokens: {response.metadata.tokens_used}")
        print(f"   Time: {response.metadata.generation_time_ms}ms")
        
        # Count records
        if 'data' in response.data and isinstance(response.data['data'], list):
            record_count = len(response.data['data'])
            print(f"\n📋 Records Generated: {record_count}")
            
            if record_count >= 20:
                print("   ✅ Generated 20+ records as requested!")
            else:
                print(f"   ⚠️  Generated fewer than 20 records")
            
            # Show first 2 records as sample
            print("\n📄 Sample Records (first 2):")
            for i, record in enumerate(response.data['data'][:2], 1):
                print(f"\n   Record {i}:")
                for key, value in record.items():
                    print(f"      {key}: {value}")
        
        print(f"\n💾 Full Response saved to: ai_layer/test/output_25_records.json")
        with open(os.path.join(os.path.dirname(__file__), 'output_25_records.json'), 'w', encoding='utf-8') as f:
            json.dump(response.data, f, indent=2, ensure_ascii=False)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"   Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_25_records()
