#!/usr/bin/env python3
"""
Test script to verify Gemini API connection for AURA RealtorProAI.
Tests basic connectivity and authentication with the Google Generative AI SDK.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

try:
    import google.generativeai as genai
    from google.api_core import exceptions as google_exceptions
    import requests.exceptions
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure google-generativeai is installed in your virtual environment")
    sys.exit(1)


def test_gemini_connection():
    """Test basic Gemini API connection and authentication."""
    
    print("🧪 Testing Gemini API connection for AURA RealtorProAI...")
    print("=" * 50)
    
    # Load API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not found!")
        print("   Make sure it's set in your .env file")
        return False
    
    print(f"✅ API Key loaded: {api_key[:10]}...")
    
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured successfully")
        
        # Initialize the generative model
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Gemini 2.0 Flash model initialized")
        
        # Make a test API call
        print("\n🚀 Making test API call...")
        response = model.generate_content('Hello Gemini from AURA RealtorProAI! Please respond with a brief greeting.')
        
        print("✅ API call successful!")
        print("\n📨 Gemini Response:")
        print("-" * 30)
        print(response.text)
        print("-" * 30)
        
        return True
        
    except google_exceptions.Unauthenticated as e:
        print(f"❌ Authentication error: {e}")
        print("   Check if your GEMINI_API_KEY is valid")
        return False
        
    except google_exceptions.PermissionDenied as e:
        print(f"❌ Permission denied: {e}")
        print("   Your API key may not have the required permissions")
        return False
        
    except google_exceptions.ResourceExhausted as e:
        print(f"❌ Quota exceeded: {e}")
        print("   You may have reached your API usage limit")
        return False
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Network connection error: {e}")
        print("   Check your internet connection")
        return False
        
    except requests.exceptions.Timeout as e:
        print(f"❌ Request timeout: {e}")
        print("   The API request took too long to respond")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        print("   Please check your configuration and try again")
        return False


def main():
    """Main test function."""
    success = test_gemini_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Gemini integration test PASSED!")
        print("   Your AURA RealtorProAI backend is ready for AI features")
    else:
        print("❌ Gemini integration test FAILED!")
        print("   Please resolve the issues above before proceeding")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)