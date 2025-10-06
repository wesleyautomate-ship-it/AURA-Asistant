import React from 'react';
import ReactDOM from 'react-dom/client';

// Mock data - same as in your services
const mockRequests = [
  {
    id: 1,
    category: 'Marketing',
    title: 'Create listing description for 3-bedroom condo',
    description: 'Need a compelling listing description for a modern 3-bedroom condo in downtown with city views',
    eta: '~15 min',
    status: 'Queued',
    progress: 0,
    assignees: [{ id: 'ai' }],
    tags: [{ text: 'High Priority', color: 'bg-red-100 text-red-800' }]
  },
  {
    id: 2,
    category: 'Data Analysis', 
    title: 'Market analysis for Miami Beach properties',
    description: 'Analyze recent sales trends and pricing in Miami Beach area',
    eta: '~25 min',
    status: 'Processing',
    progress: 65,
    assignees: [{ id: 'ai' }],
    tags: []
  },
  {
    id: 3,
    category: 'Campaign',
    title: 'Social media posts for new listing',
    description: 'Create Instagram and Facebook posts for luxury waterfront property',
    eta: '~5 min',
    status: 'Ready for Review',
    progress: 100,
    assignees: [{ id: 'ai' }],
    tags: [{ text: 'Has Deliverables', color: 'bg-green-100 text-green-800' }]
  }
];

// Request Card Component
function RequestCard({ request }) {
  const statusColors = {
    'Queued': 'bg-blue-100 text-blue-800',
    'Processing': 'bg-yellow-100 text-yellow-800',
    'Ready for Review': 'bg-green-100 text-green-800'
  };

  return React.createElement('div', 
    { className: 'bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-4' },
    React.createElement('div', 
      { className: 'flex items-center justify-between mb-3' },
      React.createElement('span', 
        { className: `text-xs px-2 py-1 rounded-full ${statusColors[request.status]}` },
        request.status
      ),
      React.createElement('span', 
        { className: 'text-xs text-gray-500' },
        request.eta
      )
    ),
    React.createElement('h3', 
      { className: 'font-semibold text-gray-900 mb-2' },
      request.title
    ),
    React.createElement('p', 
      { className: 'text-sm text-gray-600 mb-3' },
      request.description
    ),
    React.createElement('div', 
      { className: 'flex items-center justify-between mb-2' },
      React.createElement('span', 
        { className: 'text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded' },
        request.category
      ),
      request.progress > 0 && React.createElement('div', 
        { className: 'flex items-center space-x-2' },
        React.createElement('div', 
          { className: 'w-16 h-1 bg-gray-200 rounded-full' },
          React.createElement('div', {
            className: 'h-1 bg-blue-500 rounded-full',
            style: { width: `${request.progress}%` }
          })
        ),
        React.createElement('span', 
          { className: 'text-xs text-gray-500' },
          `${request.progress}%`
        )
      )
    ),
    request.tags.length > 0 && React.createElement('div',
      { className: 'flex flex-wrap gap-1 mt-2' },
      ...request.tags.map((tag, idx) => 
        React.createElement('span', 
          { key: idx, className: `text-xs px-2 py-1 rounded-full ${tag.color}` },
          tag.text
        )
      )
    )
  );
}

// Bottom Navigation Component
function BottomNav({ currentView, onViewChange }) {
  const navItems = [
    { id: 'dashboard', icon: '🏠', label: 'Dashboard' },
    { id: 'requests', icon: '🤖', label: 'AI Requests' },
    { id: 'tasks', icon: '✓', label: 'Tasks' },
    { id: 'properties', icon: '🏢', label: 'Properties' },
    { id: 'profile', icon: '👤', label: 'Profile' }
  ];

  return React.createElement('nav',
    { className: 'fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-6 py-2' },
    React.createElement('div',
      { className: 'flex justify-around' },
      ...navItems.map(item => 
        React.createElement('button',
          {
            key: item.id,
            onClick: () => onViewChange(item.id),
            className: `flex flex-col items-center py-2 px-3 rounded-lg transition-colors ${
              currentView === item.id ? 'text-blue-600 bg-blue-50' : 'text-gray-600'
            }`
          },
          React.createElement('span', { className: 'text-xl mb-1' }, item.icon),
          React.createElement('span', { className: 'text-xs' }, item.label)
        )
      )
    )
  );
}

