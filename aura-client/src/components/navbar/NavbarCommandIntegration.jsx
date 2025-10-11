/**
 * Aura v3.0 Enhanced Navbar Integration
 * 
 * Seamless app-wide integration improvements:
 * ✅ Update navbar interactions to collapse (not stop) Command Center
 * ✅ Implement pause on collapse with resume on reopen
 * ✅ Graceful Send during recording with state preservation
 * ✅ Comprehensive error handling and recovery
 * ✅ Visual status indicators in navbar
 * ✅ Keyboard shortcuts and accessibility
 * 
 * Features:
 * - Smart Command Center state management from navbar
 * - Visual indicators for recording, processing, and error states
 * - Graceful degradation and error recovery
 * - Keyboard shortcuts and accessibility support
 * - Cross-platform navbar behaviors
 * - Session persistence across navigation
 */

import React, { memo, useCallback, useEffect, useState, useRef } from 'react';
import { shallow } from 'zustand/shallow';
import { useCommandStore } from '../../store/commandStore';
import { DeviceUtils } from '../command/responsive/ResponsiveCommandCenter';

// Navbar integration configuration
const NAVBAR_CONFIG = {
  SHORTCUTS: {
    TOGGLE_COMMAND_CENTER: 'mod+shift+a', // Ctrl/Cmd + Shift + A
    VOICE_COMMAND: 'mod+shift+v', // Ctrl/Cmd + Shift + V  
    PAUSE_RESUME: 'mod+shift+p' // Ctrl/Cmd + Shift + P
  },
  VISUAL: {
    PULSE_DURATION: 2000, // ms
    STATUS_FADE_DELAY: 5000, // ms
    ERROR_DISPLAY_DURATION: 8000, // ms
    SUCCESS_DISPLAY_DURATION: 3000 // ms
  },
  BEHAVIOR: {
    PAUSE_ON_COLLAPSE: true,
    RESUME_ON_EXPAND: true,
    PRESERVE_INPUT_ON_ERROR: true,
    AUTO_SAVE_ON_NAVIGATE: true
  }
};

// Status indicator component
const CommandStatusIndicator = memo(({ status, error, className = '' }) => {
  const [showError, setShowError] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    if (error) {
      setShowError(true);
      const timer = setTimeout(() => setShowError(false), NAVBAR_CONFIG.VISUAL.ERROR_DISPLAY_DURATION);
      return () => clearTimeout(timer);
    }
  }, [error]);

  useEffect(() => {
    if (status === 'completed') {
      setShowSuccess(true);
      const timer = setTimeout(() => setShowSuccess(false), NAVBAR_CONFIG.VISUAL.SUCCESS_DISPLAY_DURATION);
      return () => clearTimeout(timer);
    }
  }, [status]);

  const getStatusColor = () => {
    if (showError) return 'text-red-500';
    if (showSuccess) return 'text-green-500';
    
    switch (status) {
      case 'recording': return 'text-red-500 animate-pulse';
      case 'processing': return 'text-blue-500 animate-pulse';
      case 'paused': return 'text-yellow-500';
      case 'connected': return 'text-green-500';
      case 'offline': return 'text-gray-400';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = () => {
    if (showError) return '⚠️';
    if (showSuccess) return '✅';
    
    switch (status) {
      case 'recording': return '🎤';
      case 'processing': return '⚡';
      case 'paused': return '⏸️';
      case 'connected': return '🔗';
      case 'offline': return '📡';
      default: return '🔹';
    }
  };

  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      <span className={`text-sm ${getStatusColor()}`}>
        {getStatusIcon()}
      </span>
      {(showError || showSuccess) && (
        <span className={`text-xs ${getStatusColor()} transition-opacity duration-300`}>
          {showError ? 'Error' : 'Success'}
        </span>
      )}
    </div>
  );
});

