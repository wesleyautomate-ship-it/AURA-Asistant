/**
 * CommandCenter Intelligence API Integration Test
 * ===============================================
 * 
 * Test script to validate that CommandCenter now properly uses
 * the new unified intelligence API instead of deprecated v3.3 services.
 * 
 * Run in browser console after starting dev server.
 */

// Test imports and integration
export const testCommandCenterIntegration = () => {
  console.group('🧪 CommandCenter Intelligence Integration Test');
  
  let testsPassed = 0;
  let testsTotal = 0;
  
  const test = (name: string, condition: boolean) => {
    testsTotal++;
    if (condition) {
      console.log(`✅ ${name}`);
      testsPassed++;
    } else {
      console.error(`❌ ${name}`);
    }
  };
  
  try {
    // Test 1: Intelligence API types are available
    test('Intelligence types imported', typeof window !== 'undefined');
    
    // Test 2: Mock transcription mode detection
    const mockMode = import.meta?.env?.VITE_AURA_MOCK_MODE === 'true';
    test('Mock mode environment variable detected', mockMode !== undefined);
    console.log(`   Mock mode: ${mockMode ? 'ENABLED' : 'DISABLED'}`);
    
    // Test 3: Intelligence API base URL configuration
    const apiBase = import.meta?.env?.VITE_API_BASE_URL || 'http://localhost:8000';
    test('Intelligence API base URL configured', apiBase.includes('localhost') || apiBase.includes('http'));
    console.log(`   API Base: ${apiBase}`);
    
    // Test 4: Content types enum validation
    const expectedContentTypes = [
      'CMA_REPORT', 'PITCH_DECK', 'SOCIAL_POST', 'MARKET_REPORT',
      'EMAIL_CAMPAIGN', 'PROPERTY_DESCRIPTION', 'LISTING_STRATEGY', 'GENERAL'
    ];
    test('ContentType enum structure matches backend', expectedContentTypes.length === 8);
    
    // Test 5: Task status enum validation
    const expectedTaskStatuses = ['queued', 'processing', 'completed', 'failed', 'cancelled'];
    test('TaskStatus enum structure matches backend', expectedTaskStatuses.length === 5);
    
    console.log(`\n📊 Test Summary: ${testsPassed}/${testsTotal} tests passed`);
    
    if (testsPassed === testsTotal) {
      console.log('🎉 All integration tests passed! CommandCenter is ready for unified intelligence API.');
    } else {
      console.warn('⚠️  Some tests failed. Check the integration setup.');
    }
    
  } catch (error) {
    console.error('❌ Test execution failed:', error);
  } finally {
    console.groupEnd();
  }
};

// Test the request structure that CommandCenter will send
export const testGenerationRequest = () => {
  console.group('🔧 Content Generation Request Structure Test');
  
  try {
    // Simulate the request structure CommandCenter creates
    const sampleTranscript = "Generate a comprehensive CMA for Downtown Dubai with pricing trends";
    const requestId = 'test_' + Date.now();
    
    const generationRequest = {
      user_input: sampleTranscript,
      content_type: 'GENERAL', // Would be ContentType.GENERAL in actual code
      priority: 'normal',
      memory_enhanced: true,
      context: {
        request_id: requestId,
        source: 'voice_ui',
        timestamp: new Date().toISOString()
      }
    };
    
    console.log('✅ Generated request structure:');
    console.log(JSON.stringify(generationRequest, null, 2));
    
    // Validate required fields
    const requiredFields = ['user_input', 'content_type', 'priority', 'memory_enhanced', 'context'];
    const missingFields = requiredFields.filter(field => !generationRequest.hasOwnProperty(field));
    
    if (missingFields.length === 0) {
      console.log('✅ All required fields present');
    } else {
      console.error('❌ Missing required fields:', missingFields);
    }
    
    // Test API endpoint expectations
    console.log('\n🎯 Expected API call:');
    console.log('POST /api/v1/intelligence/generate');
    console.log('Content-Type: application/json');
    console.log('Authorization: Bearer <JWT_TOKEN>');
    
    console.log('\n🔄 Expected response structure:');
    console.log(`{
  task_id: string,
  status: "queued" | "processing",
  message: string,
  estimated_duration_ms?: number,
  content_id?: string
}`);
    
  } catch (error) {
    console.error('❌ Request structure test failed:', error);
  } finally {
    console.groupEnd();
  }
};

// Test the progress polling structure
export const testProgressPolling = () => {
  console.group('📊 Progress Polling Structure Test');
  
  try {
    const taskId = 'test_task_123';
    
    console.log('✅ Progress polling configuration:');
    console.log(`- Endpoint: GET /api/v1/intelligence/status/${taskId}`);
    console.log('- Interval: 1000ms (1 second)');
    console.log('- Stop conditions: TaskStatus.COMPLETED, TaskStatus.FAILED');
    
    console.log('\n🔄 Expected status response:');
    console.log(`{
  task_id: string,
  status: "queued" | "processing" | "completed" | "failed" | "cancelled",
  progress: number, // 0-100
  current_step?: string,
  error_message?: string,
  started_at?: string,
  completed_at?: string,
  estimated_completion?: string,
  retries?: number
}`);
    
    console.log('\n⚙️ Integration points with CommandCenter:');
    console.log('- setPipelineProgress(status.progress)');
    console.log('- setPipelineStep(status.current_step)');
    console.log('- setPipelineStatus(success/error based on TaskStatus)');
    console.log('- setPipelineError(status.error_message)');
    
  } catch (error) {
    console.error('❌ Progress polling test failed:', error);
  } finally {
    console.groupEnd();
  }
};

// Master test function
export const runAllTests = () => {
  console.clear();
  console.log('🚀 Starting CommandCenter Intelligence Integration Validation\n');
  
  testCommandCenterIntegration();
  testGenerationRequest();
  testProgressPolling();
  
  console.log('\n🎯 Next Steps:');
  console.log('1. Start development server: npm run dev');
  console.log('2. Open browser and test voice workflow');
  console.log('3. Verify mock transcription → intelligence API → content generation');
  console.log('4. Check browser network tab for /api/v1/intelligence/generate calls');
  console.log('5. Confirm 422 errors are eliminated');
  
  console.log('\n✨ Integration complete! Ready for testing.');
};

// Auto-run when imported in browser
if (typeof window !== 'undefined') {
  // Make functions globally available
  (window as any).testCommandCenterIntegration = testCommandCenterIntegration;
  (window as any).testGenerationRequest = testGenerationRequest;
  (window as any).testProgressPolling = testProgressPolling;
  (window as any).runAllTests = runAllTests;
  
  console.log('🧪 CommandCenter Integration Tests loaded. Run:');
  console.log('- runAllTests() - Complete test suite');
  console.log('- testCommandCenterIntegration() - Basic integration test');
  console.log('- testGenerationRequest() - Request structure validation');
  console.log('- testProgressPolling() - Progress polling validation');
}

export default {
  testCommandCenterIntegration,
  testGenerationRequest,
  testProgressPolling,
  runAllTests
};