# Changelog

All notable changes to the Aura AI Assistant project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.9.7] - 2025-10-09 - Session Persistence & Navigation Continuity

### 🔄 Added - Session Management System

- **Persistent Session State**: Complete session state preservation across navigation
  - Recording session persistence (microphone state, recording duration)
  - Processing continuation in background (current task ID, progress)
  - Streaming restoration when returning to CommandCenter
  - Last prompt caching for seamless user experience
  - Auto-expiration after 30 minutes for security

- **Background Workflow Continuation**: Uninterrupted task processing
  - SSE streams continue running when CommandCenter unmounts
  - Processing states maintained in background during navigation
  - Seamless restoration of in-progress streaming responses
  - Task orchestration continues independently of UI state
  - Smart recovery for interrupted workflows

- **Enhanced Voice Recording Experience**:
  - **Send During Recording**: Users can press Send while actively recording
    - Smooth transition from recording directly to processing
    - No UI flicker or state confusion
    - Automatic transcription triggering
    - Contextual button labels ("Stop & Send Command")
  - Recording state persists across page navigation
  - Visual recording duration tracking
  - Pause/resume functionality with state preservation

### 🎨 User Experience Enhancements

- **Session Restoration UI States**: Intelligent UI restoration
  - Recording indicator automatically reappears on return
  - Processing spinners show for background tasks
  - Streaming text continues from where it left off
  - "⏮️ Restoring session…" status indicator during restoration
  - Resume pending flag prevents UI confusion

- **Seamless Navigation**: Zero interruption user experience
  - Navigate away during recording/processing without losing work
  - Return to find sessions exactly where you left them
  - Background task completion notifications
  - Smart session cleanup on completion

### 🏗️ Technical Infrastructure

- **Enhanced Zustand Store** (`store/commandStore.ts`):
  ```typescript
  interface SessionState {
    isRecording: boolean;
    isProcessing: boolean;
    isStreaming: boolean;
    lastPrompt: string | null;
    currentTaskId?: string;
    resumePending: boolean;
    streamingText?: string;
    recordingStartTime?: number;
  }
  ```

- **Session Persistence Methods**:
  - `setRecording()`: Update recording state with timestamp
  - `setProcessing()`: Track processing state changes
  - `setStreaming()`: Manage streaming state with text caching
  - `cacheSession()`: Save state to localStorage with timestamp
  - `restoreSession()`: Load and validate cached state
  - `clearSession()`: Clean up expired or completed sessions
  - `updateSession()`: Granular session state updates

- **Lifecycle Management** (`components/ui/CommandCenter.tsx`):
  - Mount/unmount handlers for session restoration
  - Automatic state caching on session changes
  - Background workflow monitoring
  - Session expiration and cleanup

### 🛡️ Reliability & Performance

- **Error Handling**: Graceful fallback for localStorage issues
- **Memory Management**: Automatic cleanup of expired sessions
- **Performance Optimized**: < 10ms cache operations, < 50ms restoration
- **State Validation**: Comprehensive session state integrity checks
- **Security**: Auto-expiration prevents stale session persistence

### 🧪 Comprehensive Testing Suite

- **Session Persistence Test Suite** (`public/test-session-persistence-v295.js`):
  ```javascript
  // Browser console testing
  testSessionPersistence();     // Full test suite
  quickSessionTest();           // Quick state inspection
  clearAllSessions();           // Clean up test data
  ```

- **Test Coverage**:
  - Recording session persistence across navigation
  - Processing continuation in background
  - Streaming restoration validation
  - Session expiration handling
  - UI state synchronization
  - Performance monitoring
  - Memory usage validation

### 📊 Impact & Benefits

| Feature | Before v2.9.7 | After v2.9.7 |
|---------|---------------|---------------|
| **Recording Navigation** | ❌ Lost on page change | ✅ Persists across navigation |
| **Processing Interruption** | ❌ Tasks abandoned | ✅ Continues in background |
| **Send During Recording** | ❌ Must stop first | ✅ Seamless stop-and-send |
| **Session Recovery** | ❌ Manual restart required | ✅ Automatic restoration |
| **UI State Confusion** | ❌ Inconsistent states | ✅ Perfect synchronization |
| **Workflow Interruption** | ❌ Lost progress | ✅ Zero interruption |

### 🎯 User Workflow Examples

1. **Voice Recording Workflow**:
   - Start recording → Navigate away → Return → Recording continues
   - Record → Press Send → Navigate → Return → See completed response

2. **Background Processing**:
   - Send text command → Navigate during processing → Return → See results
   - Long-running tasks complete while browsing other pages

3. **Streaming Restoration**:
   - Start streaming response → Navigate → Return → Text continues from checkpoint
   - No content loss during navigation

---

## [2.9.6] - 2025-10-09 - Contextual Follow-Up Behavior & Auto-Dismiss

