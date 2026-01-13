#!/usr/bin/env python3
"""
Convenience script to run the scraper test from project root.
"""

import subprocess
import sys
import os

def main():
    """Run the scraper test script."""
    
    # Path to the actual test script
    script_path = os.path.join("scraping_layer", "examples", "test_scraper.py")
    
    # Pass all arguments to the actual script
    cmd = [sys.executable, script_path] + sys.argv[1:]
    
    try:
        # Run the script
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ Error: Could not find the test script.")
        print(f"Make sure {script_path} exists.")
        sys.exit(1)

if __name__ == "__main__":
    main()