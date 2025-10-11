/**
 * Aura v2.9.4 Follow-up System Test
 * ==================================
 * 
 * Tests the intelligent follow-up agent functionality
 */

import { generateFollowUp, shouldGenerateFollowUp, generateFollowUpCommand } from '../services/followupAgent';
import type { Request } from '../store/commandStore';

// Mock completed tasks for testing
const mockTasks: Partial<Request>[] = [
  {
    id: 'cma-001',
    title: 'Comprehensive Market Analysis for Dubai Marina',
    type: 'CMA',
    status: 'Complete',
    metadata: {
      location: 'Dubai Marina',
      property_type: 'Apartment',
      price_range: '1M-2M'
    }
  },
  {
    id: 'market-002',
    title: 'Market Report for Downtown Dubai',
    type: 'MARKET_REPORT',
    status: 'Complete',
    metadata: {
      location: 'Downtown Dubai',
      report_type: 'Monthly Analysis'
    }
  },
  {
    id: 'social-003',
    title: 'Social Media Post about CMA Report Success',
    type: 'SOCIAL_POST',
    status: 'Complete',
    metadata: {
      topic: 'CMA Report - Dubai Marina Success Story',
      platform: 'LinkedIn'
    }
  }
];

/**
 * Test follow-up generation for different task types
 */
async function testFollowUpGeneration() {
  console.log('🧪 Testing Follow-up Generation...\n');

  for (const task of mockTasks) {
    console.log(`📋 Testing task: ${task.title}`);
    console.log(`   Type: ${task.type}`);
    
    if (shouldGenerateFollowUp(task as any)) {
      const suggestion = await generateFollowUp(task);
      
      if (suggestion) {
        console.log(`   ✅ Suggestion: ${suggestion.message}`);
        console.log(`   🎯 Intent: ${suggestion.intent}`);
        console.log(`   📊 Confidence: ${suggestion.confidence}`);
        
        const command = generateFollowUpCommand(suggestion);
        console.log(`   🚀 Command: ${command}`);
      } else {
        console.log('   ❌ No suggestion generated');
      }
    } else {
      console.log('   ⏸️ Should not generate follow-up');
    }
    
    console.log('');
  }
}

/**
 * Test follow-up filtering logic
 */
function testFollowUpFiltering() {
  console.log('🧪 Testing Follow-up Filtering Logic...\n');

  // Test cases
  const testCases = [
    { 
      ...mockTasks[0], 
      status: 'Processing',
      description: 'Task still in progress'
    },
    { 
      ...mockTasks[1], 
      relatedTasks: ['follow-001'],
      description: 'Task already has follow-ups'
    },
    { 
      ...mockTasks[2], 
      parentId: 'parent-001',
      description: 'Task is itself a follow-up'
    },
    {
      id: 'unsupported-001',
      title: 'Some unsupported task',
      type: 'UNKNOWN_TYPE',
      status: 'Complete',
      description: 'Unsupported task type'
    }
  ];

  testCases.forEach((testCase, index) => {
    const shouldGenerate = shouldGenerateFollowUp(testCase as any);
    console.log(`Test ${index + 1}: ${testCase.description}`);
    console.log(`   Should generate: ${shouldGenerate ? '✅ Yes' : '❌ No'}`);
    console.log('');
  });
}

/**
 * Run all tests
 */
async function runTests() {
  console.log('🚀 Aura v2.9.4 Follow-up System Tests\n');
  console.log('=====================================\n');
  
  try {
    await testFollowUpGeneration();
    testFollowUpFiltering();
    
    console.log('✅ All tests completed successfully!');
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

// Export for potential use in other test files
export { runTests };

// Run tests if this file is executed directly
if (typeof window !== 'undefined') {
  // Browser environment - can be called from console
  (window as any).testFollowUp = runTests;
} else {
  // Node environment - run immediately
  runTests();
}