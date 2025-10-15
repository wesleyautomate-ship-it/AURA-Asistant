# Track 4: UI Integration Guide

## Overview

This document provides step-by-step instructions for integrating the Track 3 orchestrator service into the existing UI components.

---

## Phase 1: Progress Tracker Component ✅ COMPLETE

**File Created**: `src/components/ui/ProgressTracker.tsx`

**Components**:
1. `<ProgressTracker />` - Full progress display with steps
2. `<CompactProgressBar />` - Inline progress bar
3. `<ProgressBadge />` - Badge for request tiles

**Usage Example**:
```tsx
<ProgressTracker
  currentStep="generating"
  progress={80}
  status="processing"
  error={undefined}
/>
```

---

## Phase 2: CommandCenter Integration

### Step 1: Add Imports (✅ DONE)

```tsx
import { generateContent, getGenerationStatus } from '../../services/orchestratorService';
import { ProgressTracker } from './ProgressTracker';
```

### Step 2: Add State Variables (✅ DONE)

```tsx
const [pipelineProgress, setPipelineProgress] = useState(0);
const [pipelineStep, setPipelineStep] = useState<string>('idle');
const [pipelineStatus, setPipelineStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
const [pipelineError, setPipelineError] = useState<string | undefined>();
const progressPollInterval = useRef<number | null>(null);
```

### Step 3: Create Progress Polling Function

Add this function to CommandCenter:

```tsx
const startProgressPolling = (requestId: string) => {
  // Clear any existing interval
  if (progressPollInterval.current) {
    clearInterval(progressPollInterval.current);
  }

  // Poll every 500ms
  progressPollInterval.current = window.setInterval(() => {
    const status = getGenerationStatus(requestId);
    
    if (status) {
      setPipelineProgress(status.progress || 0);
      setPipelineStep(status.currentStep || 'processing');
      
      // Stop polling when complete or error
      if (status.status === 'completed' || status.status === 'error') {
        if (progressPollInterval.current) {
          clearInterval(progressPollInterval.current);
          progressPollInterval.current = null;
        }
        
        setPipelineStatus(status.status === 'completed' ? 'success' : 'error');
      }
    }
  }, 500);
};

const stopProgressPolling = () => {
  if (progressPollInterval.current) {
    clearInterval(progressPollInterval.current);
    progressPollInterval.current = null;
  }
};
```

### Step 4: Update VoiceUI sendCommand Function

Replace the orchestrateCommand call with the new pipeline:

```tsx
const sendCommand = async () => {
  // ... existing code ...
  
  console.log('[VoiceUI] Starting command processing:', transcript);
  
  // Add request to queue
  const requestId = addRequest(transcript);
  
  // Start progress tracking
  setPipelineStatus('processing');
  setPipelineProgress(0);
  setPipelineStep('normalizing');
  startProgressPolling(requestId);
  
  setPhase('thinking');
  setProcessing(true);
  updateSession({ currentTaskId: requestId, lastPrompt: transcript });
  
  // ... existing UI lock code ...
  
  setTimeout(async () => {
    try {
      updateRequestStatus(requestId, 'Processing');
      setPhase('responding');
      setStreaming(true);
      
      // NEW: Use generateContent instead of orchestrateCommand
      console.log('[VoiceUI] Calling generateContent...');
      const result = await generateContent({
        userInput: transcript,
        requestId,
      });
      
      console.log('[VoiceUI] Generation result:', result);
      
      if (result.success) {
        // Content is already saved by the orchestrator
        console.log('[VoiceUI] Content ID:', result.contentId);
        console.log('[VoiceUI] Pipeline logs:', result.logs);
        
        // Stop progress polling
        stopProgressPolling();
        setPipelineStatus('success');
        setPipelineProgress(100);
        setPipelineStep('completed');
        
        // Stream AI response
        let responseText = result.logs.join('\n');
        streamCleanupRef.current = streamAIResponse(
          transcript,
          (chunk) => {
            responseText += chunk;
            addResponse(responseText);
          },
          () => {
            // onComplete
            updateRequestStatus(requestId, 'Complete');
            setPhase('idle');
            setProcessing(false);
            setStreaming(false);
            updateSession({ currentTaskId: undefined, lastPrompt: null });
            // ... reset UI ...
            streamCleanupRef.current = null;
          },
          (error) => {
            // onError
            console.error('[VoiceUI] Stream error:', error);
            updateRequestStatus(requestId, 'Error', error.message);
            // ... error handling ...
          }
        );
      } else {
        throw new Error(result.error || 'Generation failed');
      }
    } catch (error) {
      console.error('[VoiceUI] Generation failed:', error);
      stopProgressPolling();
      setPipelineStatus('error');
      setPipelineError(error instanceof Error ? error.message : 'Unknown error');
      updateRequestStatus(requestId, 'Error', error instanceof Error ? error.message : 'Unknown error');
      // ... error handling ...
    }
  }, 1200);
};
```

