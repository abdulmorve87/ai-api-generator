"""
Test generating records with 10-15 fields.
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_layer import DeepSeekConfig, DeepSeekClient, AIResponseGenerator
import json

def test_10_15_fields():
    """Test generating records with 10-15 fields."""
    
    print("🧪 Testing 10-15 Fields Per Record\n")
    
    # Initialize
    config = DeepSeekConfig.from_env()
    client = DeepSeekClient(config.api_key, config.base_url)
    generator = AIResponseGenerator(client)
    
    # Simple request with fewer records to test field count
    form_input = {
        'data_description': 'Generate 25 user profiles with comprehensive information',
        'data_source': 'User Management System',
        'desired_fields': 'user_id\nfull_name\nemail\nphone\nage\ncity\ncountry',  # 7 fields - should add 3-8 more
        'response_structure': '',
        'update_frequency': 'Daily'
    }
    
    print("📝 Request:")
    print(f"   Description: {form_input['data_description']}")
    print(f"   Specified Fields: 7 (system should add more to reach 10-15)")
    
    print("\n⏳ Generating response...")
    
    try:
        response = generator.generate_response(form_input)
        
        print("\n✅ Response generated successfully!")
        
        # Analyze field count
        if 'data' in response.data and isinstance(response.data['data'], list):
            record_count = len(response.data['data'])
            print(f"\n📊 Dataset Analysis:")
            print(f"   Records: {record_count}")
            
            if record_count > 0:
                first_record = response.data['data'][0]
                field_count = len(first_record.keys())
                print(f"   Fields per record: {field_count}")
                
                if 10 <= field_count <= 15:
                    print(f"   ✅ Perfect! {field_count} fields (target: 10-15)")
                elif field_count < 10:
                    print(f"   ⚠️  Only {field_count} fields (target: 10-15)")
                else:
                    print(f"   ✅ {field_count} fields (more than target)")
                
                print(f"\n📋 Fields in each record:")
                for i, key in enumerate(first_record.keys(), 1):
                    value = first_record[key]
                    display_value = str(value)[:40] + "..." if len(str(value)) > 40 else value
                    print(f"   {i:2d}. {key}: {display_value}")
        
        print(f"\n📊 Metadata:")
        print(f"   Model: {response.metadata.model}")
        print(f"   Tokens: {response.metadata.tokens_used}")
        print(f"   Time: {response.metadata.generation_time_ms}ms")
        
        # Save output
        output_path = os.path.join(os.path.dirname(__file__), 'output_10_15_fields.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(response.data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved to: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"   Type: {type(e).__name__}")

if __name__ == "__main__":
    test_10_15_fields()
