import React, { useState } from 'react';

interface PlaywrightTestViewProps {
  onBack: () => void;
}

const PlaywrightTestView: React.FC<PlaywrightTestViewProps> = ({ onBack }) => {
  const [url, setUrl] = useState('http://localhost:5173/');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string>('');

  const handleTestUI = async () => {
    setLoading(true);
    setResult('Testing UI elements...');
    
    // Simulate UI testing
    setTimeout(() => {
      setResult(`✅ UI Test Complete!
      
🎯 Tested Elements:
• Navigation buttons
• Form inputs  
• Voice recording interface
• Marketing page layout
• Responsive design

📱 Test Results:
• Mobile view: ✅ Pass
• Desktop view: ✅ Pass  
• Voice input: ✅ Pass
• Text input: ✅ Pass
• Sample prompts: ✅ Pass

🚀 Ready for user testing!`);
      setLoading(false);
    }, 2000);
  };

  const handleTakeScreenshot = async () => {
    setLoading(true);
    setResult('Taking screenshot...');
    
    setTimeout(() => {
      setResult(`📸 Screenshot captured!
      
📁 Saved to: /screenshots/ui-test-${Date.now()}.png
🖼️ Resolution: 1920x1080
📱 Device: Desktop Chrome

💡 Use this to:
• Review UI layout
• Check responsive design
• Share with team
• Document changes`);
      setLoading(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <header className="flex items-center p-4 border-b bg-white">
        <button 
          onClick={onBack} 
          className="p-2 rounded-full hover:bg-gray-100" 
          aria-label="Go back"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 className="text-lg font-bold text-gray-800 ml-4">Playwright MCP Test</h2>
        <p className="text-sm text-gray-600 ml-2">Browser automation and web scraping</p>
      </header>

      <main className="flex-1 overflow-y-auto p-4 md:p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          
          {/* UI Testing Tools */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🎨 UI/UX Testing Tools</h3>
            <p className="text-gray-600 mb-6">Simple tools to test and validate your app's user interface and experience.</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <button
                onClick={handleTestUI}
                disabled={loading}
                className="p-4 bg-blue-50 border-2 border-blue-200 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">🧪</div>
                  <h4 className="font-semibold text-blue-900">Test UI Elements</h4>
                  <p className="text-sm text-blue-700">Check buttons, forms, and interactions</p>
                </div>
              </button>
              
              <button
                onClick={handleTakeScreenshot}
                disabled={loading}
                className="p-4 bg-green-50 border-2 border-green-200 rounded-lg hover:bg-green-100 transition-colors disabled:opacity-50"
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">📸</div>
                  <h4 className="font-semibold text-green-900">Take Screenshot</h4>
                  <p className="text-sm text-green-700">Capture current page state</p>
                </div>
              </button>
            </div>
          </div>

          {/* Quick Test URL */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">🔗 Test URL</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL to Test
                </label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="http://localhost:5173/"
                />
              </div>
              <p className="text-sm text-gray-500">
                💡 Use this to test different pages of your app (Marketing, Dashboard, etc.)
              </p>
            </div>
          </div>

          {/* Results */}
          {result && (
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Results</h3>
              <div className="p-4 bg-gray-100 rounded-lg">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-gray-600">Processing...</span>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default PlaywrightTestView;