### Step 5: Update Text Mode handleSend Function

Similar changes to the text mode handler:

```tsx
const handleSend = async () => {
  if (!input.trim() || isStreaming) return;

  const command = input.trim();
  console.log('[CommandCenter] Starting command processing:', command);
  
  const requestId = addRequest(command);
  
  // Start progress tracking
  setPipelineStatus('processing');
  setPipelineProgress(0);
  setPipelineStep('normalizing');
  startProgressPolling(requestId);
  
  setProcessing(true);
  updateSession({ currentTaskId: requestId, lastPrompt: command });
  
  addHistory(command, 'text');
  setInput('');
  setIsStreaming(true);
  setStreamingText('');
  
  document.body.style.overflow = 'hidden';
  
  setTimeout(async () => {
    try {
      if (streamCleanupRef.current) {
        streamCleanupRef.current();
        streamCleanupRef.current = null;
      }
      
      updateRequestStatus(requestId, 'Processing');
      setStreaming(true);
      
      // NEW: Use generateContent
      console.log('[CommandCenter] Calling generateContent...');
      const result = await generateContent({
        userInput: command,
        requestId,
      });
      
      if (result.success) {
        stopProgressPolling();
        setPipelineStatus('success');
        setPipelineProgress(100);
        
        // Stream response
        let responseText = result.logs.join('\n');
        // ... streaming logic ...
      } else {
        throw new Error(result.error || 'Generation failed');
      }
    } catch (error) {
      console.error('[CommandCenter] Generation failed:', error);
      stopProgressPolling();
      setPipelineStatus('error');
      setPipelineError(error instanceof Error ? error.message : 'Unknown error');
      // ... error handling ...
    }
  }, 500);
};
```

### Step 6: Add Progress Tracker to UI

Add the progress tracker component to both voice and text modes:

**For Voice Mode** (inside VoiceUI component):
```tsx
{/* Processing Card */}
{isResponding && (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="w-full mt-4"
  >
    <ProgressTracker
      currentStep={pipelineStep}
      progress={pipelineProgress}
      status={pipelineStatus}
      error={pipelineError}
    />
  </motion.div>
)}
```

**For Text Mode** (after Send button):
```tsx
{/* Progress Tracker */}
{(isStreaming || pipelineStatus === 'processing') && (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className="mt-4"
  >
    <ProgressTracker
      currentStep={pipelineStep}
      progress={pipelineProgress}
      status={pipelineStatus}
      error={pipelineError}
    />
  </motion.div>
)}
```

### Step 7: Cleanup on Unmount

Add cleanup for progress polling:

```tsx
useEffect(() => {
  return () => {
    stopProgressPolling();
    // ... existing cleanup ...
  };
}, []);
```

---

## Phase 3: Request Tiles Enhancement

### File to Update: `src/components/ui/RequestItem.tsx`

### Step 1: Add Imports

```tsx
import { ProgressBadge } from './ProgressBadge';
import { RefreshCw } from 'lucide-react';
```

### Step 2: Add Retry Function

