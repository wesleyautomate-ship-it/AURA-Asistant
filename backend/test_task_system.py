#!/usr/bin/env python3

"""
Quick Task System Verification
==============================
Tests the core task creation and processing without full API server
"""

import asyncio
from app.core.database import get_db
from app.domain.ai.task_orchestrator import AITaskOrchestrator
from app.schemas.intelligence import ContentType

async def test_task_system():
    """Test the task orchestration system"""
    print("🧪 Testing Task Orchestration System")
    print("=" * 40)
    
    # Get database session factory
    def get_db_session():
        return next(get_db())
    
    # Create orchestrator
    orchestrator = AITaskOrchestrator(get_db_session)
    
    print("✅ Task orchestrator created")
    
    # Test intelligence task submission
    try:
        print("📝 Submitting intelligence generation task...")
        
        task_id = await orchestrator.submit_intelligence_task(
            user_input="Generate a 2-line property description for a luxury Dubai apartment",
            content_type=ContentType.PROPERTY_DESCRIPTION,
            user_id=1,
            context={"test": True}
        )
        
        print(f"✅ Task submitted successfully: {task_id}")
        
        # Wait a moment for processing to start
        await asyncio.sleep(3)
        
        # Check task status
        print("📊 Checking task status...")
        task_result = await orchestrator.get_task_status(task_id)
        
        print(f"📈 Task Status: {task_result.status}")
        print(f"📈 Progress: {task_result.progress}%")
        
        if task_result.error_message:
            print(f"⚠️ Error: {task_result.error_message}")
        
        # Wait for completion if still processing
        max_wait = 30
        wait_count = 0
        while task_result.status == "processing" and wait_count < max_wait:
            await asyncio.sleep(2)
            wait_count += 1
            task_result = await orchestrator.get_task_status(task_id)
            print(f"📈 Progress: {task_result.progress}% - Status: {task_result.status}")
        
        if task_result.status == "completed":
            print("🎉 Task completed successfully!")
            if task_result.output_data:
                content_id = task_result.output_data.get("content_id")
                print(f"📄 Generated content ID: {content_id}")
        elif task_result.status == "failed":
            print(f"❌ Task failed: {task_result.error_message}")
        else:
            print(f"⏰ Task still processing after {max_wait*2}s")
            
    except Exception as e:
        print(f"❌ Task system test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Task system verification complete!")

if __name__ == "__main__":
    asyncio.run(test_task_system())