/**
 * Aura v2.9.4 Follow-up System Integration Test
 * ==============================================
 * 
 * This script can be run in the browser console to test
 * the intelligent follow-up system end-to-end.
 * 
 * Usage: Copy and paste into browser console while Aura is running
 */

(function() {
    console.log('🧪 Aura v2.9.4 Follow-up System Integration Test');
    console.log('=================================================');

    // Helper function to wait
    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // Mock completed tasks for testing
    const mockTasks = [
        {
            id: 'test-cma-001',
            title: 'CMA for Dubai Marina Apartments',
            type: 'CMA',
            status: 'Complete',
            timestamp: Date.now() - 5000,
            metadata: {
                location: 'Dubai Marina',
                property_type: 'Apartment',
                price_range: '1.5M-2M AED'
            }
        },
        {
            id: 'test-market-002', 
            title: 'Market Analysis for Downtown Dubai',
            type: 'MARKET_REPORT',
            status: 'Complete',
            timestamp: Date.now() - 3000,
            metadata: {
                location: 'Downtown Dubai',
                report_type: 'Quarterly Analysis'
            }
        }
    ];

    async function testFollowUpWorkflow() {
        console.log('\n📋 Step 1: Simulating task completion...');
        
        // Get the Zustand store (assuming it's available globally)
        const store = window.useAuraStore || window.useCommandStore;
        
        if (!store) {
            console.error('❌ Store not found! Make sure Aura is running.');
            return;
        }

        try {
            // Add mock tasks to the store
            mockTasks.forEach(task => {
                console.log(`   Adding mock task: ${task.title}`);
                store.getState().addRequest(
                    task.title,
                    task.type,
                    task.metadata
                );
                
                // Mark as complete
                setTimeout(() => {
                    store.getState().updateRequestStatus(task.id, 'Complete');
                    console.log(`   ✅ Task completed: ${task.title}`);
                }, 1000);
            });

            console.log('\n⏳ Step 2: Waiting for follow-up suggestions...');
            await wait(3000);

            console.log('\n🎯 Step 3: Checking if follow-up suggestions appeared...');
            
            // Check if follow-up cards are rendered in the DOM
            const followUpCards = document.querySelectorAll('[data-testid="follow-up-card"]');
            if (followUpCards.length > 0) {
                console.log(`✅ Found ${followUpCards.length} follow-up suggestion(s)!`);
                followUpCards.forEach((card, index) => {
                    console.log(`   Card ${index + 1}: ${card.textContent.substring(0, 50)}...`);
                });
            } else {
                console.log('⚠️ No follow-up cards found in DOM. Checking console logs for generation attempts...');
            }

            console.log('\n🔍 Step 4: Examining store state...');
            const currentRequests = store.getState().requests;
            console.log(`   Total requests in store: ${currentRequests.length}`);
            
            const completedTasks = currentRequests.filter(r => r.status === 'Complete');
            console.log(`   Completed tasks: ${completedTasks.length}`);
            
            completedTasks.forEach(task => {
                console.log(`   - ${task.title} (${task.type})`);
                if (task.relatedTasks?.length > 0) {
                    console.log(`     → Has ${task.relatedTasks.length} linked task(s)`);
                }
            });

            console.log('\n✅ Test completed! Check the UI for follow-up suggestions.');

        } catch (error) {
            console.error('❌ Test failed:', error);
        }
    }

    // Make the test function available globally
    window.testAuraFollowUp = testFollowUpWorkflow;

    console.log('\n🚀 Test function loaded! Run testAuraFollowUp() to start the test.');

})();