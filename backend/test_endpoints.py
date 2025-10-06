#!/usr/bin/env python3
"""
PropertyPro AI Backend - Endpoint Testing Script
===============================================

This script tests all critical endpoints to ensure the backend is working correctly.

Usage:
    python test_endpoints.py

Prerequisites:
    - Backend server running on localhost:8000
    - Requests library installed (pip install requests)
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {test_name}")
    print(f"{'='*60}")

def print_response(response: requests.Response, show_full_response: bool = False):
    """Print formatted response information"""
    status_emoji = "✅" if response.status_code < 400 else "❌"
    print(f"{status_emoji} Status: {response.status_code}")
    print(f"📦 Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    try:
        data = response.json()
        if show_full_response:
            print(f"📄 Response:\n{json.dumps(data, indent=2)}")
        else:
            # Show abbreviated response
            if isinstance(data, dict):
                if 'status' in data:
                    print(f"🏷️  Status: {data['status']}")
                if 'user' in data:
                    print(f"👤 User: {data['user'].get('name', 'N/A')} ({data['user'].get('role', 'N/A')})")
                if 'metrics' in data:
                    print(f"📊 Metrics: {data['metrics']}")
                if len(str(data)) > 500:
                    print(f"📝 Response: {str(data)[:500]}... (truncated)")
                else:
                    print(f"📝 Response: {data}")
            elif isinstance(data, list):
                print(f"📝 Response: List with {len(data)} items")
                if data and len(data) > 0:
                    print(f"   First item: {data[0]}")
            else:
                print(f"📝 Response: {data}")
    except json.JSONDecodeError:
        print(f"📝 Response: {response.text[:200]}...")
    
    print(f"⏱️  Time: {response.elapsed.total_seconds():.3f}s")

def test_health_endpoint():
    """Test the health check endpoint"""
    print_test_header("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print_response(response)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print_test_header("Root Endpoint")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print_response(response)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_auth_login():
    """Test the authentication login endpoint"""
    print_test_header("Authentication - Login")
    try:
        login_data = {
            "username": "admin@propertypro.ai",
            "password": "Admin123!"
        }
        response = requests.post(
            f"{API_BASE}/auth/login", 
            json=login_data,
            timeout=5
        )
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print(f"🎫 Access Token: {data['access_token'][:20]}...")
                return True
        return False
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_properties_endpoint():
    """Test the properties endpoints"""
    print_test_header("Properties - List All")
    try:
        response = requests.get(f"{API_BASE}/properties", timeout=5)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"📊 Found {len(data)} properties")
                return True
        return False
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_clients_endpoint():
    """Test the clients endpoints"""
    print_test_header("Clients - List All")
    try:
        response = requests.get(f"{API_BASE}/clients", timeout=5)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"📊 Found {len(data)} clients")
                return True
        return False
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_command_center():
    """Test the command center endpoint"""
    print_test_header("Command Center - Dashboard")
    try:
        response = requests.get(f"{API_BASE}/command-center", timeout=10)
        print_response(response, show_full_response=True)
        
        if response.status_code == 200:
            data = response.json()
            if "metrics" in data and "recent" in data:
                print(f"📊 Dashboard data loaded successfully")
                return True
        return False
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_api_docs():
    """Test API documentation endpoints"""
    print_test_header("API Documentation")
    try:
        # Test OpenAPI JSON
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        docs_working = response.status_code == 200
        
        print(f"📚 OpenAPI JSON: {'✅' if docs_working else '❌'} ({response.status_code})")
        
        # Test Swagger UI (just check if it's accessible)
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        swagger_working = response.status_code == 200
        
        print(f"📖 Swagger UI: {'✅' if swagger_working else '❌'} ({response.status_code})")
        
        return docs_working and swagger_working
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def run_all_tests():
    """Run all endpoint tests"""
    print("🏠 PropertyPro AI Backend - Endpoint Testing")
    print("=" * 60)
    print(f"🎯 Target: {BASE_URL}")
    print(f"🕐 Started at: {requests.utils.datetime.datetime.now()}")
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("Authentication", test_auth_login),
        ("Properties API", test_properties_endpoint),
        ("Clients API", test_clients_endpoint),
        ("Command Center", test_command_center),
        ("API Documentation", test_api_docs),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print_test_header("Test Summary")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the backend configuration.")
        return False

def main():
    """Main function"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()