/**
 * Aura v2.9.6 Contextual Follow-Up Behavior Test Suite
 * ====================================================
 * 
 * Tests the contextual, ephemeral, and event-driven Smart Follow-Up system
 * 
 * Usage: Run in browser console while Aura is running
 */

(function() {
    console.log('✨ Aura v2.9.6 Contextual Follow-Up Behavior Test');
    console.log('=================================================');

    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    async function testContextualFollowUp() {
        console.log('\n🎯 Testing Contextual Follow-Up Behavior...\n');

        // Get store reference
        const store = window.useCommandStore?.getState();
        if (!store) {
            console.error('❌ Store not found! Ensure Aura is running.');
            return;
        }

        let testResults = {
            confidenceThreshold: false,
            autoDismiss: false,
            modeRespect: false,
            noClutter: false,
            eventDriven: false,
            visualEnhancements: false,
            crossModeParity: false
        };

        try {
            // Test 1: Confidence Threshold (≥ 0.6)
            console.log('📋 Test 1: Confidence Threshold Filtering');
            
            // Create a mock high-confidence task
            const highConfTaskId = store.addRequest('High Confidence CMA Task', 'CMA', {
                location: 'Dubai Marina',
                confidence: 0.85
            });
            
            // Create a mock low-confidence task
            const lowConfTaskId = store.addRequest('Low Confidence Task', 'GENERIC', {
                location: 'Test Area',
                confidence: 0.4
            });
            
            // Mark both as complete
            store.updateRequestStatus(highConfTaskId, 'Complete');
            store.updateRequestStatus(lowConfTaskId, 'Complete');
            
            console.log('   Created high confidence (0.85) and low confidence (0.4) tasks');
            
            await wait(2000); // Wait for follow-up generation
            
            // Check if only high confidence follow-up is visible
            const followUpCards = document.querySelectorAll('[class*="Smart Follow-up"]');
            if (followUpCards.length === 1) {
                console.log('   ✅ Only high-confidence follow-up displayed');
                testResults.confidenceThreshold = true;
            } else {
                console.log(`   ⚠️ Found ${followUpCards.length} follow-up cards, expected 1`);
            }
            
            await wait(1000);

            // Test 2: Auto-Dismiss Timer (10 seconds)
            console.log('\n📋 Test 2: Auto-Dismiss Timer');
            
            const followUpVisible = document.querySelector('[class*="Smart Follow-up"]');
            if (followUpVisible) {
                console.log('   Follow-up card is visible, waiting for auto-dismiss...');
                const startTime = Date.now();
                
                // Wait and check if it disappears
                await wait(11000); // Wait 11 seconds
                
                const stillVisible = document.querySelector('[class*="Smart Follow-up"]');
                if (!stillVisible) {
                    const elapsed = Date.now() - startTime;
                    console.log(`   ✅ Auto-dismiss worked after ${Math.round(elapsed/1000)} seconds`);
                    testResults.autoDismiss = true;
                } else {
                    console.log('   ⚠️ Follow-up card did not auto-dismiss');
                }
            } else {
                console.log('   ⚠️ No follow-up card found for auto-dismiss test');
            }

            await wait(1000);

            // Test 3: Mode Switching Behavior
            console.log('\n📋 Test 3: Mode Switching Behavior');
            
            // Create another high-confidence task
            const modeTestTaskId = store.addRequest('Mode Test CMA', 'CMA', {
                location: 'Business Bay',
                confidence: 0.9
            });
            store.updateRequestStatus(modeTestTaskId, 'Complete');
            
            await wait(2000);
            
            // Check if follow-up appears
            let followUpAfterComplete = document.querySelector('[class*="Smart Follow-up"]');
            if (followUpAfterComplete) {
                console.log('   Follow-up appeared after task completion');
                
                // Switch mode (simulate clicking mode toggle)
                const modeToggle = document.querySelector('[role="tablist"] button[aria-selected="false"]');
                if (modeToggle) {
                    modeToggle.click();
                    console.log('   Switched modes');
                    
                    await wait(500);
                    
                    // Check if follow-up disappeared
                    const followUpAfterModeSwitch = document.querySelector('[class*="Smart Follow-up"]');
                    if (!followUpAfterModeSwitch) {
                        console.log('   ✅ Follow-up correctly cleared on mode switch');
                        testResults.modeRespect = true;
                    } else {
                        console.log('   ⚠️ Follow-up persisted after mode switch');
                    }
                }
            }

            await wait(1000);

            // Test 4: No UI Clutter - Only Context-Appropriate
            console.log('\n📋 Test 4: No UI Clutter Check');
            
            // Count follow-up cards during idle state
            const idleFollowUps = document.querySelectorAll('[class*="Smart Follow-up"]');
            
            if (idleFollowUps.length === 0) {
                console.log('   ✅ No follow-up clutter during idle state');
                testResults.noClutter = true;
            } else {
                console.log(`   ⚠️ Found ${idleFollowUps.length} follow-up(s) during idle state`);
            }

            await wait(1000);

            // Test 5: Event-Driven Behavior
            console.log('\n📋 Test 5: Event-Driven Behavior');
            
            // Create task and immediately check (should not show before completion)
            const eventTestTaskId = store.addRequest('Event Test Task', 'SOCIAL_POST', {
                topic: 'Real Estate Marketing',
                confidence: 0.8
            });
            
            // Check before completion
            const beforeComplete = document.querySelector('[class*="Smart Follow-up"]');
            
            // Mark as complete
            store.updateRequestStatus(eventTestTaskId, 'Complete');
            
            await wait(1500); // Wait for follow-up generation
            
            // Check after completion
            const afterComplete = document.querySelector('[class*="Smart Follow-up"]');
            
            if (!beforeComplete && afterComplete) {
                console.log('   ✅ Follow-up only appeared after task completion');
                testResults.eventDriven = true;
            } else {
                console.log('   ⚠️ Event-driven behavior not working correctly');
            }

            await wait(1000);

            // Test 6: Visual Enhancements (Color-Coded Confidence)
            console.log('\n📋 Test 6: Visual Enhancement Check');
            
            const confidenceElements = document.querySelectorAll('[class*="match"]');
            let foundColorCoding = false;
            
            confidenceElements.forEach(element => {
                const classes = element.className;
                if (classes.includes('text-green') || classes.includes('text-yellow') || classes.includes('bg-green') || classes.includes('bg-yellow')) {
                    foundColorCoding = true;
                }
            });
            
            if (foundColorCoding) {
                console.log('   ✅ Color-coded confidence indicators found');
                testResults.visualEnhancements = true;
            } else {
                console.log('   ⚠️ Color-coded confidence indicators not detected');
            }

            // Test 7: Cross-Mode Parity
            console.log('\n📋 Test 7: Cross-Mode Parity');
            
            // Test in both voice and text modes
            const modes = ['Voice', 'Text'];
            let modesWorking = 0;
            
            for (const targetMode of modes) {
                const modeButton = Array.from(document.querySelectorAll('[role="tablist"] button'))
                                 .find(b => b.textContent.includes(targetMode));
                
                if (modeButton) {
                    modeButton.click();
                    await wait(500);
                    
                    // Create a test task
                    const modeTestId = store.addRequest(`${targetMode} Mode Test`, 'CMA', {
                        location: `${targetMode} Test Area`,
                        confidence: 0.75
                    });
                    
                    store.updateRequestStatus(modeTestId, 'Complete');
                    await wait(2000);
                    
                    const followUpInMode = document.querySelector('[class*="Smart Follow-up"]');
                    if (followUpInMode) {
                        console.log(`   ✅ Follow-up works in ${targetMode} mode`);
                        modesWorking++;
                    }
                    
                    await wait(1000);
                }
            }
            
            if (modesWorking === 2) {
                console.log('   ✅ Cross-mode parity confirmed');
                testResults.crossModeParity = true;
            } else {
                console.log(`   ⚠️ Only ${modesWorking}/2 modes working correctly`);
            }

        } catch (error) {
            console.error('❌ Test suite error:', error);
        }

        // Results Summary
        console.log('\n📊 Test Results Summary:');
        console.log('========================');
        
        const testNames = {
            confidenceThreshold: 'Confidence Threshold (≥0.6)',
            autoDismiss: 'Auto-Dismiss (10s)',
            modeRespect: 'Mode Switch Cleanup', 
            noClutter: 'No UI Clutter',
            eventDriven: 'Event-Driven Behavior',
            visualEnhancements: 'Visual Enhancements',
            crossModeParity: 'Cross-Mode Parity'
        };
        
        Object.entries(testResults).forEach(([test, passed]) => {
            const status = passed ? '✅ PASS' : '❌ FAIL';
            console.log(`${status} ${testNames[test]}`);
        });

        const totalPassed = Object.values(testResults).filter(Boolean).length;
        const totalTests = Object.keys(testResults).length;
        
        console.log(`\n🎯 Overall Score: ${totalPassed}/${totalTests} tests passed`);
        
        if (totalPassed === totalTests) {
            console.log('🎉 All contextual follow-up tests PASSED! v2.9.6 is working correctly.');
        } else {
            console.log('⚠️ Some tests failed. Check individual results above.');
        }
        
        return testResults;
    }

    // Manual test scenarios
    function showContextualTestScenarios() {
        console.log('\n📋 Manual Test Scenarios for v2.9.6:');
        console.log('====================================');
        
        const scenarios = [
            '1. Complete a high-quality task → Follow-up should appear after completion',
            '2. Wait 10+ seconds → Follow-up should auto-dismiss',
            '3. Complete task, then switch Voice↔Text → Follow-up should clear',
            '4. Look at confidence indicators → Should see green (≥80%), yellow (≥60%) colors',
            '5. Complete low-confidence task → No follow-up should appear',
            '6. Check during recording/streaming → Follow-up should not appear',
            '7. Dismiss manually → Follow-up should disappear immediately',
            '8. Multiple completions → Only one follow-up visible at a time'
        ];

        scenarios.forEach(scenario => console.log(`   ${scenario}`));
        console.log('\n✅ Test each scenario manually in the UI');
    }

    // Performance monitoring for contextual behavior
    function monitorContextualPerformance() {
        console.log('\n📈 Contextual Follow-Up Performance Monitor:');
        console.log('===========================================');
        
        // Monitor follow-up visibility states
        const interval = setInterval(() => {
            const followUpCount = document.querySelectorAll('[class*="Smart Follow-up"]').length;
            const store = window.useCommandStore?.getState();
            
            if (store) {
                const completedTasks = store.requests.filter(r => r.status === 'Complete').length;
                console.log(`[Monitor] Follow-ups: ${followUpCount}, Completed tasks: ${completedTasks}`);
            }
        }, 5000);
        
        console.log('📊 Monitoring started (every 5 seconds)');
        console.log('💡 Run monitorContextualPerformance.stop() to stop monitoring');
        
        // Return stop function
        monitorContextualPerformance.stop = () => {
            clearInterval(interval);
            console.log('📊 Monitoring stopped');
        };
    }

    // Make functions available globally
    window.testContextualFollowUp = testContextualFollowUp;
    window.showContextualScenarios = showContextualTestScenarios;
    window.monitorContextualPerformance = monitorContextualPerformance;
    
    console.log('\n🚀 Contextual Follow-Up Test Suite loaded!');
    console.log('Commands:');
    console.log('- testContextualFollowUp() - Run comprehensive contextual tests');
    console.log('- showContextualScenarios() - Display manual test scenarios');
    console.log('- monitorContextualPerformance() - Monitor follow-up behavior');

})();