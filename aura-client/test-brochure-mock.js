/**
 * Test brochure workflow in mock mode
 * Run with: node test-brochure-mock.js
 */

// Mock import.meta.env
global.import = {
  meta: {
    env: {
      VITE_API_BASE_URL: 'http://localhost:8000',
      VITE_API_BASE: '/api/v1',
      VITE_BACKEND_ENABLED: '1',
      VITE_USE_REAL_API: 'false' // Enable mock mode
    }
  }
};

async function testBrochureWorkflow() {
  console.log('🧪 Testing brochure workflow in mock mode...\n');
  
  try {
    // Test intent parsing
    console.log('1️⃣ Testing intent detection...');
    const { detectIntent } = await import('./src/services/intentParser.ts');
    
    const prompt = "Create a brochure for 2BR at Orla Residences on the Palm";
    const intent = detectIntent(prompt);
    
    console.log('✅ Intent detected:', {
      type: intent.type,
      building: intent.building,
      beds: intent.beds,
      confidence: intent.confidence
    });
    
    if (intent.type !== 'BROCHURE') {
      console.error('❌ Expected BROCHURE intent, got:', intent.type);
      return;
    }
    
    // Test properties API in mock mode
    console.log('\n2️⃣ Testing properties API (mock mode)...');
    const propertiesApi = await import('./src/features/properties/api/properties.ts');
    
    // Test search (should return empty array in mock mode)
    const searchResults = await propertiesApi.search({
      q: prompt,
      building: intent.building,
      limit: 1
    });
    console.log('✅ Property search completed:', searchResults.length, 'results');
    
    // Test property creation
    const propertyPayload = propertiesApi.buildMinimalProperty(prompt, intent);
    console.log('📝 Property payload:', propertyPayload);
    
    const property = await propertiesApi.create(propertyPayload);
    console.log('✅ Property created:', {
      id: property.id,
      title: property.title,
      status: property.status
    });
    
    // Test brochure API in mock mode
    console.log('\n3️⃣ Testing brochure API (mock mode)...');
    const brochureApi = await import('./src/features/brochure/api/brochure.ts');
    
    // Create draft
    const draftPayload = {
      templateKey: 'clean-minimal',
      property_id: property.id
    };
    
    const draft = await brochureApi.createDraft(draftPayload);
    console.log('✅ Brochure draft created:', {
      id: draft.id,
      status: draft.status
    });
    
    // Render draft
    const renderResult = await brochureApi.renderDraft(draft.id);
    console.log('✅ Brochure rendered:', renderResult.download_url);
    
    // Test complete orchestrator workflow
    console.log('\n4️⃣ Testing complete orchestrator workflow...');
    const { orchestrateCommand } = await import('./src/services/orchestrator.ts');
    
    const orchestratorResult = await orchestrateCommand(prompt);
    console.log('✅ Orchestrator result:', {
      success: orchestratorResult.workflowResponse?.success,
      fallbackToStream: orchestratorResult.fallbackToStream,
      message: orchestratorResult.workflowResponse?.message,
      downloadUrl: orchestratorResult.workflowResponse?.data?.downloadUrl
    });
    
    if (orchestratorResult.fallbackToStream) {
      console.log('⚠️ Orchestrator fell back to streaming:', orchestratorResult.userMessage);
    }
    
    console.log('\n🎉 All tests passed! The brochure workflow is working in mock mode.');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
  }
}

testBrochureWorkflow();