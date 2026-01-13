"""
Simple test to verify the AI API Generator Platform is working.
"""

import requests
import time

def test_system():
    """Test basic functionality."""
    print("🧪 Testing AI API Generator Platform")
    print("=" * 40)
    
    # Test API Server
    print("\n1. Testing API Server...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Server is running")
        else:
            print("❌ API Server not responding properly")
            return False
    except:
        print("❌ API Server is not running")
        print("   Start it with: python api_server.py")
        return False
    
    # Test AI Integration
    print("\n2. Testing AI Integration...")
    try:
        from ai_integration import ai_integration
        
        test_data = {
            "api_name": "test_api",
            "description": "Test API",
            "data": [{"id": 1, "message": "Hello World"}],
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "message": {"type": "string"}
                }
            }
        }
        
        result = ai_integration.receive_ai_data(test_data)
        if result["status"] == "success":
            print("✅ AI Integration working")
        else:
            print("❌ AI Integration failed")
            
    except Exception as e:
        print(f"❌ AI Integration error: {e}")
    
    print("\n🎉 Basic test completed!")
    print("\n📋 Next Steps:")
    print("1. Run: streamlit run app.py")
    print("2. Visit: http://localhost:8501")
    print("3. Edit ai_bridge.py for your colleague's AI")
    
    return True

if __name__ == "__main__":
    test_system()