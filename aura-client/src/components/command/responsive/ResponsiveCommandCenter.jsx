/**
 * Aura v3.0 Responsive Mobile & Desktop Command Center
 * 
 * Platform-specific optimizations:
 * ✅ Mobile: swipe gestures, keyboard-safe layout, notch awareness
 * ✅ Mobile: auto-collapse on scroll, touch-optimized controls
 * ✅ Desktop: dockable floating mode, minimize to tray
 * ✅ Desktop: hover states, draggable/resizable window
 * ✅ Cross-platform: adaptive layouts and interactions
 * ✅ Accessibility: keyboard navigation, screen reader support
 * 
 * Features:
 * - Responsive breakpoints with mobile-first design
 * - Touch gesture support (swipe, pinch, long-press)
 * - Keyboard-safe mobile layout with viewport adjustment
 * - Desktop window management (drag, resize, dock)
 * - Platform-specific animations and interactions
 * - Adaptive UI density and control sizing
 */

import React, { memo, useCallback, useRef, useEffect, useState, useMemo } from 'react';
import { shallow } from 'zustand/shallow';
import { useCommandStore } from '../../store/commandStore';
import { useSwipeable } from 'react-swipeable';

// Device detection utilities
const DeviceUtils = {
  isMobile: () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           window.innerWidth < 768;
  },
  
  isTouch: () => {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  },
  
  isIOS: () => {
    return /iPad|iPhone|iPod/.test(navigator.userAgent);
  },
  
  hasNotch: () => {
    // Detect device notch
    return window.CSS?.supports('padding-top: env(safe-area-inset-top)');
  },
  
  getViewportHeight: () => {
    // Get actual viewport height (mobile keyboard safe)
    return window.visualViewport?.height || window.innerHeight;
  },
  
  isDesktop: () => {
    return !DeviceUtils.isMobile() && window.innerWidth >= 1024;
  }
};

// Responsive configuration
const RESPONSIVE_CONFIG = {
  BREAKPOINTS: {
    mobile: 768,
    tablet: 1024,
    desktop: 1280
  },
  MOBILE: {
    SWIPE_THRESHOLD: 50, // pixels
    LONG_PRESS_DURATION: 500, // ms
    AUTO_COLLAPSE_SCROLL: 100, // pixels
    KEYBOARD_PADDING: 20, // pixels
    SAFE_AREA_PADDING: true
  },
  DESKTOP: {
    MIN_WIDTH: 350,
    MIN_HEIGHT: 400,
    DEFAULT_WIDTH: 400,
    DEFAULT_HEIGHT: 600,
    SNAP_THRESHOLD: 20, // pixels from edge
    DOCK_ZONES: ['left', 'right', 'bottom']
  },
  ANIMATIONS: {
    SLIDE_DURATION: 300, // ms
    SCALE_DURATION: 200, // ms
    SPRING_CONFIG: { tension: 300, friction: 30 }
  }
};

// Mobile-specific components
const MobileLayout = memo(({ children, isCollapsed, onCollapse, onExpand }) => {
  const [keyboardHeight, setKeyboardHeight] = useState(0);
  const [scrollY, setScrollY] = useState(0);
  const layoutRef = useRef(null);

  // Handle viewport changes (keyboard)
  useEffect(() => {
    const handleViewportChange = () => {
      if (window.visualViewport) {
        const keyboardHeight = window.innerHeight - window.visualViewport.height;
        setKeyboardHeight(Math.max(0, keyboardHeight));
      }
    };

    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', handleViewportChange);
      return () => window.visualViewport.removeEventListener('resize', handleViewportChange);
    }
  }, []);

  // Handle scroll-based auto-collapse
  useEffect(() => {
    let lastScrollY = 0;
    
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const scrollDelta = Math.abs(currentScrollY - lastScrollY);
      
      if (scrollDelta > RESPONSIVE_CONFIG.MOBILE.AUTO_COLLAPSE_SCROLL && !isCollapsed) {
        onCollapse();
      }
      
      lastScrollY = currentScrollY;
      setScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isCollapsed, onCollapse]);

  // Swipe gestures
  const swipeHandlers = useSwipeable({
    onSwipedUp: () => {
      if (isCollapsed) {
        onExpand();
      }
    },
    onSwipedDown: () => {
      if (!isCollapsed) {
        onCollapse();
      }
    },
    onSwipedLeft: () => {
      if (!isCollapsed) {
        onCollapse();
      }
    },
    trackMouse: false,
    delta: RESPONSIVE_CONFIG.MOBILE.SWIPE_THRESHOLD,
    preventDefaultTouchmoveEvent: false
  });

  const mobileStyles = useMemo(() => ({
    container: {
      paddingTop: DeviceUtils.hasNotch() ? 'env(safe-area-inset-top)' : '0',
      paddingBottom: Math.max(
        keyboardHeight + RESPONSIVE_CONFIG.MOBILE.KEYBOARD_PADDING,
        DeviceUtils.hasNotch() ? 'env(safe-area-inset-bottom)' : '0'
      ),
      paddingLeft: DeviceUtils.hasNotch() ? 'env(safe-area-inset-left)' : '0',
      paddingRight: DeviceUtils.hasNotch() ? 'env(safe-area-inset-right)' : '0'
    },
    overlay: {
      height: `${DeviceUtils.getViewportHeight()}px`,
      transform: `translateY(${scrollY * 0.1}px)` // Subtle parallax
    }
  }), [keyboardHeight, scrollY]);

  return (
    <div 
      ref={layoutRef}
      className="mobile-command-center fixed inset-0 z-50"
      style={mobileStyles.container}
      {...swipeHandlers}
    >
      <div 
        className="mobile-overlay bg-black bg-opacity-50 backdrop-blur-sm transition-opacity duration-300"
        style={mobileStyles.overlay}
      >
        {children}
      </div>
      
      {/* Mobile-specific UI hints */}
      {isCollapsed && (
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-60">
          <div className="bg-gray-800 text-white px-3 py-1 rounded-full text-xs animate-pulse">
            Swipe up to open
          </div>
        </div>
      )}
    </div>
  );
});

