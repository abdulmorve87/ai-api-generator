"""
Test DeepSeek API connection and diagnose issues.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test connection to DeepSeek API."""
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    print("🔍 DeepSeek API Connection Test\n")
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test 1: Basic connectivity
    print("\n1️⃣ Testing basic connectivity to api.deepseek.com...")
    try:
        response = requests.get("https://api.deepseek.com", timeout=10)
        print(f"   ✅ Connected! Status: {response.status_code}")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection failed: {e}")
        print("   💡 This might be a network/firewall issue")
        return
    except requests.exceptions.Timeout:
        print("   ❌ Connection timed out")
        return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 2: API endpoint
    print("\n2️⃣ Testing API endpoint...")
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ API call successful!")
            data = response.json()
            print(f"   Response: {data.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
        elif response.status_code == 401:
            print("   ❌ Authentication failed - Invalid API key")
        elif response.status_code == 429:
            print("   ❌ Rate limit exceeded")
        else:
            print(f"   ❌ API error: {response.text}")
    
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection error: {e}")
        print("\n   Possible causes:")
        print("   - Firewall blocking the connection")
        print("   - VPN/Proxy issues")
        print("   - DNS resolution problems")
        print("   - DeepSeek API might be down")
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out (>30s)")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
    
    print("\n" + "="*50)
    print("💡 Troubleshooting Tips:")
    print("1. Check if you're behind a corporate firewall")
    print("2. Try disabling VPN if you're using one")
    print("3. Check if DeepSeek API is accessible from your region")
    print("4. Verify your API key at https://platform.deepseek.com")
    print("="*50)

if __name__ == "__main__":
    test_connection()
