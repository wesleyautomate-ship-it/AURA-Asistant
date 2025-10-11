/**
 * Aura v3.0 Command Center - Master Integration Component
 * 
 * Complete modernization bringing together all v3.0 features:
 * ✅ Unified Session Management with persistence and context
 * ✅ Mini Mic Widget with floating orb UI
 * ✅ Cross-Tab Coordination with BroadcastChannel sync
 * ✅ Offline Mode & Recovery with IndexedDB buffering
 * ✅ Background Continuity with SSE and Service Worker
 * ✅ Performance Optimizations with React.memo and selectors
 * ✅ Intelligent Task Recovery with startup scanning
 * ✅ Context-Aware AI Continuity with smart memory
 * ✅ Responsive Mobile & Desktop UX with adaptive layouts
 * ✅ Enhanced Navbar Integration with graceful behaviors
 * 
 * This is the main component that should replace the legacy Command Center.
 */

import React, { memo, useEffect, useCallback, Suspense } from 'react';
import { shallow } from 'zustand/shallow';
import { useCommandStore } from '../store/commandStore';

// Core services
import backgroundContinuityService from '../services/backgroundContinuity';
import taskRecoveryService from '../services/taskRecovery';
import aiContinuityService from '../services/aiContinuity';

// UI Components (lazy loaded for performance)
const ResponsiveCommandCenter = React.lazy(() => import('./command/responsive/ResponsiveCommandCenter'));
const NavbarCommandIntegration = React.lazy(() => import('./navbar/NavbarCommandIntegration'));
const OptimizedCommandCenter = React.lazy(() => import('./command/optimized/OptimizedCommandCenter'));

// Component selection based on preferences
const COMPONENT_CONFIG = {
  USE_RESPONSIVE_UI: true, // Use responsive layout by default
  USE_OPTIMIZED_PERFORMANCE: true, // Use performance optimizations
  ENABLE_ALL_SERVICES: true, // Enable all v3.0 services
  FALLBACK_TO_LEGACY: false // Whether to fallback to legacy on errors
};

// Loading fallback component
const CommandCenterLoader = memo(() => (
  <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
    <div className="bg-white p-6 rounded-lg shadow-xl flex items-center space-x-3">
      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
      <span className="text-gray-700">Loading Aura Command Center...</span>
    </div>
  </div>
));

