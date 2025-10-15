#!/usr/bin/env python3

"""
Intelligence Generation Endpoint Test
=====================================

Tests the /api/v1/intelligence/generate endpoint with real Gemini API integration.
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8000"
TEST_PROMPTS = [
    {
        "user_input": "Generate a comprehensive CMA report for a 2-bedroom apartment in Dubai Marina",
        "content_type": "CMA_REPORT",
        "description": "CMA Report Generation"
    },
    {
        "user_input": "Create a social media post for a luxury villa in Palm Jumeirah with marina views",
        "content_type": "SOCIAL_POST", 
        "description": "Social Media Content"
    },
    {
        "user_input": "Write a 2-line property description for a modern apartment",
        "content_type": "PROPERTY_DESCRIPTION",
        "description": "Simple Property Description"
    }
]

def test_intelligence_endpoint():
    """Test the intelligence generation endpoint"""
    
    print("🧪 Testing Intelligence Generation Endpoint")
    print("=" * 50)
    
    for i, test_case in enumerate(TEST_PROMPTS, 1):
        print(f"\n📋 Test {i}: {test_case['description']}")
        print("-" * 30)
        
        # Prepare request
        payload = {
            "user_input": test_case["user_input"],
            "content_type": test_case.get("content_type"),
            "priority": "NORMAL",
            "memory_enhanced": True,
            "context": {
                "test_mode": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        print(f"📤 Request: {test_case['user_input'][:60]}...")
        
        try:
            # Send generation request
            start_time = time.time()
            response = requests.post(
                f"{BACKEND_URL}/api/v1/intelligence/generate",
                json=payload,
                timeout=30
            )
            
            request_time = time.time() - start_time
            print(f"⏱️ Request time: {request_time:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                task_id = result.get("task_id")
                
                print(f"✅ Task submitted: {task_id}")
                print(f"📊 Status: {result.get('status')}")
                print(f"⌛ Estimated duration: {result.get('estimated_duration_ms', 0)}ms")
                
                # Poll task status
                print("🔄 Polling task status...")
                max_polls = 30
                poll_count = 0
                
                while poll_count < max_polls:
                    time.sleep(2)
                    poll_count += 1
                    
                    try:
                        status_response = requests.get(
                            f"{BACKEND_URL}/api/v1/intelligence/status/{task_id}",
                            timeout=10
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            task_status = status_data.get("status")
                            progress = status_data.get("progress", 0)
                            current_step = status_data.get("current_step", "")
                            
                            print(f"📈 Progress: {progress}% - {current_step}")
                            
                            if task_status == "completed":
                                print(f"🎉 Task completed successfully!")
                                
                                # Try to get the generated content
                                if "content_id" in status_data:
                                    content_id = status_data["content_id"]
                                    print(f"📄 Content ID: {content_id}")
                                    
                                    try:
                                        content_response = requests.get(
                                            f"{BACKEND_URL}/api/v1/intelligence/content/{content_id}",
                                            timeout=10
                                        )
                                        
                                        if content_response.status_code == 200:
                                            content_data = content_response.json()
                                            content = content_data.get("content", {})
                                            
                                            print(f"📑 Title: {content.get('title', 'N/A')}")
                                            print(f"🏷️ Content Type: {content.get('content_type', 'N/A')}")
                                            print(f"⭐ Quality Score: {content.get('quality_scores', {}).get('overall_score', 'N/A')}")
                                            
                                            # Show a snippet of the narrative
                                            narrative = content.get("generated_content", {}).get("narrative", "")
                                            if narrative:
                                                snippet = narrative[:200] + "..." if len(narrative) > 200 else narrative
                                                print(f"📝 Content preview: {snippet}")
                                        else:
                                            print(f"⚠️ Could not retrieve content: {content_response.status_code}")
                                    
                                    except requests.RequestException as e:
                                        print(f"⚠️ Error retrieving content: {e}")
                                
                                break
                                
                            elif task_status == "failed":
                                error_msg = status_data.get("error_message", "Unknown error")
                                print(f"❌ Task failed: {error_msg}")
                                break
                                
                        else:
                            print(f"⚠️ Status check failed: {status_response.status_code}")
                            break
                            
                    except requests.RequestException as e:
                        print(f"⚠️ Status check error: {e}")
                        break
                
                if poll_count >= max_polls:
                    print(f"⏰ Task polling timeout after {max_polls} attempts")
            
            else:
                print(f"❌ Request failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"💥 Error: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"💥 Raw error: {response.text}")
        
        except requests.RequestException as e:
            print(f"🚨 Network error: {e}")
        
        print("\n" + "="*30)
    
    print("\n✅ Intelligence endpoint testing complete!")

def test_health_check():
    """Test the intelligence health endpoint"""
    print("🏥 Testing Intelligence Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/intelligence/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Service healthy: {health_data.get('service')}")
            print(f"📦 Version: {health_data.get('version')}")
            print(f"🔧 Mock mode: {health_data.get('mock_mode')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"🚨 Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Intelligence API Tests")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"📅 Test started: {datetime.utcnow().isoformat()}")
    
    # First check if the backend is healthy
    if test_health_check():
        print("\n")
        test_intelligence_endpoint()
    else:
        print("❌ Backend health check failed - aborting tests")
        print("💡 Make sure the backend is running on port 8000")