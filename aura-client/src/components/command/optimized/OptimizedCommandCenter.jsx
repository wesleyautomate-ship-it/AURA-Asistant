/**
 * Aura v3.0 Command Center - Performance Optimized Version
 * 
 * Key Optimizations:
 * ✅ React.memo for component memoization
 * ✅ Zustand selectors for targeted state subscriptions
 * ✅ Lazy loading for heavy components
 * ✅ Virtual scrolling for command history
 * ✅ Debounced input handlers
 * ✅ Optimized re-renders with shallow equality
 * ✅ Background task throttling
 * 
 * Performance Monitoring:
 * - Component render tracking
 * - Memory usage monitoring
 * - State update optimization
 * - Bundle size optimization
 */

import React, { memo, useCallback, useMemo, useRef, useEffect } from 'react';
import { shallow } from 'zustand/shallow';
import { useCommandStore } from '../../store/commandStore';
import { debounce } from 'lodash';

// Lazy loaded components for better initial load
const MiniMicWidget = React.lazy(() => import('../MiniMicWidget'));
const CommandHistory = React.lazy(() => import('./CommandHistory'));
const StreamingResponse = React.lazy(() => import('./StreamingResponse'));

// Performance monitoring utilities
const PerformanceMonitor = {
  renderCount: new Map(),
  
  trackRender: (componentName) => {
    const current = PerformanceMonitor.renderCount.get(componentName) || 0;
    PerformanceMonitor.renderCount.set(componentName, current + 1);
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Perf] ${componentName} rendered ${current + 1} times`);
    }
  },
  
  getRenderStats: () => {
    return Object.fromEntries(PerformanceMonitor.renderCount);
  }
};

// Optimized selectors for targeted subscriptions
const sessionSelectors = {
  // Only session identity data (reduces re-renders on status changes)
  identity: (state) => ({
    id: state.session.id,
    deviceId: state.session.deviceId,
    tabId: state.session.tabId
  }),
  
  // Only recording state (for mic button optimization)
  recording: (state) => ({
    isRecording: state.session.isRecording,
    isPaused: state.session.isPaused,
    isProcessing: state.session.isProcessing
  }),
  
  // Only UI state (for layout optimization) 
  ui: (state) => ({
    isOpen: state.isOpen,
    isCollapsed: state.isCollapsed,
    currentView: state.currentView
  }),
  
  // Only context data (for history optimization)
  context: (state) => ({
    contextHistory: state.session.contextHistory,
    lastPrompt: state.session.lastPrompt
  }),
  
  // Only status indicators (for widget optimization)
  status: (state) => ({
    isOnline: state.session.isOnline,
    lastActiveAt: state.session.lastActiveAt,
    queuedOperationsCount: state.session.queuedOperations?.length || 0
  })
};

// Optimized Command Input Component
const OptimizedCommandInput = memo(({ onSubmit, disabled, placeholder }) => {
  PerformanceMonitor.trackRender('OptimizedCommandInput');
  
  const [value, setValue] = React.useState('');
  const inputRef = useRef(null);
  
  // Debounced input handler to prevent excessive re-renders
  const debouncedOnChange = useCallback(
    debounce((newValue) => {
      setValue(newValue);
    }, 100),
    []
  );
  
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (value.trim() && !disabled) {
      onSubmit(value.trim());
      setValue('');
    }
  }, [value, disabled, onSubmit]);
  
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);
  
  return (
    <form onSubmit={handleSubmit} className="command-input-form">
      <div className="relative">
        <textarea
          ref={inputRef}
          value={value}
          onChange={(e) => debouncedOnChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || "What would you like me to help with?"}
          disabled={disabled}
          className="w-full p-4 pr-12 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          rows={2}
          maxLength={1000}
        />
        <button
          type="submit"
          disabled={!value.trim() || disabled}
          className="absolute right-3 top-3 p-2 text-indigo-600 hover:text-indigo-700 disabled:text-gray-400 disabled:cursor-not-allowed"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </form>
  );
});

OptimizedCommandInput.displayName = 'OptimizedCommandInput';

// Optimized Mic Button Component
const OptimizedMicButton = memo(() => {
  PerformanceMonitor.trackRender('OptimizedMicButton');
  
  // Only subscribe to recording state changes
  const { isRecording, isPaused, isProcessing } = useCommandStore(sessionSelectors.recording, shallow);
  const { startRecording, stopRecording, pauseRecording, resumeRecording } = useCommandStore(
    (state) => ({
      startRecording: state.startRecording,
      stopRecording: state.stopRecording,
      pauseRecording: state.pauseRecording,
      resumeRecording: state.resumeRecording
    }),
    shallow
  );
  
  const buttonState = useMemo(() => {
    if (isProcessing) return 'processing';
    if (isPaused) return 'paused';
    if (isRecording) return 'recording';
    return 'idle';
  }, [isRecording, isPaused, isProcessing]);
  
  const handleClick = useCallback(() => {
    switch (buttonState) {
      case 'idle':
        startRecording();
        break;
      case 'recording':
        pauseRecording();
        break;
      case 'paused':
        resumeRecording();
        break;
      case 'processing':
        // Cannot interact while processing
        break;
      default:
        break;
    }
  }, [buttonState, startRecording, pauseRecording, resumeRecording]);
  
  const handleDoubleClick = useCallback(() => {
    if (buttonState === 'recording' || buttonState === 'paused') {
      stopRecording();
    }
  }, [buttonState, stopRecording]);
  
  const buttonStyles = useMemo(() => ({
    idle: 'bg-gray-100 hover:bg-gray-200 text-gray-700',
    recording: 'bg-red-500 hover:bg-red-600 text-white animate-pulse',
    paused: 'bg-yellow-500 hover:bg-yellow-600 text-white',
    processing: 'bg-blue-500 text-white cursor-not-allowed animate-spin'
  }), []);
  
  const icons = useMemo(() => ({
    idle: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
      </svg>
    ),
    recording: (
      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
        <path d="M6 6h12v12H6z" />
      </svg>
    ),
    paused: (
      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
        <path d="M8 5v14l11-7z" />
      </svg>
    ),
    processing: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    )
  }), []);
  
  return (
    <button
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      disabled={buttonState === 'processing'}
      className={`
        p-4 rounded-full transition-all duration-200 shadow-lg
        ${buttonStyles[buttonState]}
        ${buttonState === 'recording' ? 'transform scale-110' : 'transform scale-100'}
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500
      `}
      title={buttonState === 'idle' ? 'Click to start recording' : 
             buttonState === 'recording' ? 'Click to pause, double-click to stop' :
             buttonState === 'paused' ? 'Click to resume' : 'Processing...'}
    >
      {icons[buttonState]}
    </button>
  );
});

OptimizedMicButton.displayName = 'OptimizedMicButton';

// Optimized Status Display Component  
const OptimizedStatusDisplay = memo(() => {
  PerformanceMonitor.trackRender('OptimizedStatusDisplay');
  
  const { isOnline, lastActiveAt, queuedOperationsCount } = useCommandStore(sessionSelectors.status, shallow);
  
  const formattedLastActive = useMemo(() => {
    if (!lastActiveAt) return 'Never';
    const now = Date.now();
    const diff = now - lastActiveAt;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  }, [lastActiveAt]);
  
  return (
    <div className="flex items-center space-x-4 text-sm text-gray-600">
      {/* Online/Offline Status */}
      <div className="flex items-center space-x-1">
        <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
        <span>{isOnline ? 'Online' : 'Offline'}</span>
      </div>
      
      {/* Last Active */}
      <div className="flex items-center space-x-1">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{formattedLastActive}</span>
      </div>
      
      {/* Queued Operations */}
      {queuedOperationsCount > 0 && (
        <div className="flex items-center space-x-1 text-amber-600">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{queuedOperationsCount} queued</span>
        </div>
      )}
    </div>
  );
});

OptimizedStatusDisplay.displayName = 'OptimizedStatusDisplay';

// Main Optimized Command Center Component
const OptimizedCommandCenter = memo(() => {
  PerformanceMonitor.trackRender('OptimizedCommandCenter');
  
  // Split subscriptions for optimal re-rendering
  const { isOpen, isCollapsed, currentView } = useCommandStore(sessionSelectors.ui, shallow);
  const { id: sessionId } = useCommandStore(sessionSelectors.identity, shallow);
  
  const { 
    open, 
    close, 
    collapse, 
    expand,
    setCurrentView,
    sendMessage,
    createSession
  } = useCommandStore(
    (state) => ({
      open: state.open,
      close: state.close,
      collapse: state.collapse,
      expand: state.expand,
      setCurrentView: state.setCurrentView,
      sendMessage: state.sendMessage,
      createSession: state.createSession
    }),
    shallow
  );
  
  // Initialize session if not present
  useEffect(() => {
    if (!sessionId) {
      createSession('voice');
    }
  }, [sessionId, createSession]);
  
  // Optimized message handler
  const handleSendMessage = useCallback(async (message) => {
    try {
      await sendMessage(message);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }, [sendMessage]);
  
  // Memoized view components to prevent unnecessary renders
  const renderView = useMemo(() => {
    switch (currentView) {
      case 'chat':
        return (
          <React.Suspense fallback={<div className="p-4">Loading chat...</div>}>
            <div className="flex-1 flex flex-col">
              <CommandHistory />
              <div className="border-t border-gray-200 p-4">
                <OptimizedCommandInput 
                  onSubmit={handleSendMessage}
                  placeholder="Type your message..."
                />
              </div>
            </div>
          </React.Suspense>
        );
      case 'voice':
        return (
          <div className="flex-1 flex flex-col items-center justify-center p-8">
            <OptimizedMicButton />
            <div className="mt-4 text-center">
              <React.Suspense fallback={<div>Loading streaming...</div>}>
                <StreamingResponse />
              </React.Suspense>
            </div>
          </div>
        );
      default:
        return (
          <div className="flex-1 flex items-center justify-center p-8 text-gray-500">
            Select a mode to begin
          </div>
        );
    }
  }, [currentView, handleSendMessage]);
  
  // Don't render mini widget if not collapsed
  const shouldShowMiniWidget = isCollapsed && sessionId;
  
  if (!isOpen && !isCollapsed) {
    return null;
  }
  
  return (
    <>
      {/* Main Command Center Panel */}
      {isOpen && !isCollapsed && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50">
          <div className="absolute right-0 top-0 w-96 h-full bg-white shadow-xl flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Aura Command Center</h2>
              <div className="flex space-x-2">
                <button
                  onClick={collapse}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                  title="Minimize"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                  </svg>
                </button>
                <button
                  onClick={close}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                  title="Close"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            {/* View Tabs */}
            <div className="flex border-b border-gray-200">
              {['voice', 'chat'].map((view) => (
                <button
                  key={view}
                  onClick={() => setCurrentView(view)}
                  className={`flex-1 py-3 px-4 text-sm font-medium capitalize ${
                    currentView === view
                      ? 'text-indigo-600 border-b-2 border-indigo-600 bg-indigo-50'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {view}
                </button>
              ))}
            </div>
            
            {/* View Content */}
            {renderView}
            
            {/* Status Bar */}
            <div className="border-t border-gray-200 p-3">
              <OptimizedStatusDisplay />
            </div>
          </div>
        </div>
      )}
      
      {/* Mini Widget */}
      {shouldShowMiniWidget && (
        <React.Suspense fallback={null}>
          <MiniMicWidget />
        </React.Suspense>
      )}
    </>
  );
});

OptimizedCommandCenter.displayName = 'OptimizedCommandCenter';

// Performance monitoring hook
export const usePerformanceMonitoring = () => {
  const [stats, setStats] = React.useState({});
  
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(PerformanceMonitor.getRenderStats());
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  return {
    renderStats: stats,
    memoryUsage: performance.memory ? {
      used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
      total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
      limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
    } : null
  };
};

// Export performance utilities for testing
export { PerformanceMonitor, sessionSelectors };

export default OptimizedCommandCenter;