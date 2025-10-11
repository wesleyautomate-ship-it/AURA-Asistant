/**
 * Mock Transcription Integration Test
 * ==================================
 * 
 * Quick verification that mock transcription is working correctly.
 * Run this in the browser console to test the integration.
 */

import { simulateMockTranscription, getMockPrompt, getRandomPrompt } from '../mocks/transcriptionPrompts';

export const testMockTranscription = async () => {
  console.group('🧪 Mock Transcription Integration Test');
  
  // Test 1: Environment variable check
  const mockMode = import.meta.env.VITE_AURA_MOCK_MODE === 'true';
  console.log('✅ Test 1 - Mock Mode Enabled:', mockMode);
  
  if (!mockMode) {
    console.warn('⚠️  Mock mode is disabled. Set VITE_AURA_MOCK_MODE=true to test.');
    console.groupEnd();
    return;
  }
  
  // Test 2: Mock transcription simulation
  console.log('🎯 Test 2 - Testing simulateMockTranscription...');
  const startTime = Date.now();
  
  try {
    const transcription = await simulateMockTranscription();
    const endTime = Date.now();
    const duration = endTime - startTime;
    
    console.log('✅ Transcription Result:', transcription);
    console.log('⏱️  Duration:', `${duration}ms (expected: 1000-1500ms)`);
    
    if (duration >= 1000 && duration <= 2000) {
      console.log('✅ Timing is within expected range');
    } else {
      console.warn('⚠️  Timing outside expected range');
    }
    
  } catch (error) {
    console.error('❌ Test 2 Failed:', error);
  }
  
  // Test 3: Random prompt generation
  console.log('🎯 Test 3 - Testing getRandomPrompt...');
  try {
    const randomPrompt = getRandomPrompt();
    console.log('✅ Random Prompt:', randomPrompt);
    console.log('📝 Content Type:', randomPrompt.contentType);
    console.log('🏷️  Mock Type:', randomPrompt.mockType);
  } catch (error) {
    console.error('❌ Test 3 Failed:', error);
  }
  
  // Test 4: Specific prompt retrieval
  console.log('🎯 Test 4 - Testing getMockPrompt...');
  try {
    const specificPrompt = getMockPrompt('cma_request');
    console.log('✅ Specific Prompt (CMA):', specificPrompt.text);
    
    const fallbackPrompt = getMockPrompt('nonexistent');
    console.log('✅ Fallback Prompt:', fallbackPrompt.text);
  } catch (error) {
    console.error('❌ Test 4 Failed:', error);
  }
  
  // Test 5: Integration with legacy API
  console.log('🎯 Test 5 - Testing legacy API integration...');
  try {
    const { transcribeAudio } = await import('../services/api');
    const mockBlob = new Blob(['test'], { type: 'audio/webm' });
    
    const legacyResult = await transcribeAudio(mockBlob);
    console.log('✅ Legacy API Result:', legacyResult);
  } catch (error) {
    console.error('❌ Test 5 Failed:', error);
  }
  
  // Test 6: Intelligence API integration
  console.log('🎯 Test 6 - Testing Intelligence API integration...');
  try {
    const { intelligenceApi } = await import('../services/api/intelligenceApi');
    const mockBlob = new Blob(['test'], { type: 'audio/webm' });
    
    const intelligenceResult = await intelligenceApi.transcribe(mockBlob);
    console.log('✅ Intelligence API Result:', intelligenceResult);
  } catch (error) {
    console.error('❌ Test 6 Failed:', error);
  }
  
  console.log('🎉 Mock Transcription Integration Test Complete!');
  console.groupEnd();
};

// Export for browser console usage
if (typeof window !== 'undefined') {
  (window as any).testMockTranscription = testMockTranscription;
  console.log('🧪 Mock transcription test available: Run testMockTranscription() in console');
}

export default testMockTranscription;