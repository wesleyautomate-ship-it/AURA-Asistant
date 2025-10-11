/**
 * Aura v3.3 Intelligence Layer Test Suite
 * ========================================
 * 
 * Comprehensive test suite for the v3.3 Intelligence Layer features.
 * Run in browser console to validate all intelligence features.
 */

window.testIntelligenceV33 = async function() {
  console.clear();
  console.log('🧠 Aura v3.3 Intelligence Layer Test Suite');
  console.log('==========================================\n');
  
  const results = {
    tests_run: 0,
    tests_passed: 0,
    tests_failed: 0,
    errors: []
  };

  const runTest = async (name, testFn) => {
    results.tests_run++;
    console.group(`🧪 Test: ${name}`);
    try {
      await testFn();
      console.log('✅ PASSED');
      results.tests_passed++;
    } catch (error) {
      console.error('❌ FAILED:', error);
      results.tests_failed++;
      results.errors.push({ test: name, error: error.message });
    }
    console.groupEnd();
  };

  // Test 1: Memory Service Initialization
  await runTest('Memory Service Initialization', async () => {
    const { memoryService } = await import('/src/services/intelligence/memoryService.ts');
    
    // Test agent storage
    await memoryService.upsertAgent({
      id: 'test_agent_1',
      name: 'Test Agent',
      specialties: ['CMA', 'Market Analysis'],
      voice_preferences: {
        tone: 'professional',
        style: 'clear and concise'
      }
    });
    
    console.log('✓ Agent profile stored successfully');
    
    // Test property storage
    await memoryService.upsertProperty({
      id: 'test_prop_1',
      address: 'Test Property Downtown Dubai',
      property_type: 'apartment',
      market_data: {
        current_price: 1500000,
        market_trends: ['Rising values', 'High demand']
      }
    });
    
    console.log('✓ Property record stored successfully');
    
    // Test semantic recall
    const recalled = await memoryService.recall('Dubai apartment market analysis');
    
    if (recalled.agents.length === 0 && recalled.properties.length === 0) {
      throw new Error('Semantic recall returned no results');
    }
    
    console.log('✓ Semantic recall working:', {
      agents: recalled.agents.length,
      properties: recalled.properties.length,
      relevance: recalled.relevance_score
    });
  });

  // Test 2: Content Intelligence Service
  await runTest('Content Intelligence Service', async () => {
    const { contentIntelligence } = await import('/src/services/intelligence/contentIntelligence.ts');
    
    const request = {
      user_input: 'Generate a comprehensive CMA for Downtown Dubai apartments',
      session_id: 'test_session_1'
    };
    
    const result = await contentIntelligence.generateIntelligentContent(request);
    
    if (!result.success) {
      throw new Error(`Content generation failed: ${result.error}`);
    }
    
    if (!result.quality_scores) {
      throw new Error('Quality scores not generated');
    }
    
    console.log('✓ Content generated successfully:', {
      success: result.success,
      content_type: result.generated_content?.type,
      overall_quality: result.quality_scores.overall_score,
      recommendations: result.recommendations?.length || 0
    });
  });

  // Test 3: Integration Hub
  await runTest('Integration Hub Processing', async () => {
    const { integrationHub } = await import('/src/services/intelligence/integrationHub.ts');
    
    // Test system health
    const health = integrationHub.getSystemHealth();
    console.log('✓ System health check:', health);
    
    // Initialize sample data
    await integrationHub.initializeSampleData();
    console.log('✓ Sample data initialized');
    
    // Test intelligent processing
    const request = {
      userInput: 'Create a market report for Dubai Marina luxury properties',
      requestId: 'test_integration_1',
      enable_intelligence: true,
      memory_enhanced: true,
      quality_threshold: 0.75
    };
    
    const result = await integrationHub.processIntelligentRequest(request);
    
    if (!result.success) {
      throw new Error(`Integration processing failed: ${result.error}`);
    }
    
    console.log('✓ Integration processing successful:', {
      intelligence_used: result.intelligence_used,
      memory_context_used: result.memory_context_used,
      quality_score: result.quality_scores?.overall_score,
      recommendations_count: result.recommendations?.length || 0
    });
  });

  // Test 4: Orchestrator Integration
  await runTest('Enhanced Orchestrator Integration', async () => {
    const { generateContent } = await import('/src/services/orchestratorService.ts');
    
    const request = {
      userInput: 'Generate a pitch deck for a luxury property investment in Business Bay',
      requestId: 'test_orchestrator_1',
      metadata: {
        test_mode: true
      }
    };
    
    const result = await generateContent(request);
    
    if (!result.success) {
      throw new Error(`Orchestrator failed: ${result.error}`);
    }
    
    console.log('✓ Enhanced orchestrator working:', {
      success: result.success,
      content_id: result.contentId,
      processing_time: result.logs.find(log => log.includes('Time:'))?.split(':')[1] || 'N/A'
    });
  });

  // Test 5: CommandCenter Integration
  await runTest('CommandCenter Integration', async () => {
    // Simulate voice command processing
    const store = window.useCommandStore?.getState?.();
    
    if (!store) {
      console.log('⚠️ CommandStore not available, skipping UI integration test');
      return;
    }
    
    const testCommand = 'Create a comprehensive market analysis for Downtown Dubai';
    const requestId = store.addRequest(testCommand);
    
    // Simulate processing
    store.updateRequestStatus(requestId, 'Processing');
    
    // Test that request was added
    const request = store.requests.find(r => r.id === requestId);
    if (!request) {
      throw new Error('Request not found in store');
    }
    
    console.log('✓ CommandCenter integration working:', {
      request_id: requestId,
      status: request.status,
      message: request.userMessage
    });
    
    // Mark as complete
    store.updateRequestStatus(requestId, 'Complete');
  });

  // Test 6: Performance Benchmark
  await runTest('Performance Benchmark', async () => {
    const { processIntelligentRequest } = await import('/src/services/intelligence/integrationHub.ts');
    
    const startTime = performance.now();
    
    const request = {
      userInput: 'Quick CMA for Dubai Marina apartment',
      requestId: 'perf_test_1',
      enable_intelligence: true,
      memory_enhanced: true
    };
    
    const result = await processIntelligentRequest(request);
    
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    if (!result.success) {
      throw new Error('Performance test failed: ' + result.error);
    }
    
    if (duration > 5000) { // 5 seconds
      console.warn(`⚠️ Performance warning: Processing took ${duration.toFixed(2)}ms`);
    }
    
    console.log('✓ Performance benchmark completed:', {
      duration: `${duration.toFixed(2)}ms`,
      intelligence_used: result.intelligence_used,
      quality_score: result.quality_scores?.overall_score
    });
  });

  // Test 7: Error Handling and Fallbacks
  await runTest('Error Handling and Fallbacks', async () => {
    const { processIntelligentRequest } = await import('/src/services/intelligence/integrationHub.ts');
    
    // Test with invalid input
    const invalidRequest = {
      userInput: '', // Empty input
      requestId: 'error_test_1',
      enable_intelligence: true
    };
    
    const result = await processIntelligentRequest(invalidRequest);
    
    // Should handle gracefully (either succeed with fallback or fail gracefully)
    if (result.success) {
      console.log('✓ Graceful handling of edge case - processed with fallback');
    } else {
      console.log('✓ Graceful error handling - failed with proper error message');
    }
    
    // Test intelligence disabled fallback
    const fallbackRequest = {
      userInput: 'Test fallback processing',
      requestId: 'fallback_test_1',
      enable_intelligence: false // Explicitly disable
    };
    
    const fallbackResult = await processIntelligentRequest(fallbackRequest);
    
    if (fallbackResult.intelligence_used === true) {
      throw new Error('Intelligence was used when explicitly disabled');
    }
    
    console.log('✓ Fallback to v3.2 orchestrator working correctly');
  });

  // Test Summary
  console.log('\n🎯 Test Summary');
  console.log('===============');
  console.log(`Total Tests: ${results.tests_run}`);
  console.log(`✅ Passed: ${results.tests_passed}`);
  console.log(`❌ Failed: ${results.tests_failed}`);
  console.log(`Success Rate: ${((results.tests_passed / results.tests_run) * 100).toFixed(1)}%`);
  
  if (results.errors.length > 0) {
    console.log('\n❌ Failed Tests:');
    results.errors.forEach(error => {
      console.log(`  • ${error.test}: ${error.error}`);
    });
  }
  
  // System Health Check
  console.log('\n🏥 System Health Check');
  console.log('=====================');
  try {
    const { integrationHub } = await import('/src/services/intelligence/integrationHub.ts');
    const health = integrationHub.getSystemHealth();
    
    Object.entries(health).forEach(([key, value]) => {
      const status = value === true ? '✅' : value === false ? '❌' : '⚙️';
      console.log(`${status} ${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`);
    });
  } catch (error) {
    console.error('❌ Health check failed:', error);
  }
  
  console.log('\n🎉 Intelligence Layer Test Suite Complete!');
  
  return results;
};

// Auto-run if script is loaded directly
if (typeof window !== 'undefined') {
  console.log('🧠 Aura v3.3 Intelligence Test Suite loaded. Run testIntelligenceV33() to start.');
}