// Voice command button component
const VoiceCommandButton = memo(({ 
  isRecording, 
  isProcessing, 
  onStartRecording, 
  onStopRecording, 
  onToggleCommandCenter,
  disabled = false,
  className = ''
}) => {
  const [isLongPress, setIsLongPress] = useState(false);
  const longPressTimer = useRef(null);
  const isMobile = DeviceUtils.isMobile();

  const handleMouseDown = useCallback((e) => {
    if (disabled) return;
    
    e.preventDefault();
    setIsLongPress(false);
    
    longPressTimer.current = setTimeout(() => {
      setIsLongPress(true);
      if (!isRecording) {
        onStartRecording();
      }
    }, 500); // 500ms for long press
  }, [disabled, isRecording, onStartRecording]);

  const handleMouseUp = useCallback((e) => {
    if (disabled) return;
    
    e.preventDefault();
    
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }

    if (isLongPress && isRecording) {
      // End long press recording
      onStopRecording();
      setIsLongPress(false);
    } else if (!isLongPress) {
      // Regular click - toggle command center
      onToggleCommandCenter();
    }
  }, [disabled, isLongPress, isRecording, onStopRecording, onToggleCommandCenter]);

  const handleMouseLeave = useCallback(() => {
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }
  }, []);

  const getButtonStyles = () => {
    const baseStyles = 'relative flex items-center justify-center p-2 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500';
    
    if (disabled) return `${baseStyles} bg-gray-100 text-gray-400 cursor-not-allowed`;
    if (isProcessing) return `${baseStyles} bg-blue-100 text-blue-600 animate-pulse cursor-wait`;
    if (isRecording) return `${baseStyles} bg-red-100 text-red-600 animate-pulse hover:bg-red-200`;
    
    return `${baseStyles} bg-gray-100 text-gray-600 hover:bg-indigo-100 hover:text-indigo-600 active:scale-95`;
  };

  const getButtonIcon = () => {
    if (isProcessing) {
      return (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      );
    }
    
    if (isRecording) {
      return (
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M6 6h12v12H6z" />
        </svg>
      );
    }
    
    return (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
      </svg>
    );
  };

  return (
    <button
      className={`${getButtonStyles()} ${className}`}
      onMouseDown={isMobile ? undefined : handleMouseDown}
      onMouseUp={isMobile ? undefined : handleMouseUp}
      onMouseLeave={handleMouseLeave}
      onTouchStart={isMobile ? handleMouseDown : undefined}
      onTouchEnd={isMobile ? handleMouseUp : undefined}
      onClick={isMobile ? onToggleCommandCenter : undefined}
      disabled={disabled}
      title={
        isRecording ? 'Recording... (Click to stop)' :
        isProcessing ? 'Processing...' :
        isMobile ? 'Tap to open voice commands' :
        'Click to open, Hold to record'
      }
      aria-label={
        isRecording ? 'Stop voice recording' :
        isProcessing ? 'Processing voice command' :
        'Voice command button'
      }
    >
      {getButtonIcon()}
      
      {/* Recording indicator */}
      {isRecording && (
        <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-ping" />
      )}
      
      {/* Long press indicator */}
      {isLongPress && (
        <div className="absolute inset-0 border-2 border-indigo-500 rounded-lg animate-pulse" />
      )}
    </button>
  );
});

