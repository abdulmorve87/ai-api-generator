#!/usr/bin/env python3
"""Test SSL certificate configuration."""

import os
import sys

# Clear any problematic SSL environment variables
for var in ['SSL_CERT_FILE', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']:
    if var in os.environ:
        print(f"Clearing {var}: {os.environ[var]}")
        del os.environ[var]

# Now import and test
import certifi
import requests

print(f"Certifi path: {certifi.where()}")
print(f"Certifi exists: {os.path.exists(certifi.where())}")

# Test with DeepSeek client
from ai_layer import DeepSeekConfig, DeepSeekClient

try:
    config = DeepSeekConfig.from_env()
    client = DeepSeekClient(config.api_key)
    print(f"Client verify setting: {client.session.verify}")
    
    # Try a simple request
    print("\nTesting DeepSeek API connection...")
    response = client.generate_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello' in JSON format: {\"message\": \"Hello\"}"}
        ],
        max_tokens=50
    )
    print(f"✅ Success! Response: {response[:100]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
