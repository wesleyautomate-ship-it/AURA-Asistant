#!/usr/bin/env python3
"""
Quick Gemini API test runner for AURA RealtorProAI.
Convenience script to test Gemini connectivity.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the Gemini connection test."""
    test_file = Path(__file__).parent / "tests" / "test_gemini_connection.py"
    
    if not test_file.exists():
        print("❌ Test file not found!")
        print(f"   Expected: {test_file}")
        return 1
    
    print("🚀 Running Gemini API connection test...")
    print()
    
    try:
        result = subprocess.run([sys.executable, str(test_file)], 
                              capture_output=False, 
                              text=True)
        return result.returncode
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())