// Main navbar integration component
const NavbarCommandIntegration = memo(({ className = '', showStatusIndicator = true, showVoiceButton = true }) => {
  const [lastError, setLastError] = useState(null);
  const [keyboardShortcuts, setKeyboardShortcuts] = useState(true);

  // Command Center state
  const { 
    isOpen, 
    isCollapsed, 
    session, 
    currentView 
  } = useCommandStore(
    state => ({
      isOpen: state.isOpen,
      isCollapsed: state.isCollapsed,
      session: state.session,
      currentView: state.currentView
    }),
    shallow
  );

  // Command Center actions
  const { 
    open, 
    close, 
    collapse, 
    expand,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    saveSession,
    sendMessage
  } = useCommandStore(
    state => ({
      open: state.open,
      close: state.close,
      collapse: state.collapse,
      expand: state.expand,
      startRecording: state.startRecording,
      stopRecording: state.stopRecording,
      pauseRecording: state.pauseRecording,
      resumeRecording: state.resumeRecording,
      saveSession: state.saveSession,
      sendMessage: state.sendMessage
    }),
    shallow
  );

  // Enhanced Command Center control
  const handleToggleCommandCenter = useCallback(() => {
    try {
      if (!isOpen && !isCollapsed) {
        // Closed -> Open
        open();
      } else if (isOpen && !isCollapsed) {
        // Open -> Collapsed (with pause if recording)
        if (NAVBAR_CONFIG.BEHAVIOR.PAUSE_ON_COLLAPSE && session?.isRecording) {
          pauseRecording();
        }
        collapse();
      } else if (isCollapsed) {
        // Collapsed -> Open (with resume if was recording)
        if (NAVBAR_CONFIG.BEHAVIOR.RESUME_ON_EXPAND && session?.isPaused) {
          resumeRecording();
        }
        expand();
      }
      
      setLastError(null);
    } catch (error) {
      console.error('[NavbarIntegration] Toggle command center failed:', error);
      setLastError(error.message);
    }
  }, [isOpen, isCollapsed, session, open, collapse, expand, pauseRecording, resumeRecording]);

  const handleStartRecording = useCallback(async () => {
    try {
      // Ensure command center is open
      if (!isOpen) {
        open();
      }
      
      // Start recording
      await startRecording();
      setLastError(null);
    } catch (error) {
      console.error('[NavbarIntegration] Start recording failed:', error);
      setLastError(error.message);
    }
  }, [isOpen, open, startRecording]);

  const handleStopRecording = useCallback(async () => {
    try {
      await stopRecording();
      setLastError(null);
    } catch (error) {
      console.error('[NavbarIntegration] Stop recording failed:', error);
      setLastError(error.message);
    }
  }, [stopRecording]);

  const handleGracefulSend = useCallback(async (message) => {
    try {
      // If recording, stop it first
      if (session?.isRecording) {
        await stopRecording();
        
        // Wait a moment for processing to complete
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      // Send message
      await sendMessage(message);
      setLastError(null);
    } catch (error) {
      console.error('[NavbarIntegration] Graceful send failed:', error);
      setLastError(error.message);
      
      if (NAVBAR_CONFIG.BEHAVIOR.PRESERVE_INPUT_ON_ERROR) {
        // Could emit event to preserve input text
        window.dispatchEvent(new CustomEvent('aura:preserve-input', { 
          detail: { message, error: error.message } 
        }));
      }
    }
  }, [session, stopRecording, sendMessage]);

  // Keyboard shortcuts
  useEffect(() => {
    if (!keyboardShortcuts) return;

    const handleKeyDown = (e) => {
      const isModKey = e.ctrlKey || e.metaKey;
      
      if (isModKey && e.shiftKey && e.key.toLowerCase() === 'a') {
        e.preventDefault();
        handleToggleCommandCenter();
      } else if (isModKey && e.shiftKey && e.key.toLowerCase() === 'v') {
        e.preventDefault();
        if (session?.isRecording) {
          handleStopRecording();
        } else {
          handleStartRecording();
        }
      } else if (isModKey && e.shiftKey && e.key.toLowerCase() === 'p') {
        e.preventDefault();
        if (session?.isRecording) {
          pauseRecording();
        } else if (session?.isPaused) {
          resumeRecording();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [
    keyboardShortcuts,
    session,
    handleToggleCommandCenter,
    handleStartRecording,
    handleStopRecording,
    pauseRecording,
    resumeRecording
  ]);

  // Auto-save on navigation
  useEffect(() => {
    if (!NAVBAR_CONFIG.BEHAVIOR.AUTO_SAVE_ON_NAVIGATE) return;

    const handleBeforeUnload = () => {
      if (session?.id) {
        saveSession();
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [session, saveSession]);

  // Determine current status
  const getCurrentStatus = () => {
    if (session?.isProcessing) return 'processing';
    if (session?.isRecording) return 'recording';
    if (session?.isPaused) return 'paused';
    if (session?.isOnline === false) return 'offline';
    if (session?.id) return 'connected';
    return 'idle';
  };

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* Status indicator */}
      {showStatusIndicator && (
        <CommandStatusIndicator
          status={getCurrentStatus()}
          error={lastError}
          className="hidden sm:flex"
        />
      )}

      {/* Voice command button */}
      {showVoiceButton && (
        <VoiceCommandButton
          isRecording={session?.isRecording || false}
          isProcessing={session?.isProcessing || false}
          onStartRecording={handleStartRecording}
          onStopRecording={handleStopRecording}
          onToggleCommandCenter={handleToggleCommandCenter}
          disabled={false}
        />
      )}

      {/* Error message tooltip */}
      {lastError && (
        <div className="absolute top-full mt-2 right-0 z-50 max-w-sm p-2 bg-red-100 border border-red-300 rounded-lg shadow-lg">
          <div className="flex items-start space-x-2">
            <svg className="w-4 h-4 text-red-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-800">Command Error</p>
              <p className="text-xs text-red-600 mt-1">{lastError}</p>
            </div>
          </div>
        </div>
      )}

      {/* Keyboard shortcuts help */}
      <div className="hidden lg:block text-xs text-gray-400 ml-2">
        <div>Ctrl+Shift+A: Toggle</div>
        <div>Ctrl+Shift+V: Voice</div>
      </div>
    </div>
  );
});

// Hook for navbar integration
export const useNavbarCommandIntegration = () => {
  const store = useCommandStore();
  
  const gracefulSend = useCallback(async (message) => {
    try {
      if (store.session?.isRecording) {
        await store.stopRecording();
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      await store.sendMessage(message);
      return { success: true };
    } catch (error) {
      console.error('[NavbarIntegration] Graceful send failed:', error);
      return { success: false, error: error.message };
    }
  }, [store]);

  const smartToggle = useCallback(() => {
    try {
      if (!store.isOpen && !store.isCollapsed) {
        store.open();
      } else if (store.isOpen && !store.isCollapsed) {
        if (store.session?.isRecording) {
          store.pauseRecording();
        }
        store.collapse();
      } else if (store.isCollapsed) {
        if (store.session?.isPaused) {
          store.resumeRecording();
        }
        store.expand();
      }
      return { success: true };
    } catch (error) {
      console.error('[NavbarIntegration] Smart toggle failed:', error);
      return { success: false, error: error.message };
    }
  }, [store]);

  const getStatus = useCallback(() => {
    return {
      isOpen: store.isOpen,
      isCollapsed: store.isCollapsed,
      isRecording: store.session?.isRecording || false,
      isProcessing: store.session?.isProcessing || false,
      isPaused: store.session?.isPaused || false,
      isOnline: store.session?.isOnline ?? true,
      hasActiveSession: !!store.session?.id
    };
  }, [store]);

  return {
    gracefulSend,
    smartToggle,
    getStatus,
    store
  };
};

CommandStatusIndicator.displayName = 'CommandStatusIndicator';
VoiceCommandButton.displayName = 'VoiceCommandButton';
NavbarCommandIntegration.displayName = 'NavbarCommandIntegration';

export default NavbarCommandIntegration;
export { NAVBAR_CONFIG };