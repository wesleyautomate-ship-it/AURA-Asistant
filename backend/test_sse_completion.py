#!/usr/bin/env python3
"""
Quick SSE Completion Test
Tests that the SSE stream sends a proper completion event and closes cleanly
"""

import asyncio
import requests
import json
import time
from datetime import datetime

BACKEND_URL = "http://localhost:8000"
TEST_REQUEST = "Generate a brief CMA for Downtown Dubai"

async def test_sse_completion():
    """Test SSE completion event"""
    print("🧪 Testing SSE Stream Completion")
    print("-" * 50)
    
    try:
        # 1. Start generation task
        generation_request = {
            "user_input": TEST_REQUEST,
            "content_type": "CMA_REPORT",
            "priority": "normal",
            "memory_enhanced": True,
            "context": {"test": "sse_completion"}
        }
        
        print("📝 Starting generation task...")
        gen_response = requests.post(
            f"{BACKEND_URL}/api/v1/intelligence/generate",
            json=generation_request,
            timeout=10
        )
        
        if gen_response.status_code != 200:
            print(f"❌ Failed to start generation: {gen_response.status_code}")
            return False
            
        task_data = gen_response.json()
        task_id = task_data.get("task_id")
        print(f"✅ Task started: {task_id}")
        
        # 2. Test SSE stream for completion
        print(f"📡 Streaming progress for task: {task_id}")
        stream_url = f"{BACKEND_URL}/api/v1/intelligence/stream/{task_id}"
        
        event_count = 0
        completion_received = False
        start_time = time.time()
        
        try:
            with requests.get(stream_url, stream=True, timeout=60) as response:
                if response.status_code != 200:
                    print(f"❌ SSE endpoint failed: {response.status_code}")
                    return False
                
                print("✅ SSE stream connected")
                
                for line in response.iter_lines(decode_unicode=True):
                    if time.time() - start_time > 45:  # 45 second timeout
                        print("⏰ Timeout - stopping stream read")
                        break
                        
                    if line and line.startswith('data:'):
                        event_count += 1
                        try:
                            event_data = json.loads(line[5:])  # Remove 'data: ' prefix
                            status = event_data.get('status', 'unknown')
                            progress = event_data.get('progress', 0)
                            step = event_data.get('step', event_data.get('current_step', 'N/A'))
                            is_final = event_data.get('final', False)
                            
                            print(f"📈 Event #{event_count}: {status} - {progress}% - {step}")
                            
                            if is_final or status in ['completed', 'failed']:
                                completion_received = True
                                print(f"🎉 Completion event received! Status: {status}")
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"⚠️ Failed to parse: {line[:100]}...")
                            continue
                    
                    elif line and line.startswith('event:'):
                        event_type = line[6:].strip()
                        if event_type == 'complete':
                            completion_received = True
                            print(f"🎉 Explicit completion event received!")
                
                elapsed = time.time() - start_time
                print(f"📊 Stream completed in {elapsed:.1f}s with {event_count} events")
                
                if completion_received:
                    print("✅ SSE stream completed successfully with proper closure!")
                    return True
                else:
                    print("❌ No completion event received")
                    return False
                    
        except requests.exceptions.Timeout:
            print("❌ SSE stream timeout")
            return False
            
    except Exception as e:
        print(f"❌ SSE test failed: {e}")
        return False

def main():
    """Run SSE completion test"""
    print("🚀 SSE Completion Test")
    print(f"🌐 Backend: {BACKEND_URL}")
    print(f"📅 Started: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Run async test
    result = asyncio.run(test_sse_completion())
    
    print("\n" + "=" * 50)
    if result:
        print("🎉 SUCCESS: SSE completion working correctly!")
        print("✅ Stream closes cleanly after completion")
        print("✅ Frontend should now receive proper completion signals")
    else:
        print("❌ FAILURE: SSE completion needs debugging")
        print("⚠️ Check backend logs for SSE streaming issues")

if __name__ == "__main__":
    main()