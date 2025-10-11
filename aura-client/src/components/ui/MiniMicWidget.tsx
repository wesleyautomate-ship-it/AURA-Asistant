import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Play, Loader2 } from 'lucide-react';
import { useCommandStore } from '../../store/commandStore';
import { useState, useEffect, useRef } from 'react';

interface MiniMicWidgetProps {
  position?: 'bottom-right' | 'bottom-left' | 'custom';
  customStyle?: React.CSSProperties;
}

export default function MiniMicWidget({ 
  position = 'bottom-right',
  customStyle 
}: MiniMicWidgetProps) {
  const { 
    isOpen, isCollapsed, session, expand, startRecording, pauseRecording, resumeRecording 
  } = useCommandStore();
  
  const [isPressed, setIsPressed] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);
  const longPressTimeoutRef = useRef<number | null>(null);
  
  // Don't show widget if Command Center is fully open
  if (isOpen && !isCollapsed) {
    return null;
  }
  
  // Position styles
  const positionStyles = {
    'bottom-right': {
      bottom: '24px',
      right: '24px',
    },
    'bottom-left': {
      bottom: '24px', 
      left: '24px',
    },
    'custom': customStyle || {}
  };
  
  // Handle long press functionality
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsPressed(true);
    
    // Start long press timer
    longPressTimeoutRef.current = window.setTimeout(() => {
      handleLongPress();
    }, 500); // 500ms for long press
  };
  
  const handleMouseUp = () => {
    setIsPressed(false);
    
    // Clear long press timer
    if (longPressTimeoutRef.current) {
      clearTimeout(longPressTimeoutRef.current);
      longPressTimeoutRef.current = null;
    }
  };
  
  const handleTap = () => {
    // Only handle tap if it wasn't a long press
    if (!longPressTimeoutRef.current) {
      console.log('[MiniMic] Tap - expanding Command Center');
      expand();
    }
  };
  
  const handleLongPress = () => {
    console.log('[MiniMic] Long press detected');
    
    if (session.isRecording) {
      if (session.recordingPaused) {
        console.log('[MiniMic] Resuming recording via long press');
        resumeRecording();
      } else {
        console.log('[MiniMic] Pausing recording via long press');
        pauseRecording();
      }
    } else {
      console.log('[MiniMic] Starting recording via long press');
      startRecording();
    }
    
    // Clear the timer since we handled the long press
    if (longPressTimeoutRef.current) {
      clearTimeout(longPressTimeoutRef.current);
      longPressTimeoutRef.current = null;
    }
  };
  
  // Touch event handlers for mobile
  const handleTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    setIsPressed(true);
    
    longPressTimeoutRef.current = window.setTimeout(() => {
      handleLongPress();
      // Haptic feedback on mobile
      if ('vibrate' in navigator) {
        navigator.vibrate(50);
      }
    }, 500);
  };
  
  const handleTouchEnd = (e: React.TouchEvent) => {
    e.preventDefault();
    setIsPressed(false);
    
    if (longPressTimeoutRef.current) {
      clearTimeout(longPressTimeoutRef.current);
      longPressTimeoutRef.current = null;
      // This was a tap, not a long press
      handleTap();
    }
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (longPressTimeoutRef.current) {
        clearTimeout(longPressTimeoutRef.current);
      }
    };
  }, []);
  
  // Determine current state for display
  const getWidgetState = () => {
    if (session.isRecording && !session.recordingPaused) {
      return 'recording';
    } else if (session.isRecording && session.recordingPaused) {
      return 'paused';
    } else if (session.isProcessing || session.isStreaming) {
      return 'processing';
    } else {
      return 'idle';
    }
  };
  
  const widgetState = getWidgetState();
  
  // State-based styling and content
  const stateConfig = {
    idle: {
      bgColor: 'from-blue-500 to-blue-600',
      hoverColor: 'hover:from-blue-600 hover:to-blue-700',
      icon: Mic,
      shadowColor: 'shadow-blue-500/30',
      pulseColor: '',
      tooltip: 'Tap to open • Long press to record'
    },
    recording: {
      bgColor: 'from-red-500 to-red-600',
      hoverColor: 'hover:from-red-600 hover:to-red-700', 
      icon: Mic,
      shadowColor: 'shadow-red-500/30',
      pulseColor: 'animate-pulse',
      tooltip: 'Recording • Long press to pause'
    },
    paused: {
      bgColor: 'from-yellow-500 to-yellow-600',
      hoverColor: 'hover:from-yellow-600 hover:to-yellow-700',
      icon: Play,
      shadowColor: 'shadow-yellow-500/30',
      pulseColor: '',
      tooltip: 'Paused • Long press to resume'
    },
    processing: {
      bgColor: 'from-purple-500 to-purple-600',
      hoverColor: 'hover:from-purple-600 hover:to-purple-700',
      icon: Loader2,
      shadowColor: 'shadow-purple-500/30',
      pulseColor: '',
      tooltip: 'Processing • Tap to open'
    }
  };
  
  const config = stateConfig[widgetState];
  const IconComponent = config.icon;
  
  return (
    <>
      {/* Mini Mic Widget */}
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0, opacity: 0 }}
        transition={{ 
          type: 'spring', 
          damping: 25, 
          stiffness: 300,
          delay: 0.2 
        }}
        className="fixed z-50 pointer-events-auto"
        style={positionStyles[position]}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {/* Pulsing Ring for Recording */}
        <AnimatePresence>
          {widgetState === 'recording' && (
            <motion.div
              initial={{ scale: 1, opacity: 1 }}
              animate={{ 
                scale: [1, 1.5, 1],
                opacity: [0.7, 0, 0.7]
              }}
              exit={{ opacity: 0 }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
              className="absolute inset-0 rounded-full bg-red-400 pointer-events-none"
            />
          )}
        </AnimatePresence>
        
        {/* Main Widget Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          animate={isPressed ? { scale: 0.9 } : {}}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onTouchStart={handleTouchStart}
          onTouchEnd={handleTouchEnd}
          className={`
            relative w-14 h-14 rounded-full bg-gradient-to-br ${config.bgColor} ${config.hoverColor}
            text-white shadow-lg ${config.shadowColor} ${config.pulseColor}
            transition-all duration-200 select-none
            ring-2 ring-white/20 backdrop-blur-sm
            active:ring-4 active:ring-white/30
          `}
          style={{
            userSelect: 'none',
            WebkitUserSelect: 'none',
            touchAction: 'manipulation'
          }}
        >
          <IconComponent 
            className={`w-6 h-6 ${
              widgetState === 'processing' ? 'animate-spin' : ''
            }`}
          />
          
          {/* Recording indicator dot */}
          {widgetState === 'recording' && (
            <motion.div
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="absolute -top-1 -right-1 w-3 h-3 bg-red-400 rounded-full border-2 border-white shadow-sm"
            />
          )}
          
          {/* Paused indicator */}
          {widgetState === 'paused' && (
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full border-2 border-white shadow-sm" />
          )}
          
          {/* Processing indicator */}
          {widgetState === 'processing' && (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              className="absolute -top-1 -right-1 w-3 h-3 bg-purple-400 rounded-full border-2 border-white shadow-sm"
            />
          )}
        </motion.button>
        
        {/* Tooltip */}
        <AnimatePresence>
          {showTooltip && (
            <motion.div
              initial={{ opacity: 0, y: 10, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.9 }}
              transition={{ duration: 0.2 }}
              className={`
                absolute ${position === 'bottom-right' ? 'bottom-full right-0 mb-3' : 'bottom-full left-0 mb-3'}
                px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg
                whitespace-nowrap pointer-events-none z-10
                border border-gray-700
              `}
            >
              {config.tooltip}
              <div className={`
                absolute top-full ${position === 'bottom-right' ? 'right-3' : 'left-3'}
                w-0 h-0 border-l-4 border-r-4 border-t-4 
                border-l-transparent border-r-transparent border-t-gray-900
              `} />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
      
      {/* Session Info Badge (shows when collapsed and has active session) */}
      <AnimatePresence>
        {isCollapsed && (session.isRecording || session.isProcessing || session.isStreaming) && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className={`
              fixed z-40 pointer-events-none
              ${position === 'bottom-right' ? 'bottom-20 right-6' : 'bottom-20 left-6'}
              px-3 py-2 bg-gray-900/90 text-white text-xs rounded-lg shadow-lg
              border border-gray-700 backdrop-blur-sm
            `}
          >
            <div className="flex items-center gap-2">
              {session.isRecording && (
                <>
                  <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
                  <span>Recording...</span>
                </>
              )}
              {session.isProcessing && (
                <>
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Processing...</span>
                </>
              )}
              {session.isStreaming && (
                <>
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  <span>AI Responding...</span>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}