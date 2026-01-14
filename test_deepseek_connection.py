#!/usr/bin/env python3
"""Quick test to verify DeepSeek API connection."""

import os
import sys

# Fix SSL certificate issues
for var in ['SSL_CERT_FILE', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']:
    if var in os.environ:
        print(f"Clearing {var}")
        del os.environ[var]

from dotenv import load_dotenv
load_dotenv()

print("🔍 Testing DeepSeek API Connection...")
print("=" * 60)

# Check API key
api_key = os.getenv('DEEPSEEK_API_KEY')
if not api_key:
    print("❌ DEEPSEEK_API_KEY not found in .env")
    sys.exit(1)

print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")

# Test connection
print("\n📡 Testing API connection...")

try:
    from ai_layer import DeepSeekClient
    
    client = DeepSeekClient(api_key)
    print(f"✅ Client initialized")
    print(f"   Verify setting: {client.session.verify}")
    
    # Try a minimal request
    print("\n🤖 Sending test request (this may take 5-10 seconds)...")
    
    response = client.generate_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello' in JSON: {\"message\": \"Hello\"}"}
        ],
        max_tokens=50,
        temperature=0.1
    )
    
    print(f"✅ SUCCESS! Response received:")
    print(f"   {response[:100]}")
    print("\n🎉 DeepSeek API is working correctly!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n🔍 Troubleshooting:")
    
    error_str = str(e).lower()
    
    if "authentication" in error_str or "401" in error_str:
        print("   • Your API key may be invalid")
        print("   • Get a new key from: https://platform.deepseek.com/")
        print("   • Update DEEPSEEK_API_KEY in .env file")
    elif "timeout" in error_str or "connection" in error_str:
        print("   • Check your internet connection")
        print("   • Try again in a few moments")
        print("   • Check if you can access: https://api.deepseek.com")
    elif "rate limit" in error_str or "429" in error_str:
        print("   • You've exceeded the rate limit")
        print("   • Wait a few minutes and try again")
    elif "ssl" in error_str or "certificate" in error_str:
        print("   • SSL certificate issue detected")
        print("   • Try running: pip install --upgrade certifi")
    else:
        print("   • Unknown error occurred")
        print("   • Full error details above")
    
    import traceback
    print("\n📋 Full traceback:")
    traceback.print_exc()
    sys.exit(1)