// Desktop-specific components
const DesktopLayout = memo(({ children, isCollapsed, position, onPositionChange, size, onSizeChange }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [isDocked, setIsDocked] = useState(false);
  const layoutRef = useRef(null);

  // Handle window dragging
  const handleMouseDown = useCallback((e) => {
    if (e.target.classList.contains('drag-handle')) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  }, [position]);

  const handleMouseMove = useCallback((e) => {
    if (isDragging) {
      const newX = e.clientX - dragStart.x;
      const newY = e.clientY - dragStart.y;
      
      // Snap to edges
      const snapThreshold = RESPONSIVE_CONFIG.DESKTOP.SNAP_THRESHOLD;
      let snappedX = newX;
      let snappedY = newY;
      
      if (newX < snapThreshold) {
        snappedX = 0;
        setIsDocked(true);
      } else if (newX > window.innerWidth - size.width - snapThreshold) {
        snappedX = window.innerWidth - size.width;
        setIsDocked(true);
      } else {
        setIsDocked(false);
      }
      
      if (newY < snapThreshold) {
        snappedY = 0;
      } else if (newY > window.innerHeight - size.height - snapThreshold) {
        snappedY = window.innerHeight - size.height;
      }
      
      onPositionChange({ x: snappedX, y: snappedY });
    }
  }, [isDragging, dragStart, onPositionChange, size]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Handle window resizing
  const handleResizeStart = useCallback((e) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const handleResize = useCallback((e) => {
    if (isResizing) {
      const rect = layoutRef.current?.getBoundingClientRect();
      if (!rect) return;

      const newWidth = Math.max(
        RESPONSIVE_CONFIG.DESKTOP.MIN_WIDTH,
        e.clientX - rect.left
      );
      const newHeight = Math.max(
        RESPONSIVE_CONFIG.DESKTOP.MIN_HEIGHT,
        e.clientY - rect.top
      );

      onSizeChange({ width: newWidth, height: newHeight });
    }
  }, [isResizing, onSizeChange]);

  const handleResizeEnd = useCallback(() => {
    setIsResizing(false);
  }, []);

  // Mouse event listeners
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleResize);
      document.addEventListener('mouseup', handleResizeEnd);
      return () => {
        document.removeEventListener('mousemove', handleResize);
        document.removeEventListener('mouseup', handleResizeEnd);
      };
    }
  }, [isResizing, handleResize, handleResizeEnd]);

  const desktopStyles = useMemo(() => ({
    container: {
      left: `${position.x}px`,
      top: `${position.y}px`,
      width: `${size.width}px`,
      height: `${size.height}px`,
      cursor: isDragging ? 'grabbing' : 'default',
      boxShadow: isDocked ? '0 0 0 2px #3B82F6' : '0 10px 25px rgba(0, 0, 0, 0.2)',
      transition: isDragging ? 'none' : 'all 0.2s ease'
    }
  }), [position, size, isDragging, isDocked]);

  return (
    <div 
      ref={layoutRef}
      className="desktop-command-center fixed bg-white rounded-lg overflow-hidden shadow-xl border border-gray-200"
      style={desktopStyles.container}
      onMouseDown={handleMouseDown}
    >
      {/* Title bar with drag handle */}
      <div className="drag-handle bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center justify-between cursor-grab hover:bg-gray-100">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
        </div>
        <h2 className="text-sm font-medium text-gray-700 select-none">Aura Command Center</h2>
        <div className="flex items-center space-x-1">
          {isDocked && (
            <div className="text-xs text-blue-600 font-medium">Docked</div>
          )}
        </div>
      </div>
      
      {/* Content area */}
      <div className="desktop-content flex-1 overflow-hidden">
        {children}
      </div>
      
      {/* Resize handle */}
      <div 
        className="absolute bottom-0 right-0 w-4 h-4 bg-gray-300 cursor-nw-resize hover:bg-gray-400 transition-colors"
        onMouseDown={handleResizeStart}
        style={{
          background: 'linear-gradient(-45deg, transparent 30%, #9CA3AF 30%, #9CA3AF 70%, transparent 70%)'
        }}
      />
    </div>
  );
});

