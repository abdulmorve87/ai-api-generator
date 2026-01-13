"""
Quick start script for the AI API Generator Platform demo.
This script sets up everything needed to run the demo.
"""

import subprocess
import sys
import time
import os
import requests
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
            "--trusted-host", "pypi.org", 
            "--trusted-host", "pypi.python.org", 
            "--trusted-host", "files.pythonhosted.org"
        ])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_demo_data():
    """Set up demo data using AI integration."""
    print("\n🔧 Setting up demo data...")
    try:
        # Run the simple test to populate sample data
        subprocess.check_call([sys.executable, "simple_test.py"])
        print("✅ Demo data setup complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup demo data: {e}")
        return False

def start_api_server():
    """Start the API server in background."""
    print("\n🚀 Starting API server...")
    try:
        # Start API server in background
        api_process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running and server responds
        if api_process.poll() is None:
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API server started successfully")
                    print("📖 API Documentation: http://localhost:8000/docs")
                    return api_process
                else:
                    print("❌ API server not responding properly")
                    return None
            except requests.RequestException:
                print("❌ API server not responding")
                return None
        else:
            print("❌ API server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_streamlit():
    """Start the Streamlit application."""
    print("\n🎯 Starting Streamlit application...")
    try:
        subprocess.check_call([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")

def check_prerequisites():
    """Check if all required files exist."""
    required_files = ["app.py", "api_server.py", "database.py", "ai_integration.py", "requirements.txt"]
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure you're running this script from the project root directory")
        return False
    
    return True

def main():
    """Main demo startup function."""
    print("🚀 AI API Generator Platform - Quick Start")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Cannot continue without installing requirements")
        return
    
    # Setup demo data
    if not setup_demo_data():
        print("⚠️ Demo data setup failed, but continuing...")
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Cannot continue without API server")
        return
    
    print("\n🎉 Setup completed! Starting Streamlit interface...")
    print("\n📋 Available URLs:")
    print("  - Streamlit Interface: http://localhost:8501")
    print("  - API Documentation: http://localhost:8000/docs")
    print("  - API Health Check: http://localhost:8000/health")
    print("  - List All APIs: http://localhost:8000/apis")
    print("\n🔧 For Your College AI Team:")
    print("  - Integration Interface: ai_integration.receive_ai_data()")
    print("  - Example Usage: See test_integration.py")
    print("  - Integration Guide: INTEGRATION_GUIDE.md")
    print("\n⚡ Press Ctrl+C to stop all services")
    print("=" * 60)
    
    try:
        # Start Streamlit (this will block until interrupted)
        start_streamlit()
    finally:
        # Cleanup: terminate API server
        if api_process and api_process.poll() is None:
            print("\n🛑 Stopping API server...")
            api_process.terminate()
            api_process.wait()
            print("✅ API server stopped")

if __name__ == "__main__":
    main()