```tsx
const handleRetry = async () => {
  const { retryGeneration } = await import('../../services/orchestratorService');
  
  try {
    setRetrying(true);
    const result = await retryGeneration(request.id);
    
    if (result.success) {
      console.log('Retry successful:', result.contentId);
    } else {
      console.error('Retry failed:', result.error);
    }
  } catch (error) {
    console.error('Retry error:', error);
  } finally {
    setRetrying(false);
  }
};
```

### Step 3: Add Progress Badge to Request Tile

```tsx
<div className="flex items-center gap-2">
  <StatusBadge status={request.status} />
  
  {/* NEW: Add progress badge for in-progress requests */}
  {request.status === 'Processing' && (
    <ProgressBadge
      progress={request.progress || 0}
      status="processing"
    />
  )}
</div>
```

### Step 4: Add Retry Button

```tsx
{request.status === 'Error' && (
  <button
    onClick={handleRetry}
    disabled={retrying}
    className="flex items-center gap-1 px-2 py-1 text-xs text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
  >
    <RefreshCw className={`w-3 h-3 ${retrying ? 'animate-spin' : ''}`} />
    Retry
  </button>
)}
```

### Step 5: Show Enrichment Sources

Add a collapsible section to show enrichment sources:

```tsx
{request.content?.metadata?.enrichment_sources && (
  <details className="mt-2">
    <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
      View enrichment sources
    </summary>
    <div className="mt-2 p-2 bg-gray-50 rounded-md text-xs">
      {Object.entries(request.content.metadata.enrichment_sources).map(([field, source]) => (
        <div key={field} className="flex justify-between">
          <span className="font-medium">{field}:</span>
          <span className="text-gray-600">{source}</span>
        </div>
      ))}
    </div>
  </details>
)}
```

### Step 6: Show Generation Logs

Add a logs viewer:

```tsx
{request.logs && request.logs.length > 0 && (
  <details className="mt-2">
    <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
      View generation logs ({request.logs.length})
    </summary>
    <div className="mt-2 p-2 bg-gray-50 rounded-md text-xs space-y-1">
      {request.logs.map((log, index) => (
        <div key={index} className="text-gray-700">
          {log}
        </div>
      ))}
    </div>
  </details>
)}
```

---

## Phase 4: Error Handling UI

### Create ErrorDialog Component

**File**: `src/components/ui/ErrorDialog.tsx`

```tsx
import { motion } from 'framer-motion';
import { AlertCircle, X } from 'lucide-react';

export interface ErrorDialogProps {
  error: string;
  onRetry?: () => void;
  onDismiss: () => void;
  suggestions?: string[];
}

export function ErrorDialog({
  error,
  onRetry,
  onDismiss,
  suggestions = [],
}: ErrorDialogProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm"
    >
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-50 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">
                Generation Failed
              </h3>
              <p className="text-sm text-gray-500">
                We encountered an issue
              </p>
            </div>
          </div>
          <button
            onClick={onDismiss}
            className="p-1 hover:bg-gray-100 rounded-md"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Error Message */}
        <div className="mb-4 p-3 bg-red-50 rounded-lg">
          <p className="text-sm text-red-800">{error}</p>
        </div>

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-700 mb-2">
              Suggestions:
            </p>
            <ul className="space-y-1">
              {suggestions.map((suggestion, index) => (
                <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2">
          {onRetry && (
            <button
              onClick={onRetry}
              className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
            >
              Retry
            </button>
          )}
          <button
            onClick={onDismiss}
            className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
          >
            Dismiss
          </button>
        </div>
      </div>
    </motion.div>
  );
}
```

### Use ErrorDialog in CommandCenter

```tsx
const [showErrorDialog, setShowErrorDialog] = useState(false);
const [errorDetails, setErrorDetails] = useState<{
  message: string;
  suggestions: string[];
}>({ message: '', suggestions: [] });

// When error occurs:
setPipelineStatus('error');
setPipelineError(errorMessage);
setErrorDetails({
  message: errorMessage,
  suggestions: [
    'Try rephrasing your request with more details',
    'Check that all required information is provided',
    'Contact support if the issue persists',
  ],
});
setShowErrorDialog(true);

// In render:
{showErrorDialog && (
  <ErrorDialog
    error={errorDetails.message}
    suggestions={errorDetails.suggestions}
    onRetry={() => {
      setShowErrorDialog(false);
      // Trigger retry
      handleRetry();
    }}
    onDismiss={() => setShowErrorDialog(false)}
  />
)}
```