// Error boundary for graceful fallbacks
class CommandCenterErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[AuraV3] Command Center error:', error, errorInfo);
    
    // Report error to monitoring service
    if (window.analytics) {
      window.analytics.track('Command Center Error', {
        error: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack
      });
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md">
            <div className="flex items-center space-x-3 mb-4">
              <div className="text-red-500">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900">Command Center Error</h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              The Command Center encountered an error. Please try refreshing the page.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700"
              >
                Refresh Page
              </button>
              <button
                onClick={() => this.setState({ hasError: false, error: null })}
                className="px-4 py-2 bg-gray-200 text-gray-800 text-sm rounded-lg hover:bg-gray-300"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Service initialization hook
const useAuraServices = () => {
  const [servicesInitialized, setServicesInitialized] = React.useState(false);
  const [initErrors, setInitErrors] = React.useState([]);

  useEffect(() => {
    if (!COMPONENT_CONFIG.ENABLE_ALL_SERVICES || servicesInitialized) return;

    const initializeServices = async () => {
      const errors = [];
      
      try {
        console.log('[AuraV3] Initializing services...');
        
        // Initialize core services in order of dependency
        await backgroundContinuityService.start();
        console.log('[AuraV3] Background continuity service started');
        
        await taskRecoveryService.initialize();
        console.log('[AuraV3] Task recovery service initialized');
        
        await aiContinuityService.initialize();
        console.log('[AuraV3] AI continuity service initialized');
        
        setServicesInitialized(true);
        console.log('[AuraV3] All services initialized successfully');
        
      } catch (error) {
        console.error('[AuraV3] Service initialization error:', error);
        errors.push(error);
        setInitErrors(errors);
        
        // Continue with partial functionality
        setServicesInitialized(true);
      }
    };

    initializeServices();

    // Cleanup on unmount
    return () => {
      if (servicesInitialized) {
        console.log('[AuraV3] Cleaning up services...');
        backgroundContinuityService.stop();
        taskRecoveryService.destroy();
        aiContinuityService.destroy();
      }
    };
  }, [servicesInitialized]);

  return { servicesInitialized, initErrors };
};

// Main Aura v3.0 Command Center component
const AuraCommandCenterV3 = memo(({ 
  useResponsiveUI = COMPONENT_CONFIG.USE_RESPONSIVE_UI,
  enableOptimizations = COMPONENT_CONFIG.USE_OPTIMIZED_PERFORMANCE,
  enableServices = COMPONENT_CONFIG.ENABLE_ALL_SERVICES,
  className = '',
  ...props 
}) => {
  const { servicesInitialized, initErrors } = useAuraServices();
  
  // Command Center state
  const { isOpen, isCollapsed } = useCommandStore(
    state => ({
      isOpen: state.isOpen,
      isCollapsed: state.isCollapsed
    }),
    shallow
  );

  // Don't render anything if not open
  if (!isOpen && !isCollapsed) {
    return null;
  }

  // Wait for services to initialize if enabled
  if (enableServices && !servicesInitialized) {
    return <CommandCenterLoader />;
  }

  // Select the appropriate component based on configuration
  const CommandCenterComponent = useResponsiveUI ? 
    ResponsiveCommandCenter : 
    OptimizedCommandCenter;

  return (
    <CommandCenterErrorBoundary>
      <Suspense fallback={<CommandCenterLoader />}>
        <CommandCenterComponent className={className} {...props} />
        
        {/* Show initialization errors if any */}
        {initErrors.length > 0 && (
          <div className="fixed bottom-4 right-4 z-60 max-w-sm">
            <div className="bg-yellow-100 border border-yellow-300 rounded-lg p-3">
              <div className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-yellow-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-yellow-800">Partial Functionality</p>
                  <p className="text-xs text-yellow-600 mt-1">
                    Some features may be limited due to initialization issues.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </Suspense>
    </CommandCenterErrorBoundary>
  );
});

// Navbar integration component (can be used separately)
const AuraNavbarIntegration = memo((props) => (
  <CommandCenterErrorBoundary>
    <Suspense fallback={
      <div className="flex items-center space-x-2">
        <div className="w-4 h-4 animate-spin rounded-full border-2 border-gray-300 border-t-indigo-600"></div>
        <span className="text-xs text-gray-500">Loading...</span>
      </div>
    }>
      <NavbarCommandIntegration {...props} />
    </Suspense>
  </CommandCenterErrorBoundary>
));

// Hooks for external integration
export const useAuraCommandCenter = () => {
  const store = useCommandStore();
  
  const openCommandCenter = useCallback(() => {
    store.open();
  }, [store]);
  
  const closeCommandCenter = useCallback(() => {
    store.close();
  }, [store]);
  
  const toggleCommandCenter = useCallback(() => {
    if (store.isOpen) {
      store.isCollapsed ? store.expand() : store.collapse();
    } else {
      store.open();
    }
  }, [store]);
  
  const startVoiceCommand = useCallback(async () => {
    try {
      if (!store.isOpen) {
        store.open();
      }
      await store.startRecording();
      return { success: true };
    } catch (error) {
      console.error('[AuraV3] Start voice command failed:', error);
      return { success: false, error: error.message };
    }
  }, [store]);
  
  const sendMessage = useCallback(async (message, options = {}) => {
    try {
      // If recording, stop it first
      if (store.session?.isRecording) {
        await store.stopRecording();
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      // Enhance message with AI continuity if available
      let enhancedMessage = message;
      if (store.aiContinuity?.enhancePrompt && options.useAIContext !== false) {
        enhancedMessage = store.aiContinuity.enhancePrompt(message);
      }
      
      const result = await store.sendMessage(enhancedMessage);
      
      // Add to AI context if available
      if (store.aiContinuity?.addTaskToContext) {
        await store.aiContinuity.addTaskToContext({
          id: `message_${Date.now()}`,
          type: 'send_message',
          data: { message, enhancedMessage },
          result
        });
      }
      
      return { success: true, result };
    } catch (error) {
      console.error('[AuraV3] Send message failed:', error);
      return { success: false, error: error.message };
    }
  }, [store]);
  
  const getStatus = useCallback(() => {
    return {
      isOpen: store.isOpen,
      isCollapsed: store.isCollapsed,
      isRecording: store.session?.isRecording || false,
      isProcessing: store.session?.isProcessing || false,
      isOnline: store.session?.isOnline ?? true,
      hasActiveSession: !!store.session?.id,
      currentView: store.currentView,
      contextItems: store.session?.contextHistory?.length || 0,
      queuedOperations: store.session?.queuedOperations?.length || 0
    };
  }, [store]);
  
  return {
    // Actions
    open: openCommandCenter,
    close: closeCommandCenter,
    toggle: toggleCommandCenter,
    startVoiceCommand,
    sendMessage,
    
    // State
    getStatus,
    
    // Advanced features (if services are available)
    backgroundService: store.backgroundService,
    taskRecovery: store.taskRecovery,
    aiContinuity: store.aiContinuity
  };
};

// Performance monitoring hook
export const useAuraPerformance = () => {
  const [metrics, setMetrics] = React.useState({
    renderCount: 0,
    memoryUsage: null,
    servicesStatus: {},
    lastUpdate: Date.now()
  });
  
  useEffect(() => {
    let renderCount = 0;
    
    const updateMetrics = () => {
      renderCount++;
      
      const newMetrics = {
        renderCount,
        memoryUsage: performance.memory ? {
          used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
          total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024)
        } : null,
        servicesStatus: {
          backgroundContinuity: backgroundContinuityService.getStatus(),
          taskRecovery: taskRecoveryService.getStatus(),
          aiContinuity: aiContinuityService.getStatus()
        },
        lastUpdate: Date.now()
      };
      
      setMetrics(newMetrics);
    };
    
    // Update immediately and then every 10 seconds
    updateMetrics();
    const interval = setInterval(updateMetrics, 10000);
    
    return () => clearInterval(interval);
  }, []);
  
  return metrics;
};

// Display names for dev tools
AuraCommandCenterV3.displayName = 'AuraCommandCenterV3';
AuraNavbarIntegration.displayName = 'AuraNavbarIntegration';
CommandCenterLoader.displayName = 'CommandCenterLoader';

// Export main component and utilities
export default AuraCommandCenterV3;
export { 
  AuraNavbarIntegration,
  CommandCenterLoader,
  CommandCenterErrorBoundary,
  COMPONENT_CONFIG 
};