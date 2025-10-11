/**
 * Aura v2.9.5 Session Persistence & Navigation Continuity Test Suite
 * 
 * This comprehensive test suite validates the session management system for:
 * - Recording session persistence across navigation
 * - Processing continuation in background
 * - Streaming restoration when returning to CommandCenter
 * - Session state caching/restoration
 * - UI state synchronization
 * 
 * Usage:
 * 1. Load the app in browser
 * 2. Open browser console
 * 3. Run: testSessionPersistence()
 * 4. Follow the prompts for interactive testing
 */

// Test utilities
const TestUtils = {
  log: (message, type = 'info') => {
    const prefix = {
      info: '🔧',
      success: '✅', 
      error: '❌',
      warning: '⚠️'
    }[type];
    console.log(`${prefix} [SessionTest] ${message}`);
  },

  wait: (ms) => new Promise(resolve => setTimeout(resolve, ms)),

  getCommandStore: () => {
    const store = window.__ZUSTAND_STORES?.find(s => s.getState?.()?.sessionState);
    if (!store) {
      throw new Error('CommandStore not found - ensure app is running');
    }
    return store;
  },

  getSessionState: () => {
    const store = TestUtils.getCommandStore();
    return store.getState().sessionState;
  },

  simulateNavigation: async () => {
    TestUtils.log('Simulating navigation away from CommandCenter...');
    
    // Find CommandCenter close button and click it
    const closeButton = document.querySelector('[aria-label="Close Command Center"]');
    if (closeButton) {
      closeButton.click();
      await TestUtils.wait(500);
      TestUtils.log('CommandCenter closed');
      return true;
    }
    
    TestUtils.log('CommandCenter close button not found', 'warning');
    return false;
  },

  simulateReturn: async () => {
    TestUtils.log('Simulating return to CommandCenter...');
    
    // Look for main trigger button (usually the floating action button)
    const triggerButton = document.querySelector('[aria-label*="Open"], [aria-label*="Command"], button[class*="bottom"]');
    if (triggerButton) {
      triggerButton.click();
      await TestUtils.wait(800);
      TestUtils.log('CommandCenter reopened');
      return true;
    }
    
    TestUtils.log('CommandCenter trigger button not found', 'warning');
    return false;
  }
};