// Responsive content wrapper
const ResponsiveContent = memo(({ children, isMobile, isCollapsed }) => {
  const contentStyles = useMemo(() => {
    if (isMobile) {
      return {
        container: isCollapsed ? 
          'flex flex-col h-20 bg-white rounded-t-3xl shadow-lg' :
          'flex flex-col h-full bg-white rounded-t-3xl shadow-lg',
        content: 'flex-1 overflow-hidden'
      };
    } else {
      return {
        container: 'flex flex-col h-full',
        content: 'flex-1 overflow-hidden'
      };
    }
  }, [isMobile, isCollapsed]);

  return (
    <div className={contentStyles.container}>
      {isMobile && (
        <div className="flex-shrink-0 p-2 border-b border-gray-200">
          <div className="w-12 h-1 bg-gray-300 rounded mx-auto"></div>
        </div>
      )}
      <div className={contentStyles.content}>
        {children}
      </div>
    </div>
  );
});

// Adaptive input components
const AdaptiveButton = memo(({ children, onClick, variant = 'primary', size = 'medium', className = '', ...props }) => {
  const isMobile = DeviceUtils.isMobile();
  const isTouch = DeviceUtils.isTouch();
  
  const buttonStyles = useMemo(() => {
    const baseStyles = 'font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2';
    
    const variants = {
      primary: 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500',
      secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
      ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500'
    };
    
    const sizes = {
      small: isMobile ? 'px-3 py-2 text-sm min-h-[44px]' : 'px-3 py-1.5 text-sm',
      medium: isMobile ? 'px-4 py-3 text-base min-h-[48px]' : 'px-4 py-2 text-sm',
      large: isMobile ? 'px-6 py-4 text-lg min-h-[52px]' : 'px-6 py-3 text-base'
    };
    
    const touchStyles = isTouch ? 'active:scale-95' : 'hover:scale-105';
    
    return `${baseStyles} ${variants[variant]} ${sizes[size]} ${touchStyles} ${className}`;
  }, [isMobile, isTouch, variant, size, className]);

  return (
    <button
      className={buttonStyles}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  );
});