---

## Phase 5: Store Integration

### Update Request Interface

**File**: `src/store/commandStore.ts`

Add new fields to Request interface:

```tsx
export interface Request {
  id: string;
  userMessage: string;
  contentType?: ContentType;
  status: string;
  timestamp: string;
  errorMessage?: string;
  content?: BaseContent;
  // NEW FIELDS:
  progress?: number;
  currentStep?: string;
  logs?: string[];
  enrichmentSources?: Record<string, string>;
}
```

### Update Store Actions

Add action to update progress:

```tsx
updateRequestProgress: (requestId: string, progress: number, step: string) => 
  set((state) => ({
    requests: state.requests.map((req) =>
      req.id === requestId
        ? { ...req, progress, currentStep: step }
        : req
    ),
  })),

addRequestLogs: (requestId: string, logs: string[]) =>
  set((state) => ({
    requests: state.requests.map((req) =>
      req.id === requestId
        ? { ...req, logs: [...(req.logs || []), ...logs] }
        : req
    ),
  })),
```

---

## Testing Checklist

### Manual Testing

- [ ] Test CMA generation with full input
- [ ] Test CMA generation with minimal input (enrichment should kick in)
- [ ] Test error handling (disconnect backend)
- [ ] Test retry functionality
- [ ] Test progress tracking visibility
- [ ] Test voice mode with new orchestrator
- [ ] Test text mode with new orchestrator
- [ ] Verify enrichment sources are displayed
- [ ] Verify generation logs are shown
- [ ] Test progress polling cleanup on unmount

### Integration Testing

- [ ] Verify content is saved to store correctly
- [ ] Verify request status updates properly
- [ ] Verify progress updates in real-time
- [ ] Verify error states display correctly
- [ ] Verify retry regenerates content

---

## Rollout Strategy

### Phase 1: Soft Launch
1. Add feature flag: `VITE_USE_NEW_ORCHESTRATOR=true`
2. Only enable for specific users
3. Monitor for errors

### Phase 2: A/B Test
1. 50% of users get new orchestrator
2. Track success rates
3. Compare performance metrics

### Phase 3: Full Rollout
1. Enable for all users
2. Remove legacy orchestrator
3. Clean up old code

---

## Performance Metrics to Track

1. **Pipeline Duration**:
   - Target: < 4 seconds total
   - Track each step duration

2. **Success Rate**:
   - Target: > 95%
   - Track failure reasons

3. **Enrichment Quality**:
   - Track enrichment confidence scores
   - Track user corrections

4. **User Experience**:
   - Track time to first interaction
   - Track completion rates
   - Track retry rates

---

## Next Steps

1. ✅ Create ProgressTracker component
2. ⏳ Add state variables to CommandCenter
3. ⏳ Implement progress polling
4. ⏳ Update voice command handler
5. ⏳ Update text command handler
6. ⏳ Add ProgressTracker to UI
7. ⏳ Update RequestItem component
8. ⏳ Create ErrorDialog component
9. ⏳ Update store interface
10. ⏳ Test end-to-end

---

## Estimated Time

- **Phase 2 (CommandCenter)**: 1-2 hours
- **Phase 3 (Request Tiles)**: 30 minutes
- **Phase 4 (Error Handling)**: 30 minutes
- **Phase 5 (Store Updates)**: 15 minutes
- **Testing**: 1 hour

**Total**: ~3-4 hours

---

## Support

For questions or issues during integration, refer to:
- `docs/track3-summary.md` - Orchestrator API documentation
- `docs/track3-architecture.md` - Pipeline architecture
- `docs/TRACK3_COMPLETE.md` - Implementation summary