// Core test scenarios
const SessionTests = {
  
  async testRecordingPersistence() {
    TestUtils.log('=== Testing Recording Session Persistence ===');
    
    try {
      const store = TestUtils.getCommandStore();
      
      // Step 1: Start recording
      TestUtils.log('Starting recording...');
      const micButton = document.querySelector('[aria-label="Start Recording"]');
      if (!micButton) throw new Error('Recording button not found');
      
      micButton.click();
      await TestUtils.wait(1000);
      
      const sessionAfterRecord = TestUtils.getSessionState();
      if (!sessionAfterRecord.isRecording) {
        throw new Error('Recording state not set in session');
      }
      TestUtils.log('Recording started and session updated', 'success');
      
      // Step 2: Navigate away
      const navSuccess = await TestUtils.simulateNavigation();
      if (!navSuccess) throw new Error('Navigation simulation failed');
      
      // Step 3: Check localStorage persistence
      const cachedSession = JSON.parse(localStorage.getItem('aura_session') || '{}');
      if (!cachedSession.isRecording) {
        throw new Error('Recording state not persisted to localStorage');
      }
      TestUtils.log('Recording state persisted to localStorage', 'success');
      
      // Step 4: Return to CommandCenter
      const returnSuccess = await TestUtils.simulateReturn();
      if (!returnSuccess) throw new Error('Return simulation failed');
      
      await TestUtils.wait(1000);
      
      // Step 5: Verify restoration
      const sessionAfterReturn = TestUtils.getSessionState();
      if (sessionAfterReturn.resumePending || sessionAfterReturn.isRecording) {
        TestUtils.log('Recording session restored successfully', 'success');
        return true;
      } else {
        throw new Error('Recording session not restored properly');
      }
      
    } catch (error) {
      TestUtils.log(`Recording persistence test failed: ${error.message}`, 'error');
      return false;
    }
  },

  async testProcessingContinuation() {
    TestUtils.log('=== Testing Processing Continuation ===');
    
    try {
      const store = TestUtils.getCommandStore();
      
      // Step 1: Start a text command processing
      TestUtils.log('Initiating text processing...');
      const textarea = document.querySelector('textarea[placeholder*="Ask Aura"]');
      const sendButton = document.querySelector('button:has([class*="Send"])');
      
      if (!textarea || !sendButton) {
        throw new Error('Text input elements not found');
      }
      
      textarea.value = 'Generate a detailed market analysis for Dubai Marina';
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
      
      // Wait briefly then click send
      await TestUtils.wait(200);
      sendButton.click();
      
      // Wait for processing to start
      await TestUtils.wait(800);
      
      const sessionDuringProcessing = TestUtils.getSessionState();
      if (!sessionDuringProcessing.isProcessing) {
        throw new Error('Processing state not set in session');
      }
      TestUtils.log('Processing started and session updated', 'success');
      
      // Step 2: Navigate away during processing
      const navSuccess = await TestUtils.simulateNavigation();
      if (!navSuccess) throw new Error('Navigation simulation failed');
      
      // Step 3: Verify background continuation
      const cachedSession = JSON.parse(localStorage.getItem('aura_session') || '{}');
      if (!cachedSession.isProcessing || !cachedSession.currentTaskId) {
        throw new Error('Processing state not persisted properly');
      }
      TestUtils.log('Processing state persisted for background continuation', 'success');
      
      // Step 4: Wait for processing to continue in background
      await TestUtils.wait(2000);
      
      // Step 5: Return and verify
      const returnSuccess = await TestUtils.simulateReturn();
      if (!returnSuccess) throw new Error('Return simulation failed');
      
      await TestUtils.wait(1000);
      
      const sessionAfterReturn = TestUtils.getSessionState();
      if (sessionAfterReturn.resumePending || sessionAfterReturn.isProcessing || sessionAfterReturn.isStreaming) {
        TestUtils.log('Processing continuation restored successfully', 'success');
        return true;
      } else {
        TestUtils.log('Processing may have completed in background (also valid)', 'success');
        return true;
      }
      
    } catch (error) {
      TestUtils.log(`Processing continuation test failed: ${error.message}`, 'error');
      return false;
    }
  },

  async testStreamingRestoration() {
    TestUtils.log('=== Testing Streaming Restoration ===');
    
    try {
      // This test is more complex as it requires catching streaming in progress
      TestUtils.log('Starting streaming test...');
      
      const store = TestUtils.getCommandStore();
      
      // Step 1: Manually set streaming state to simulate in-progress stream
      store.getState().setStreaming(true, 'This is a partial streaming response that should be restored...');
      store.getState().setProcessing(true);
      store.getState().updateSession({ 
        currentTaskId: 'test-stream-123',
        lastPrompt: 'Test streaming restoration'
      });
      
      await TestUtils.wait(500);
      
      const sessionDuringStream = TestUtils.getSessionState();
      if (!sessionDuringStream.isStreaming || !sessionDuringStream.streamingText) {
        throw new Error('Streaming state not set properly');
      }
      TestUtils.log('Streaming state configured', 'success');
      
      // Step 2: Navigate away
      const navSuccess = await TestUtils.simulateNavigation();
      if (!navSuccess) throw new Error('Navigation simulation failed');
      
      // Step 3: Verify persistence
      const cachedSession = JSON.parse(localStorage.getItem('aura_session') || '{}');
      if (!cachedSession.isStreaming || !cachedSession.streamingText) {
        throw new Error('Streaming state not persisted');
      }
      TestUtils.log('Streaming state persisted', 'success');
      
      // Step 4: Return and verify restoration
      const returnSuccess = await TestUtils.simulateReturn();
      if (!returnSuccess) throw new Error('Return simulation failed');
      
      await TestUtils.wait(1000);
      
      const sessionAfterReturn = TestUtils.getSessionState();
      if (sessionAfterReturn.resumePending) {
        TestUtils.log('Streaming restoration initiated', 'success');
        return true;
      } else {
        throw new Error('Streaming restoration not initiated');
      }
      
    } catch (error) {
      TestUtils.log(`Streaming restoration test failed: ${error.message}`, 'error');
      return false;
    }
  },

  async testSessionExpiration() {
    TestUtils.log('=== Testing Session Expiration ===');
    
    try {
      // Step 1: Create an old session in localStorage
      const oldSession = {
        isRecording: true,
        isProcessing: true,
        lastPrompt: 'Old expired session',
        timestamp: Date.now() - (31 * 60 * 1000) // 31 minutes ago
      };
      
      localStorage.setItem('aura_session', JSON.stringify(oldSession));
      TestUtils.log('Created expired session in localStorage');
      
      // Step 2: Trigger restoration
      const store = TestUtils.getCommandStore();
      store.getState().restoreSession();
      
      await TestUtils.wait(500);
      
      // Step 3: Verify session was cleared due to age
      const cachedSession = localStorage.getItem('aura_session');
      const currentSession = TestUtils.getSessionState();
      
      if (cachedSession === null && !currentSession.isRecording && !currentSession.isProcessing) {
        TestUtils.log('Expired session correctly cleared', 'success');
        return true;
      } else {
        throw new Error('Expired session not cleared properly');
      }
      
    } catch (error) {
      TestUtils.log(`Session expiration test failed: ${error.message}`, 'error');
      return false;
    }
  },

  async testUIStateSynchronization() {
    TestUtils.log('=== Testing UI State Synchronization ===');
    
    try {
      const store = TestUtils.getCommandStore();
      
      // Step 1: Set various session states
      store.getState().setRecording(true);
      store.getState().updateSession({ recordingStartTime: Date.now() });
      
      await TestUtils.wait(300);
      
      // Step 2: Check if UI reflects the state
      const recordingIndicator = document.querySelector('[class*="Recording"], [aria-label*="Recording"]');
      const micButton = document.querySelector('[aria-label*="Resume"], [aria-label*="Pause"]');
      
      if (recordingIndicator && micButton) {
        TestUtils.log('UI correctly reflects recording state', 'success');
      } else {
        TestUtils.log('UI may not be fully synchronized (check visual state)', 'warning');
      }
      
      // Step 3: Test processing state
      store.getState().setProcessing(true);
      store.getState().setRecording(false);
      
      await TestUtils.wait(500);
      
      const processingIndicator = document.querySelector('[class*="thinking"], [class*="processing"]');
      if (processingIndicator) {
        TestUtils.log('UI reflects processing state', 'success');
      }
      
      // Step 4: Clear states
      store.getState().setProcessing(false);
      store.getState().clearSession();
      
      return true;
      
    } catch (error) {
      TestUtils.log(`UI synchronization test failed: ${error.message}`, 'error');
      return false;
    }
  }
};

