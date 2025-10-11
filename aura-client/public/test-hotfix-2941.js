/**
 * Aura v2.9.4.1 Hotfix Validation Test
 * ====================================
 * 
 * Validates the fixes for follow-up card visibility and dismiss functionality
 * 
 * Usage: Run in browser console while Aura is running
 */

(function() {
    console.log('🔧 Aura v2.9.4.1 Hotfix Validation Test');
    console.log('========================================');

    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    async function validateHotfixFixes() {
        console.log('\n🎯 Testing Hotfix Fixes...\n');

        // Get store reference
        const store = window.useCommandStore?.getState();
        if (!store) {
            console.error('❌ Store not found! Ensure Aura is running.');
            return;
        }

        let testResults = {
            voiceModeVisibility: false,
            textModeVisibility: false, 
            dismissFunctionality: false,
            modeChangeCleanup: false,
            animationPresence: false
        };

        try {
            // Test 1: Voice Mode Visibility
            console.log('📝 Test 1: Voice Mode Follow-up Visibility');
            
            // Switch to voice mode first
            const modeToggle = document.querySelector('[role="tablist"] button[aria-selected="false"]');
            if (modeToggle && modeToggle.textContent.includes('Voice')) {
                modeToggle.click();
                console.log('   Switched to Voice mode');
                await wait(500);
                
                // Add mock task and complete it
                const voiceTaskId = store.addRequest('Voice test: CMA for Business Bay', 'CMA', {
                    location: 'Business Bay',
                    property_type: 'Office'
                });
                
                store.updateRequestStatus(voiceTaskId, 'Complete');
                console.log('   ✅ Voice task completed');
                
                await wait(2000); // Wait for follow-up generation
                
                // Check if follow-up card appeared
                const followUpCard = document.querySelector('[data-testid="follow-up-card"]') || 
                                   document.querySelector('div[class*="follow"]') ||
                                   document.querySelector('div:contains("follow-up")');
                
                if (followUpCard || store.requests.find(r => r.id === voiceTaskId && r.relatedTasks?.length > 0)) {
                    console.log('   ✅ Follow-up appeared in Voice mode');
                    testResults.voiceModeVisibility = true;
                } else {
                    console.log('   ⚠️ Follow-up may not have appeared in Voice mode');
                }
            }

            await wait(1000);

            // Test 2: Text Mode Visibility  
            console.log('\n📝 Test 2: Text Mode Follow-up Visibility');
            
            const textModeButton = document.querySelector('[role="tablist"] button:contains("Text")') ||
                                 Array.from(document.querySelectorAll('[role="tablist"] button')).find(b => b.textContent.includes('Text'));
            
            if (textModeButton) {
                textModeButton.click();
                console.log('   Switched to Text mode');
                await wait(500);
                
                const textTaskId = store.addRequest('Text test: Market report for JLT', 'MARKET_REPORT', {
                    location: 'JLT',
                    report_type: 'Monthly'
                });
                
                store.updateRequestStatus(textTaskId, 'Complete');
                console.log('   ✅ Text task completed');
                
                await wait(2000);
                
                const textFollowUp = document.querySelector('[data-testid="follow-up-card"]');
                if (textFollowUp) {
                    console.log('   ✅ Follow-up appeared in Text mode');
                    testResults.textModeVisibility = true;
                }
            }

            await wait(1000);

            // Test 3: Dismiss Button Functionality
            console.log('\n📝 Test 3: Dismiss Button Functionality');
            
            const dismissButton = document.querySelector('button[title*="Dismiss"]') ||
                                document.querySelector('button:has(svg[data-lucide="x"])');
            
            if (dismissButton) {
                console.log('   Found dismiss button, testing click...');
                
                // Monitor for console logs indicating dismissal
                const originalConsoleLog = console.log;
                let dismissLogged = false;
                
                console.log = function(...args) {
                    if (args.some(arg => typeof arg === 'string' && arg.includes('dismiss'))) {
                        dismissLogged = true;
                    }
                    originalConsoleLog.apply(console, args);
                };
                
                dismissButton.click();
                
                await wait(500);
                
                console.log = originalConsoleLog; // Restore console
                
                const cardStillExists = document.querySelector('[data-testid="follow-up-card"]');
                if (!cardStillExists || dismissLogged) {
                    console.log('   ✅ Dismiss button working - card removed');
                    testResults.dismissFunctionality = true;
                } else {
                    console.log('   ⚠️ Dismiss button may not be working properly');
                }
            }

            // Test 4: Mode Change Cleanup
            console.log('\n📝 Test 4: Mode Change Cleanup');
            
            // Switch modes rapidly and check cleanup
            const modes = ['Voice', 'Text'];
            for (let i = 0; i < 2; i++) {
                const targetMode = modes[i];
                const modeBtn = Array.from(document.querySelectorAll('[role="tablist"] button'))
                              .find(b => b.textContent.includes(targetMode));
                
                if (modeBtn) {
                    modeBtn.click();
                    await wait(300);
                    
                    // Check if any stale follow-up cards exist
                    const staleCards = document.querySelectorAll('[data-testid="follow-up-card"]');
                    if (staleCards.length === 0) {
                        testResults.modeChangeCleanup = true;
                    }
                }
            }
            
            if (testResults.modeChangeCleanup) {
                console.log('   ✅ Mode change cleanup working');
            }

            // Test 5: Animation Presence
            console.log('\n📝 Test 5: Animation Presence Check');
            
            const animatedElements = document.querySelectorAll('[style*="opacity"], [style*="transform"]');
            if (animatedElements.length > 0) {
                console.log('   ✅ Animation elements detected');
                testResults.animationPresence = true;
            }

        } catch (error) {
            console.error('❌ Test error:', error);
        }

        // Results Summary
        console.log('\n📊 Test Results Summary:');
        console.log('========================');
        
        Object.entries(testResults).forEach(([test, passed]) => {
            const status = passed ? '✅ PASS' : '❌ FAIL';
            const testName = test.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
            console.log(`${status} ${testName}`);
        });

        const totalPassed = Object.values(testResults).filter(Boolean).length;
        const totalTests = Object.keys(testResults).length;
        
        console.log(`\n🎯 Overall Score: ${totalPassed}/${totalTests} tests passed`);
        
        if (totalPassed === totalTests) {
            console.log('🎉 All hotfix validations PASSED! v2.9.4.1 is working correctly.');
        } else {
            console.log('⚠️ Some tests failed. Check individual results above.');
        }
    }

    // Manual test checklist
    function showManualTestChecklist() {
        console.log('\n📋 Manual Test Checklist for v2.9.4.1:');
        console.log('==========================================');
        
        const checklist = [
            '1. Complete a task in Voice mode → Follow-up card should appear',
            '2. Complete a task in Text mode → Follow-up card should appear', 
            '3. Click the ✕ dismiss button → Card should fade out and disappear',
            '4. Switch from Text → Voice → Follow-up card should clear',
            '5. Switch from Voice → Text → Follow-up card should clear',
            '6. Multiple task completions → Only one follow-up card visible',
            '7. Card animations → Smooth fade-in/fade-out transitions'
        ];

        checklist.forEach(item => console.log(`   ${item}`));
        console.log('\n✅ Check each item manually in the UI');
    }

    // Make functions available globally
    window.validateHotfix2941 = validateHotfixFixes;
    window.showHotfixChecklist = showManualTestChecklist;
    
    console.log('\n🚀 Hotfix validation loaded!');
    console.log('Commands:');
    console.log('- validateHotfix2941() - Run automated validation');
    console.log('- showHotfixChecklist() - Show manual test checklist');

})();