### ✨ Enhanced - Smart Follow-Up Contextual Behavior

- **Contextual Visibility**: Follow-up cards now appear **only after successful task completion** with relevant suggestions
  - Confidence threshold filtering (≥ 0.6) prevents low-quality suggestions
  - Event-driven display eliminates UI clutter and maintains voice-first flow
  - No longer persists in idle state or during active processing

- **Auto-Dismiss Timer**: Ephemeral 10-second display window
  - Automatically fades out after timeout to maintain clean UI
  - Manual dismiss still available with immediate response
  - Prevents follow-up cards from becoming permanent UI elements

- **Mode-Aware Behavior**: Respects voice-first design principles
  - Hidden during recording, transcription, and streaming phases
  - Cross-mode parity: works identically in Voice and Text modes
  - Clean state reset when switching between modes

- **Enhanced Visual Indicators**: Color-coded confidence scoring
  - 🟢 **Green** (≥ 80%): High confidence suggestions
  - 🟡 **Yellow** (≥ 60%): Moderate confidence suggestions  
  - ⚫ **Gray** (< 60%): Fallback suggestions (filtered out)

### 🎨 User Experience Improvements

- **Organic Feel**: Follow-ups feel natural and contextual, not intrusive
- **Voice-First Respect**: Never interrupts active voice interactions
- **Smooth Transitions**: Enhanced fade-in/fade-out animations (0.25s)
- **Clean State Management**: Proper cleanup on mode changes and dismissals

### 🔧 Technical Enhancements

- **State Management**: Added `showFollowUp` visibility control state
- **Timeout Management**: Proper cleanup of auto-dismiss timers
- **Event-Driven Logic**: Contextual visibility based on task completion events
- **Development Logging**: Comprehensive debug information for follow-up states

### 🧪 Testing Framework

- **Comprehensive Test Suite**: 7-point validation covering all contextual behaviors
- **Performance Monitoring**: Real-time follow-up visibility tracking
- **Manual Test Scenarios**: Complete user interaction validation

### 📊 Behavioral Changes

| Before v2.9.6 | After v2.9.6 |
|---------------|---------------|
| ❌ Always visible when suggestion exists | ✅ Only after task completion |
| ❌ Permanent until manually dismissed | ✅ Auto-dismiss after 10 seconds |
| ❌ Visible during voice recording | ✅ Hidden during active interactions |
| ❌ Basic confidence display | ✅ Color-coded confidence indicators |
| ❌ UI clutter in idle state | ✅ Clean, contextual appearance |

---

## [2.9.5] - 2025-10-09 - Task Lifecycle Recovery & Auto-Resolution

### 🔄 Added - Task Lifecycle Management

- **Watchdog Timer System**: Automatic detection and resolution of stale tasks stuck in Pending/Processing states
  - Configurable timeouts: 5 min for Pending, 10 min for Processing, 15 min general timeout
  - Runs every minute to check for stuck tasks
  - Auto-marks expired tasks as "Error" with descriptive messages

- **Manual Retry Functionality**: One-click retry system for failed tasks
  - "Retry Task" button appears on all Error status tasks
  - Automatically resets task to Pending and re-triggers orchestration
  - Comprehensive error handling and logging

- **Auto-Recovery System**: Smart recovery for orphaned and incomplete tasks
  - Detects local tasks not synchronized with backend
  - Auto-completes orphaned tasks older than 2 minutes
  - Validates local store consistency during sync cycles

- **Enhanced UI Indicators**: Rich visual feedback for task lifecycle states
  - Task age display ("5m 30s" format)
  - Task type badges (CMA, MARKET_REPORT, etc.)
  - Stale task warning indicators (yellow triangles)
  - Linked task indicators (🔗 icon)
  - Visual error states with retry buttons

### 🔧 Enhanced

- **Task Sync Service**: Integrated lifecycle management with sync operations
  - Watchdog timer starts automatically with sync service
  - Orphaned task detection and cleanup
  - Performance monitoring and validation

- **Zustand Store**: Extended with lifecycle management actions
  - `checkStaleTasks()`: Detect and auto-resolve stuck tasks
  - `retryTask()`: Manual retry functionality with orchestration integration
  - `clearStuckTasks()`: Cleanup utility for maintenance

- **RequestItem Component**: Comprehensive redesign for lifecycle visibility
  - Age tracking and display
  - Task metadata visibility
  - Interactive retry buttons
  - Visual stale task indicators

### 🛠️ Configuration

- **Lifecycle Constants**: Centralized timeout and retry configuration
  - Configurable timeout values for different task states
  - Customizable error messages and retry settings
  - Performance monitoring parameters

### 🧪 Testing

- **Comprehensive Test Suite**: Full lifecycle testing framework
  - Automated stale task simulation and detection
  - Manual retry functionality validation
  - UI enhancement verification
  - Performance monitoring and statistics