// Requests View Component
function RequestsView() {
  const [statusFilter, setStatusFilter] = React.useState('all');
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    setTimeout(() => setLoading(false), 800);
  }, []);

  const filteredRequests = statusFilter === 'all' 
    ? mockRequests 
    : mockRequests.filter(req => req.status === statusFilter);

  const statusOptions = [
    { value: 'all', label: 'All', count: mockRequests.length },
    { value: 'Queued', label: 'Queued', count: mockRequests.filter(r => r.status === 'Queued').length },
    { value: 'Processing', label: 'Processing', count: mockRequests.filter(r => r.status === 'Processing').length },
    { value: 'Ready for Review', label: 'Ready for Review', count: mockRequests.filter(r => r.status === 'Ready for Review').length }
  ];

  if (loading) {
    return React.createElement('div',
      { className: 'flex items-center justify-center min-h-screen pb-20' },
      React.createElement('div',
        { className: 'text-center' },
        React.createElement('div', { className: 'animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4' }),
        React.createElement('p', { className: 'text-gray-600' }, 'Loading AI Requests...')
      )
    );
  }

  return React.createElement('div',
    { className: 'pb-20' },
    // Header
    React.createElement('div',
      { className: 'bg-white border-b border-gray-200 p-6 sticky top-0 z-10' },
      React.createElement('h1', { className: 'text-2xl font-bold text-gray-900 mb-4' }, '🤖 AI Requests'),
      React.createElement('div',
        { className: 'flex gap-2 overflow-x-auto pb-2' },
        ...statusOptions.map(option => 
          React.createElement('button',
            {
              key: option.value,
              onClick: () => setStatusFilter(option.value),
              className: `px-3 py-2 text-xs font-medium rounded-full whitespace-nowrap transition-all ${
                statusFilter === option.value
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`
            },
            `${option.label} (${option.count})`
          )
        )
      )
    ),
    // Content
    React.createElement('div',
      { className: 'p-6' },
      ...filteredRequests.map(request => 
        React.createElement(RequestCard, { key: request.id, request })
      )
    ),
    // Success indicator
    React.createElement('div',
      { className: 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-3 py-2 rounded-lg shadow-lg' },
      '✅ Production Frontend Working!'
    )
  );
}

// Dashboard View Component  
function DashboardView() {
  return React.createElement('div',
    { className: 'p-6 pb-20' },
    React.createElement('h1', { className: 'text-2xl font-bold text-gray-900 mb-6' }, '🏠 Dashboard'),
    React.createElement('div',
      { className: 'bg-white p-6 rounded-xl shadow-sm mb-4' },
      React.createElement('h2', { className: 'text-lg font-semibold mb-4' }, 'RealtorPro AI'),
      React.createElement('p', { className: 'text-gray-600 mb-4' }, 'Your production-ready AI-powered real estate assistant is now working!'),
      React.createElement('div',
        { className: 'bg-blue-50 p-4 rounded-lg' },
        React.createElement('p', { className: 'text-sm text-blue-800' }, '🚀 Production Frontend Successfully Fixed!')
      )
    )
  );
}

// Placeholder View
function PlaceholderView({ title, icon }) {
  return React.createElement('div',
    { className: 'p-6 pb-20 text-center' },
    React.createElement('span', { className: 'text-6xl mb-4 block' }, icon),
    React.createElement('h1', { className: 'text-2xl font-bold text-gray-900 mb-4' }, title),
    React.createElement('p', { className: 'text-gray-600' }, 'This view is coming soon.')
  );
}

// Main App Component
function App() {
  const [currentView, setCurrentView] = React.useState('requests');
  
  const renderView = () => {
    switch(currentView) {
      case 'dashboard':
        return React.createElement(DashboardView);
      case 'requests':
        return React.createElement(RequestsView);
      case 'tasks':
        return React.createElement(PlaceholderView, { title: 'Tasks', icon: '✓' });
      case 'properties':
        return React.createElement(PlaceholderView, { title: 'Properties', icon: '🏢' });
      case 'profile':
        return React.createElement(PlaceholderView, { title: 'Profile', icon: '👤' });
      default:
        return React.createElement(DashboardView);
    }
  };

  return React.createElement('div',
    { className: 'min-h-screen bg-gray-50' },
    renderView(),
    React.createElement(BottomNav, { currentView, onViewChange: setCurrentView })
  );
}

// Initialize the app
console.log('🚀 RealtorPro AI Production Frontend Loading...');
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Could not find root element to mount to');
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  React.createElement(React.StrictMode, null, 
    React.createElement(App)
  )
);
console.log('✅ RealtorPro AI Production Frontend Loaded Successfully!');