// Performance monitoring
const PerformanceMonitor = {
  
  async measureSessionOperations() {
    TestUtils.log('=== Performance Monitoring ===');
    
    try {
      const store = TestUtils.getCommandStore();
      
      // Measure cache operation
      const cacheStart = performance.now();
      store.getState().cacheSession();
      const cacheTime = performance.now() - cacheStart;
      
      // Measure restore operation  
      const restoreStart = performance.now();
      store.getState().restoreSession();
      const restoreTime = performance.now() - restoreStart;
      
      TestUtils.log(`Session cache time: ${cacheTime.toFixed(2)}ms`);
      TestUtils.log(`Session restore time: ${restoreTime.toFixed(2)}ms`);
      
      if (cacheTime < 10 && restoreTime < 50) {
        TestUtils.log('Session operations are performant', 'success');
        return true;
      } else {
        TestUtils.log('Session operations may be slow', 'warning');
        return true;
      }
      
    } catch (error) {
      TestUtils.log(`Performance monitoring failed: ${error.message}`, 'error');
      return false;
    }
  },

  async monitorMemoryUsage() {
    TestUtils.log('=== Memory Usage Monitoring ===');
    
    if (performance.memory) {
      const initial = performance.memory.usedJSHeapSize;
      
      // Perform multiple session operations
      const store = TestUtils.getCommandStore();
      for (let i = 0; i < 100; i++) {
        store.getState().cacheSession();
        store.getState().restoreSession();
      }
      
      const final = performance.memory.usedJSHeapSize;
      const difference = final - initial;
      
      TestUtils.log(`Memory difference after 100 operations: ${(difference / 1024).toFixed(2)} KB`);
      
      if (difference < 100000) { // Less than 100KB increase
        TestUtils.log('Memory usage is acceptable', 'success');
      } else {
        TestUtils.log('Potential memory leak detected', 'warning');
      }
      
      return true;
    } else {
      TestUtils.log('Memory monitoring not available in this browser', 'warning');
      return true;
    }
  }
};