### 📊 Impact

- **Reliability**: No more permanently stuck tasks
- **Visibility**: Clear task lifecycle status and age information
- **Recovery**: Automatic and manual task recovery options
- **Performance**: Optimized task management with automatic cleanup

---

## [2.9.4.1] - 2025-10-09 - Follow-up Display & Dismiss Hotfix

### 🔧 Fixed

- **FollowUpCard Visibility**: Fixed follow-up cards not appearing in Voice mode - cards now display in both Voice and Text modes
- **Dismiss Button Behavior**: Fixed dismiss (✕) button not removing cards from screen due to stale state binding
- **UI Logic Improvements**: 
  - Added proper AnimatePresence wrapper for smooth card transitions
  - Enhanced dismiss handler with console logging for better debugging
  - Added mode change cleanup to reset follow-up state when switching between Voice ↔ Text
  - Prevented duplicate follow-up card renders with defensive guards

### 🎨 Enhanced

- **User Experience**: Follow-up suggestions now work seamlessly across both interface modes
- **State Management**: Improved follow-up state lifecycle with proper cleanup on mode changes
- **Visual Feedback**: Added smooth fade-in/fade-out animations for follow-up card appearance

---

## [2.9.4] - 2025-10-09

### 🎯 Added - Intelligent Follow-up and Linked Task Automation

- **AI Follow-up Agent Service** (`services/followupAgent.ts`)
  - Contextual analysis of completed tasks
  - Intelligent suggestion generation based on task type and metadata
  - Support for CMA, Market Reports, Social Posts, and Generic tasks
  - Confidence scoring for suggestion quality
  - Smart filtering to prevent infinite suggestion loops

- **Enhanced Task Relationship Management** (`store/commandStore.ts`)
  - Added `parentId` field to Request interface for task linking
  - Added `relatedTasks` array to track child tasks
  - Implemented `linkTasks()` action for creating parent-child relationships
  - Enhanced task chain integrity and context preservation

- **FollowUpCard UI Component** (`components/ui/FollowUpCard.tsx`)
  - Elegant inline follow-up suggestion display
  - One-click accept/dismiss functionality
  - Visual confidence indicators and loading states
  - Responsive design with smooth animations
  - Intent and location context preview

- **Command Orchestrator Enhancement** (`services/orchestrator.ts`)
  - Support for optional `parentId` parameter in orchestration
  - Maintains task relationship context during execution
  - Preserves linked task metadata across operations

- **CommandCenter Integration** (`components/ui/CommandCenter.tsx`)
  - Automatic follow-up generation on task completion
  - State management for suggestions and execution
  - Seamless UI integration with existing workflow
  - Support for both voice and text interfaces

### 🏗️ Enhanced

- **Task Workflow Intelligence**
  - CMA → Social Media Post workflow chains
  - Market Report → Detailed CMA workflows  
  - Social Post → Marketing Campaign chains
  - Location-based contextual suggestions

- **User Experience Improvements**
  - Proactive AI assistance with contextual next steps
  - Visual task relationship indicators
  - Smooth loading states and error handling
  - Non-intrusive suggestion system

### 🔧 Technical Improvements

- **Type Safety**: Full TypeScript support with proper interfaces
- **Error Handling**: Graceful failures with comprehensive logging
- **Performance**: Async operations with proper loading states
- **Testing**: Comprehensive test suite with mock scenarios
- **Documentation**: Detailed feature documentation and usage examples

### 🧪 Testing

- Created integration test suite (`tests/followup.test.ts`)
- Added browser console test script (`public/test-followup.js`)
- Covered all supported task types and edge cases
- Verified UI states and error scenarios

### 📋 Supported Workflow Chains

1. **CMA Analysis → Social Media Promotion**
   - Generate social posts to promote completed CMA reports
   - Include location and property details in content

2. **Market Report → Property Analysis**
   - Drill down from market-level to property-specific CMAs
   - Maintain market context and insights

3. **Social Content → Marketing Campaigns**
   - Expand social media posts into comprehensive campaigns
   - Cross-platform content optimization

4. **Generic Tasks → Contextual Analysis**
   - Extract actionable insights from general requests
   - Location-based market analysis suggestions

### 🔮 Future Roadmap

- Advanced NLP-based content understanding
- Machine learning for personalized suggestions
- Multi-step workflow automation
- Team collaboration and task handoffs
- Calendar integration for time-based reminders

---

## [2.9.3] - Previous Release

### Added
- Backend CORS fixes and authentication improvements
- Enhanced error handling and logging
- Environment variable fallback tokens

### Fixed
- 403 Forbidden errors in authentication
- 422 Unprocessable Content payload issues
- CORS policy blocks for frontend origins

---

*For detailed technical documentation, see `/docs/features/intelligent-followup.md`*