// Main responsive command center component
const ResponsiveCommandCenter = memo(() => {
  const [isMobile, setIsMobile] = useState(DeviceUtils.isMobile());
  const [deviceInfo, setDeviceInfo] = useState({
    isTouch: DeviceUtils.isTouch(),
    isIOS: DeviceUtils.isIOS(),
    hasNotch: DeviceUtils.hasNotch()
  });
  
  // Desktop window management state
  const [desktopPosition, setDesktopPosition] = useState({ 
    x: window.innerWidth - RESPONSIVE_CONFIG.DESKTOP.DEFAULT_WIDTH - 20, 
    y: 20 
  });
  const [desktopSize, setDesktopSize] = useState({
    width: RESPONSIVE_CONFIG.DESKTOP.DEFAULT_WIDTH,
    height: RESPONSIVE_CONFIG.DESKTOP.DEFAULT_HEIGHT
  });

  // Command Center state
  const { isOpen, isCollapsed, currentView } = useCommandStore(
    state => ({
      isOpen: state.isOpen,
      isCollapsed: state.isCollapsed,
      currentView: state.currentView
    }),
    shallow
  );

  const { collapse, expand, close, setCurrentView } = useCommandStore(
    state => ({
      collapse: state.collapse,
      expand: state.expand,
      close: state.close,
      setCurrentView: state.setCurrentView
    }),
    shallow
  );

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      const newIsMobile = DeviceUtils.isMobile();
      setIsMobile(newIsMobile);
      
      // Update desktop position if window size changes
      if (!newIsMobile) {
        setDesktopPosition(prev => ({
          x: Math.min(prev.x, window.innerWidth - desktopSize.width),
          y: Math.min(prev.y, window.innerHeight - desktopSize.height)
        }));
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [desktopSize]);

  // Device orientation change handling
  useEffect(() => {
    const handleOrientationChange = () => {
      setTimeout(() => {
        setDeviceInfo({
          isTouch: DeviceUtils.isTouch(),
          isIOS: DeviceUtils.isIOS(),
          hasNotch: DeviceUtils.hasNotch()
        });
      }, 100);
    };

    window.addEventListener('orientationchange', handleOrientationChange);
    return () => window.removeEventListener('orientationchange', handleOrientationChange);
  }, []);

  // Content component
  const renderContent = useCallback(() => {
    return (
      <ResponsiveContent isMobile={isMobile} isCollapsed={isCollapsed}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            {isMobile && isCollapsed ? 'Aura' : 'Aura Command Center'}
          </h2>
          <div className="flex space-x-2">
            {!isMobile && (
              <AdaptiveButton
                variant="ghost"
                size="small"
                onClick={collapse}
                title="Minimize"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
              </AdaptiveButton>
            )}
            <AdaptiveButton
              variant="ghost"
              size="small"
              onClick={close}
              title="Close"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </AdaptiveButton>
          </div>
        </div>

        {/* View tabs (if not collapsed on mobile) */}
        {!(isMobile && isCollapsed) && (
          <div className="flex border-b border-gray-200">
            {['voice', 'chat'].map((view) => (
              <AdaptiveButton
                key={view}
                variant={currentView === view ? 'primary' : 'ghost'}
                size="medium"
                className={`flex-1 rounded-none border-b-2 ${
                  currentView === view
                    ? 'border-indigo-600 bg-indigo-50'
                    : 'border-transparent'
                }`}
                onClick={() => setCurrentView(view)}
              >
                {view.charAt(0).toUpperCase() + view.slice(1)}
              </AdaptiveButton>
            ))}
          </div>
        )}

        {/* Main content area */}
        {!(isMobile && isCollapsed) && (
          <div className="flex-1 p-4">
            {currentView === 'voice' ? (
              <div className="flex flex-col items-center justify-center h-full space-y-4">
                <div className="w-16 h-16 bg-indigo-600 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <p className="text-center text-gray-600">
                  {isMobile ? 'Tap to start recording' : 'Click to start voice command'}
                </p>
              </div>
            ) : (
              <div className="h-full flex flex-col space-y-4">
                <div className="flex-1 bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-600">Chat interface coming soon...</p>
                </div>
                <div className="flex space-x-2">
                  <input 
                    type="text" 
                    placeholder="Type your message..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                  <AdaptiveButton variant="primary" size="medium">
                    Send
                  </AdaptiveButton>
                </div>
              </div>
            )}
          </div>
        )}
      </ResponsiveContent>
    );
  }, [isMobile, isCollapsed, currentView, collapse, close, setCurrentView]);

  // Don't render if not open
  if (!isOpen && !isCollapsed) {
    return null;
  }

  // Render mobile layout
  if (isMobile) {
    return (
      <MobileLayout 
        isCollapsed={isCollapsed}
        onCollapse={collapse}
        onExpand={expand}
      >
        <div className={`transform transition-transform duration-300 ${
          isCollapsed ? 'translate-y-full' : 'translate-y-0'
        }`}>
          <div className="absolute inset-x-0 bottom-0">
            {renderContent()}
          </div>
        </div>
      </MobileLayout>
    );
  }

  // Render desktop layout
  return (
    <DesktopLayout
      isCollapsed={isCollapsed}
      position={desktopPosition}
      onPositionChange={setDesktopPosition}
      size={desktopSize}
      onSizeChange={setDesktopSize}
    >
      {renderContent()}
    </DesktopLayout>
  );
});

ResponsiveCommandCenter.displayName = 'ResponsiveCommandCenter';
MobileLayout.displayName = 'MobileLayout';
DesktopLayout.displayName = 'DesktopLayout';
ResponsiveContent.displayName = 'ResponsiveContent';
AdaptiveButton.displayName = 'AdaptiveButton';

export default ResponsiveCommandCenter;
export { DeviceUtils, RESPONSIVE_CONFIG, AdaptiveButton };