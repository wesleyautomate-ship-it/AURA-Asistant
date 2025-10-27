/**
 * Test script for brochure workflow
 * Run with: npm run test:brochure
 */

if (!import.meta?.env) {
  console.error('⚠️  `import.meta.env` is undefined. Run this script via `npm run test:brochure` so vite-node can provide the Vite environment.');
  process.exit(1);
}

if (import.meta.env.VITE_USE_REAL_API !== 'false') {
  console.log('dY"? Forcing VITE_USE_REAL_API=false for test harness (uses mocked HTTP calls)');
  import.meta.env.VITE_USE_REAL_API = 'false';
}

// Mock fetch globally
global.fetch = async (url, options = {}) => {
  console.log(`🌐 [Mock] ${options.method || 'GET'} ${url}`);
  console.log('   Headers:', options.headers);
  if (options.body) {
    console.log('   Body:', options.body);
  }
  
  // Simulate backend responses based on URL pattern
  if (url.includes('/properties')) {
    if (options.method === 'POST') {
      // Creating property
      return {
        ok: true,
        json: async () => ({
          id: 'prop-123',
          title: '2BR at Orla Residences',
          building: 'Orla Residences',
          beds: 2,
          status: 'draft',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          photos: []
        })
      };
    } else if (url.includes('?')) {
      // Searching properties
      return {
        ok: true,
        json: async () => ([]) // No existing properties
      };
    }
  } else if (url.includes('/brochures')) {
    if (options.method === 'POST') {
      if (url.includes('/render')) {
        // Rendering brochure
        return {
          ok: true,
          json: async () => ({
            download_url: 'http://localhost:8000/api/v1/assets/brochures/brochure-123.pdf'
          })
        };
      } else {
        // Creating brochure draft
        return {
          ok: true,
          json: async () => ({
            id: 'broch-123',
            status: 'draft',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
        };
      }
    }
  }
  
  // Default 404
  throw new Error(`404 Not Found: ${url}`);
};

// Test the intent parser
console.log('🧪 Testing intent parser...');
const { detectIntent } = await import('./src/services/intentParser.ts');

const testPrompt = "Create a brochure for 2BR at Orla Residences on the Palm";
const intent = detectIntent(testPrompt);
console.log('✅ Intent detected:', intent);

// Test the orchestrator
console.log('\n🧪 Testing orchestrator...');
const { orchestrateCommand } = await import('./src/services/orchestrator.ts');

try {
  const result = await orchestrateCommand(testPrompt);
  console.log('✅ Orchestration result:', result);
  
  if (result.workflowResponse) {
    console.log('📋 Workflow data:', result.workflowResponse.data);
  }
  
  if (result.fallbackToStream) {
    console.log('⚠️ Fell back to streaming mode');
  }
} catch (error) {
  console.error('❌ Orchestration failed:', error.message);
  console.error(error.stack);
}
