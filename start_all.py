#!/usr/bin/env python3
"""
Startup script for the AI API Generator.

This script starts both the API server and Streamlit UI in the background.
"""

import subprocess
import sys
import time
import os
import signal
import requests

# Store process IDs for cleanup
processes = []

def cleanup(signum=None, frame=None):
    """Clean up background processes."""
    print("\n🛑 Shutting down services...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            proc.kill()
    print("✅ All services stopped")
    sys.exit(0)

# Register cleanup handler
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def check_env():
    """Check if .env file exists and has API key."""
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found")
        print("💡 Creating .env from .env.example...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ Created .env file")
            print("⚠️  Please edit .env and add your DEEPSEEK_API_KEY")
            print("   Get your API key from: https://platform.deepseek.com/")
            return False
        else:
            print("❌ .env.example not found")
            return False
    
    # Check if API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key or api_key == 'your_deepseek_api_key_here':
        print("⚠️  DEEPSEEK_API_KEY not configured in .env")
        print("💡 Please edit .env and add your API key")
        print("   Get your API key from: https://platform.deepseek.com/")
        return False
    
    print("✅ Configuration found")
    return True

def wait_for_server(url, timeout=30):
    """Wait for server to be ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    """Start all services."""
    print("🚀 Starting AI API Generator")
    print("=" * 60)
    
    # Check environment
    if not check_env():
        print("\n❌ Please configure .env file before starting")
        sys.exit(1)
    
    # Start API server
    print("\n📡 Starting API Server...")
    api_proc = subprocess.Popen(
        [sys.executable, "api_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes.append(api_proc)
    
    # Wait for API server to be ready
    print("   Waiting for API server to start...")
    if wait_for_server("http://localhost:8000/health"):
        print("✅ API Server is running at http://localhost:8000")
    else:
        print("⚠️  API Server may not be ready yet")
    
    # Start Streamlit UI
    print("\n🎨 Starting Streamlit UI...")
    ui_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    processes.append(ui_proc)
    
    # Wait a bit for Streamlit to start
    time.sleep(3)
    print("✅ Streamlit UI is starting at http://localhost:8501")
    
    # Print status
    print("\n" + "=" * 60)
    print("🎉 All services started successfully!")
    print("=" * 60)
    print("\n📍 Access Points:")
    print("   • Streamlit UI:  http://localhost:8501")
    print("   • API Server:    http://localhost:8000")
    print("   • API Docs:      http://localhost:8000/docs")
    print("\n💡 Press Ctrl+C to stop all services")
    print("=" * 60 + "\n")
    
    # Keep running until interrupted
    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            for proc in processes:
                if proc.poll() is not None:
                    print(f"⚠️  Process {proc.pid} exited unexpectedly")
                    cleanup()
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        cleanup()
        sys.exit(1)
