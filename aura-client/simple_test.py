#!/usr/bin/env python3
"""
Simple test to understand the brochure workflow issue
"""

import asyncio
import aiohttp
import json

async def test_brochure_workflow():
    """Test the complete brochure workflow"""
    
    print("🧪 Testing brochure workflow...")
    
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Test backend health
            print("\n1️⃣ Testing backend health...")
            try:
                async with session.get(f"{base_url.replace('/api/v1', '')}/healthz") as resp:
                    if resp.status == 200:
                        print("✅ Backend is running")
                    else:
                        print(f"❌ Backend health check failed: {resp.status}")
                        return
            except Exception as e:
                print(f"❌ Cannot connect to backend: {e}")
                print("   Make sure backend is running on http://localhost:8000")
                return
            
            # 2. Test property creation
            print("\n2️⃣ Testing property creation...")
            property_data = {
                "title": "2BR at Orla Residences",
                "building": "Orla Residences", 
                "community": "Palm Jumeirah",
                "beds": 2,
                "baths": 2.0,
                "area_sqft": 1650.0,
                "price_aed": 7200000,
                "description": "Test property for brochure workflow",
                "photos": []
            }
            
            try:
                async with session.post(f"{base_url}/properties", json=property_data) as resp:
                    if resp.status == 200:
                        property_result = await resp.json()
                        print(f"✅ Property created: {property_result['id']}")
                        property_id = property_result['id']
                    else:
                        error_text = await resp.text()
                        print(f"❌ Property creation failed: {resp.status}")
                        print(f"   Error: {error_text}")
                        return
            except Exception as e:
                print(f"❌ Property creation error: {e}")
                return
            
            # 3. Test brochure draft creation
            print("\n3️⃣ Testing brochure draft creation...")
            brochure_data = {
                "templateKey": "clean-minimal",
                "property_id": property_id
            }
            
            try:
                async with session.post(f"{base_url}/brochures", json=brochure_data) as resp:
                    if resp.status == 200:
                        brochure_result = await resp.json()
                        print(f"✅ Brochure draft created: {brochure_result['id']}")
                        brochure_id = brochure_result['id']
                    else:
                        error_text = await resp.text()
                        print(f"❌ Brochure creation failed: {resp.status}")
                        print(f"   Error: {error_text}")
                        return
            except Exception as e:
                print(f"❌ Brochure creation error: {e}")
                return
            
            # 4. Test brochure rendering
            print("\n4️⃣ Testing brochure rendering...")
            try:
                async with session.post(f"{base_url}/brochures/{brochure_id}/render") as resp:
                    if resp.status == 200:
                        render_result = await resp.json()
                        print(f"✅ Brochure rendered: {render_result.get('download_url')}")
                    else:
                        error_text = await resp.text()
                        print(f"❌ Brochure rendering failed: {resp.status}")
                        print(f"   Error: {error_text}")
                        return
            except Exception as e:
                print(f"❌ Brochure rendering error: {e}")
                return
                
            print("\n🎉 Complete brochure workflow test passed!")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_brochure_workflow())