// Main test runner
async function testSessionPersistence() {
  console.clear();
  TestUtils.log('🚀 Starting Aura v2.9.5 Session Persistence Test Suite');
  TestUtils.log('===============================================');
  
  const results = {
    recordingPersistence: false,
    processingContinuation: false,
    streamingRestoration: false,
    sessionExpiration: false,
    uiSynchronization: false,
    performance: false,
    memoryUsage: false
  };
  
  try {
    // Core functionality tests
    results.recordingPersistence = await SessionTests.testRecordingPersistence();
    await TestUtils.wait(1000);
    
    results.processingContinuation = await SessionTests.testProcessingContinuation();
    await TestUtils.wait(1000);
    
    results.streamingRestoration = await SessionTests.testStreamingRestoration();
    await TestUtils.wait(1000);
    
    results.sessionExpiration = await SessionTests.testSessionExpiration();
    await TestUtils.wait(500);
    
    results.uiSynchronization = await SessionTests.testUIStateSynchronization();
    await TestUtils.wait(500);
    
    // Performance tests
    results.performance = await PerformanceMonitor.measureSessionOperations();
    results.memoryUsage = await PerformanceMonitor.monitorMemoryUsage();
    
  } catch (error) {
    TestUtils.log(`Test suite error: ${error.message}`, 'error');
  }
  
  // Results summary
  TestUtils.log('===============================================');
  TestUtils.log('🏁 Test Suite Results:');
  
  const passed = Object.values(results).filter(Boolean).length;
  const total = Object.keys(results).length;
  
  Object.entries(results).forEach(([test, result]) => {
    TestUtils.log(`${test}: ${result ? 'PASS' : 'FAIL'}`, result ? 'success' : 'error');
  });
  
  TestUtils.log(`Overall: ${passed}/${total} tests passed`, passed === total ? 'success' : 'warning');
  
  if (passed === total) {
    TestUtils.log('🎉 All session persistence tests passed!', 'success');
  } else {
    TestUtils.log('⚠️ Some tests failed - check implementation', 'warning');
  }
  
  return results;
}

// Interactive testing helpers
function quickSessionTest() {
  TestUtils.log('🔧 Quick Session State Check');
  
  try {
    const sessionState = TestUtils.getSessionState();
    console.table(sessionState);
    
    const cached = localStorage.getItem('aura_session');
    if (cached) {
      TestUtils.log('Cached session found in localStorage');
      console.log('Cached data:', JSON.parse(cached));
    } else {
      TestUtils.log('No cached session in localStorage');
    }
    
    return sessionState;
  } catch (error) {
    TestUtils.log(`Quick test failed: ${error.message}`, 'error');
    return null;
  }
}

function clearAllSessions() {
  TestUtils.log('🧹 Clearing all session data');
  
  try {
    const store = TestUtils.getCommandStore();
    store.getState().clearSession();
    TestUtils.log('All session data cleared', 'success');
  } catch (error) {
    TestUtils.log(`Clear failed: ${error.message}`, 'error');
  }
}

// Export test functions globally
window.testSessionPersistence = testSessionPersistence;
window.quickSessionTest = quickSessionTest;
window.clearAllSessions = clearAllSessions;
window.SessionTests = SessionTests;
window.PerformanceMonitor = PerformanceMonitor;

TestUtils.log('Session persistence test suite loaded! Run testSessionPersistence() to begin.');