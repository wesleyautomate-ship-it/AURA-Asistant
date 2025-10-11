/**
 * Aura v3.0 Intelligent Task Recovery System
 * 
 * Enhanced recovery beyond current lifecycle management:
 * ✅ Detect stuck tasks on startup and during runtime
 * ✅ Offer retry/continue buttons with visual indicators  
 * ✅ Auto-resume SSE streams with session tokens
 * ✅ Context-aware recovery with user prompts
 * ✅ Smart recovery strategies per task type
 * ✅ Recovery history and analytics
 * 
 * Features:
 * - Startup scan for abandoned operations
 * - Runtime monitoring for stuck tasks
 * - Visual recovery UI with user choices
 * - Automatic session token restoration
 * - Intelligent retry strategies
 * - Recovery success tracking
 */

import { useCommandStore } from '../store/commandStore';
import backgroundContinuityService from './backgroundContinuity';

// Configuration for task recovery
const RECOVERY_CONFIG = {
  DETECTION: {
    STARTUP_SCAN_DELAY: 2000, // 2 seconds after startup
    STUCK_TASK_TIMEOUT: 300000, // 5 minutes for stuck detection
    ABANDONED_TASK_TIMEOUT: 1800000, // 30 minutes for abandoned detection
    HEARTBEAT_TIMEOUT: 60000, // 1 minute for heartbeat timeout
  },
  RECOVERY: {
    AUTO_RECOVER_THRESHOLD: 3, // Auto-recover tasks with <= 3 failures
    MAX_RECOVERY_ATTEMPTS: 5,
    RECOVERY_DELAY: 5000, // 5 seconds between recovery attempts
    SESSION_TOKEN_TTL: 3600000, // 1 hour for session tokens
  },
  UI: {
    SHOW_RECOVERY_BANNER: true,
    AUTO_HIDE_SUCCESS: 5000, // Hide success message after 5 seconds
    BATCH_RECOVERY_LIMIT: 10, // Max tasks to show in batch recovery
  }
};

class TaskRecoveryService {
  constructor() {
    this.isInitialized = false;
    this.detectionInterval = null;
    this.recoveryQueue = [];
    this.recoveryHistory = [];
    this.sessionTokens = new Map();
    this.recoveryCallbacks = new Map();
    
    this.bindMethods();
  }

  bindMethods() {
    this.detectStuckTasks = this.detectStuckTasks.bind(this);
    this.handleRecoveryAction = this.handleRecoveryAction.bind(this);
    this.processRecoveryQueue = this.processRecoveryQueue.bind(this);
  }

  async initialize() {
    if (this.isInitialized) {
      console.log('[TaskRecovery] Already initialized');
      return;
    }

    console.log('[TaskRecovery] Initializing task recovery system');
    this.isInitialized = true;

    // Delay startup scan to let other systems initialize
    setTimeout(() => {
      this.performStartupScan();
    }, RECOVERY_CONFIG.DETECTION.STARTUP_SCAN_DELAY);

    // Start runtime monitoring
    this.startRuntimeMonitoring();

    // Register with command store
    this.registerWithStore();

    console.log('[TaskRecovery] Task recovery system initialized');
  }

  destroy() {
    if (!this.isInitialized) return;

    console.log('[TaskRecovery] Destroying task recovery system');
    this.stopRuntimeMonitoring();
    this.clearRecoveryQueue();
    this.sessionTokens.clear();
    this.recoveryCallbacks.clear();
    this.isInitialized = false;
  }

  async performStartupScan() {
    console.log('[TaskRecovery] Performing startup scan for abandoned tasks');
    
    const store = useCommandStore.getState();
    const session = store.session;
    
    if (!session) {
      console.log('[TaskRecovery] No session found, skipping startup scan');
      return;
    }

    const now = Date.now();
    const queuedOps = session.queuedOperations || [];
    const abandonedTasks = [];
    const stuckTasks = [];

    // Analyze each queued operation
    for (const operation of queuedOps) {
      const timeSinceUpdate = now - (operation.lastUpdated || operation.createdAt || 0);
      
      if (operation.status === 'processing') {
        if (timeSinceUpdate > RECOVERY_CONFIG.DETECTION.STUCK_TASK_TIMEOUT) {
          stuckTasks.push({ ...operation, reason: 'stuck_processing', timeSinceUpdate });
        }
      } else if (operation.status === 'pending') {
        if (timeSinceUpdate > RECOVERY_CONFIG.DETECTION.ABANDONED_TASK_TIMEOUT) {
          abandonedTasks.push({ ...operation, reason: 'abandoned_pending', timeSinceUpdate });
        }
      } else if (operation.status === 'failed') {
        const retryCount = operation.retryCount || 0;
        if (retryCount < RECOVERY_CONFIG.RECOVERY.MAX_RECOVERY_ATTEMPTS) {
          abandonedTasks.push({ ...operation, reason: 'failed_recoverable', timeSinceUpdate });
        }
      }
    }

    // Check for session continuity issues
    const sessionAge = now - (session.createdAt || 0);
    const lastActiveAge = now - (session.lastActiveAt || 0);
    
    let sessionRecoveryNeeded = false;
    if (session.isRecording && lastActiveAge > RECOVERY_CONFIG.DETECTION.HEARTBEAT_TIMEOUT) {
      sessionRecoveryNeeded = true;
    }

    // Process findings
    const totalIssues = abandonedTasks.length + stuckTasks.length + (sessionRecoveryNeeded ? 1 : 0);
    
    if (totalIssues === 0) {
      console.log('[TaskRecovery] Startup scan complete - no issues found');
      return;
    }

    console.log(`[TaskRecovery] Startup scan found ${totalIssues} issues:`, {
      abandoned: abandonedTasks.length,
      stuck: stuckTasks.length,
      sessionRecovery: sessionRecoveryNeeded
    });

    // Create recovery plan
    const recoveryPlan = this.createRecoveryPlan([...abandonedTasks, ...stuckTasks], sessionRecoveryNeeded);
    
    // Show recovery UI or auto-recover
    if (recoveryPlan.autoRecoverable.length > 0) {
      await this.performAutoRecovery(recoveryPlan.autoRecoverable);
    }
    
    if (recoveryPlan.userActionRequired.length > 0) {
      this.showRecoveryUI(recoveryPlan.userActionRequired);
    }

    if (sessionRecoveryNeeded) {
      await this.recoverSession();
    }
  }

  createRecoveryPlan(tasks, sessionRecoveryNeeded = false) {
    const autoRecoverable = [];
    const userActionRequired = [];

    for (const task of tasks) {
      const failureCount = this.getTaskFailureCount(task.id);
      
      if (failureCount <= RECOVERY_CONFIG.RECOVERY.AUTO_RECOVER_THRESHOLD) {
        // Auto-recoverable: low failure count
        autoRecoverable.push({
          ...task,
          recoveryStrategy: this.determineRecoveryStrategy(task),
          priority: this.calculateRecoveryPriority(task)
        });
      } else {
        // Requires user action: high failure count
        userActionRequired.push({
          ...task,
          recoveryOptions: this.getRecoveryOptions(task),
          reason: `Failed ${failureCount} times - manual intervention needed`
        });
      }
    }

    return {
      autoRecoverable: autoRecoverable.sort((a, b) => b.priority - a.priority),
      userActionRequired: userActionRequired.slice(0, RECOVERY_CONFIG.UI.BATCH_RECOVERY_LIMIT),
      sessionRecoveryNeeded
    };
  }

  determineRecoveryStrategy(task) {
    switch (task.type) {
      case 'transcribe':
        return task.reason === 'stuck_processing' ? 'restart_transcription' : 'retry_transcription';
      case 'generate_response':
        return 'restart_with_context';
      case 'save_audio':
        return 'retry_save';
      default:
        return 'generic_retry';
    }
  }

  calculateRecoveryPriority(task) {
    let priority = 50; // Base priority
    
    // Higher priority for more recent tasks
    const age = Date.now() - (task.createdAt || 0);
    if (age < 300000) priority += 30; // Less than 5 minutes
    else if (age < 1800000) priority += 15; // Less than 30 minutes
    
    // Higher priority for user-initiated tasks
    if (task.userInitiated) priority += 20;
    
    // Higher priority for critical task types
    if (task.type === 'transcribe') priority += 15;
    if (task.type === 'generate_response') priority += 10;
    
    // Lower priority for failed tasks
    const failureCount = this.getTaskFailureCount(task.id);
    priority -= failureCount * 10;
    
    return Math.max(0, Math.min(100, priority));
  }

  getRecoveryOptions(task) {
    const options = [
      {
        id: 'retry',
        label: 'Retry Task',
        description: 'Attempt to run the task again',
        action: 'retry'
      },
      {
        id: 'restart',
        label: 'Restart Fresh',
        description: 'Clear task state and start over',
        action: 'restart'
      },
      {
        id: 'skip',
        label: 'Skip Task',
        description: 'Mark as skipped and continue',
        action: 'skip'
      },
      {
        id: 'delete',
        label: 'Remove Task',
        description: 'Delete this task permanently',
        action: 'delete'
      }
    ];

    // Add task-specific options
    if (task.type === 'transcribe') {
      options.splice(1, 0, {
        id: 'manual_transcript',
        label: 'Manual Entry',
        description: 'Enter transcript manually',
        action: 'manual_entry'
      });
    }

    return options;
  }

  async performAutoRecovery(tasks) {
    console.log(`[TaskRecovery] Performing auto-recovery for ${tasks.length} tasks`);
    
    const store = useCommandStore.getState();
    let recoveredCount = 0;
    let failedCount = 0;

    for (const task of tasks) {
      try {
        console.log(`[TaskRecovery] Auto-recovering task: ${task.id} (${task.recoveryStrategy})`);
        
        const success = await this.executeRecoveryStrategy(task, task.recoveryStrategy);
        
        if (success) {
          recoveredCount++;
          this.recordRecoverySuccess(task.id, 'auto', task.recoveryStrategy);
          
          // Update task status
          store.updateQueuedOperation(task.id, {
            status: 'pending',
            recoveredAt: Date.now(),
            recoveryStrategy: task.recoveryStrategy,
            autoRecovered: true
          });
        } else {
          failedCount++;
          this.recordRecoveryFailure(task.id, 'auto', 'strategy_failed');
        }
        
        // Delay between recovery attempts
        await this.delay(RECOVERY_CONFIG.RECOVERY.RECOVERY_DELAY);
        
      } catch (error) {
        console.error(`[TaskRecovery] Auto-recovery failed for task ${task.id}:`, error);
        failedCount++;
        this.recordRecoveryFailure(task.id, 'auto', error.message);
      }
    }

    if (recoveredCount > 0) {
      store.addContext(`Auto-recovered ${recoveredCount} tasks successfully`);
      this.showRecoveryNotification(`✅ Auto-recovered ${recoveredCount} tasks`, 'success');
    }

    if (failedCount > 0) {
      console.warn(`[TaskRecovery] ${failedCount} auto-recovery attempts failed`);
    }
  }

  async executeRecoveryStrategy(task, strategy) {
    const store = useCommandStore.getState();
    
    switch (strategy) {
      case 'restart_transcription':
        // Clear processing state and restart
        store.updateQueuedOperation(task.id, {
          status: 'pending',
          processingStart: null,
          lastError: null,
          retryCount: (task.retryCount || 0) + 1
        });
        return true;
        
      case 'retry_transcription':
        // Simple retry
        store.updateQueuedOperation(task.id, {
          status: 'pending',
          retryCount: (task.retryCount || 0) + 1,
          nextRetry: Date.now() + 1000
        });
        return true;
        
      case 'restart_with_context':
        // Restart with fresh context
        const context = store.getRecentContext();
        store.updateQueuedOperation(task.id, {
          status: 'pending',
          data: { ...task.data, context },
          retryCount: (task.retryCount || 0) + 1
        });
        return true;
        
      case 'retry_save':
        // Retry audio save
        store.updateQueuedOperation(task.id, {
          status: 'pending',
          retryCount: (task.retryCount || 0) + 1
        });
        return true;
        
      case 'generic_retry':
      default:
        // Generic retry approach
        store.updateQueuedOperation(task.id, {
          status: 'pending',
          retryCount: (task.retryCount || 0) + 1,
          lastRecovery: Date.now()
        });
        return true;
    }
  }

  showRecoveryUI(tasks) {
    console.log(`[TaskRecovery] Showing recovery UI for ${tasks.length} tasks`);
    
    const store = useCommandStore.getState();
    
    // Add recovery UI state to store
    store.updateSession({
      recoveryUI: {
        visible: true,
        tasks: tasks,
        timestamp: Date.now()
      }
    });

    // Auto-hide after reasonable time if no user action
    setTimeout(() => {
      const currentRecoveryUI = store.session?.recoveryUI;
      if (currentRecoveryUI && currentRecoveryUI.timestamp === Date.now()) {
        this.hideRecoveryUI();
      }
    }, 300000); // 5 minutes
  }

  hideRecoveryUI() {
    const store = useCommandStore.getState();
    store.updateSession({
      recoveryUI: { visible: false, tasks: [] }
    });
  }

  async handleRecoveryAction(taskId, action, options = {}) {
    console.log(`[TaskRecovery] Handling recovery action: ${action} for task: ${taskId}`);
    
    const store = useCommandStore.getState();
    const task = (store.session?.queuedOperations || []).find(op => op.id === taskId);
    
    if (!task) {
      console.error(`[TaskRecovery] Task not found: ${taskId}`);
      return false;
    }

    try {
      let success = false;
      
      switch (action) {
        case 'retry':
          success = await this.executeRecoveryStrategy(task, 'generic_retry');
          break;
          
        case 'restart':
          store.updateQueuedOperation(taskId, {
            status: 'pending',
            processingStart: null,
            lastError: null,
            retryCount: 0,
            restarted: true,
            restartedAt: Date.now()
          });
          success = true;
          break;
          
        case 'skip':
          store.updateQueuedOperation(taskId, {
            status: 'skipped',
            skippedAt: Date.now(),
            skipReason: options.reason || 'User choice'
          });
          success = true;
          break;
          
        case 'delete':
          store.removeQueuedOperation(taskId);
          success = true;
          break;
          
        case 'manual_entry':
          if (options.transcript) {
            store.updateQueuedOperation(taskId, {
              status: 'completed',
              result: { transcript: options.transcript, manual: true },
              completedAt: Date.now()
            });
            store.addContext(options.transcript);
            success = true;
          }
          break;
          
        default:
          console.error(`[TaskRecovery] Unknown recovery action: ${action}`);
          return false;
      }
      
      if (success) {
        this.recordRecoverySuccess(taskId, 'manual', action);
        this.showRecoveryNotification(`✅ Task ${action}ed successfully`, 'success');
        
        // Remove task from recovery UI
        this.removeTaskFromRecoveryUI(taskId);
      }
      
      return success;
      
    } catch (error) {
      console.error(`[TaskRecovery] Recovery action failed:`, error);
      this.recordRecoveryFailure(taskId, 'manual', error.message);
      this.showRecoveryNotification(`❌ Recovery action failed: ${error.message}`, 'error');
      return false;
    }
  }

  async recoverSession() {
    console.log('[TaskRecovery] Recovering session state');
    
    const store = useCommandStore.getState();
    
    try {
      // Stop any stuck recording
      if (store.session?.isRecording) {
        console.log('[TaskRecovery] Stopping stuck recording session');
        store.stopRecording();
      }
      
      // Reset processing flags
      store.updateSession({
        isProcessing: false,
        isStreaming: false,
        currentTranscript: null,
        currentResponse: null,
        lastActiveAt: Date.now()
      });
      
      // Attempt to restore SSE connection
      if (backgroundContinuityService) {
        backgroundContinuityService.forceReconnect();
      }
      
      // Restore session tokens if available
      await this.restoreSessionTokens();
      
      this.showRecoveryNotification('✅ Session recovered successfully', 'success');
      return true;
      
    } catch (error) {
      console.error('[TaskRecovery] Session recovery failed:', error);
      this.showRecoveryNotification(`❌ Session recovery failed: ${error.message}`, 'error');
      return false;
    }
  }

  async restoreSessionTokens() {
    const store = useCommandStore.getState();
    const sessionId = store.session?.id;
    
    if (!sessionId) return;
    
    const tokenKey = `session_token_${sessionId}`;
    const savedToken = localStorage.getItem(tokenKey);
    
    if (savedToken) {
      try {
        const tokenData = JSON.parse(savedToken);
        
        // Check if token is still valid
        if (Date.now() - tokenData.createdAt < RECOVERY_CONFIG.RECOVERY.SESSION_TOKEN_TTL) {
          this.sessionTokens.set(sessionId, tokenData.token);
          console.log('[TaskRecovery] Session token restored');
          return true;
        } else {
          localStorage.removeItem(tokenKey);
          console.log('[TaskRecovery] Expired session token removed');
        }
      } catch (error) {
        console.error('[TaskRecovery] Failed to parse session token:', error);
        localStorage.removeItem(tokenKey);
      }
    }
    
    return false;
  }

  startRuntimeMonitoring() {
    if (this.detectionInterval) return;
    
    console.log('[TaskRecovery] Starting runtime task monitoring');
    
    this.detectionInterval = setInterval(() => {
      this.detectStuckTasks();
    }, 60000); // Check every minute
  }

  stopRuntimeMonitoring() {
    if (this.detectionInterval) {
      clearInterval(this.detectionInterval);
      this.detectionInterval = null;
      console.log('[TaskRecovery] Stopped runtime monitoring');
    }
  }

  detectStuckTasks() {
    const store = useCommandStore.getState();
    const queuedOps = store.session?.queuedOperations || [];
    const now = Date.now();
    const stuckTasks = [];

    for (const operation of queuedOps) {
      if (operation.status === 'processing') {
        const processTime = now - (operation.processingStart || 0);
        
        if (processTime > RECOVERY_CONFIG.DETECTION.STUCK_TASK_TIMEOUT) {
          stuckTasks.push({
            ...operation,
            stuckDuration: processTime,
            detectedAt: now
          });
        }
      }
    }

    if (stuckTasks.length > 0) {
      console.warn(`[TaskRecovery] Detected ${stuckTasks.length} stuck tasks`);
      
      // Add to recovery queue for processing
      for (const task of stuckTasks) {
        this.addToRecoveryQueue(task, 'runtime_detection');
      }
    }
  }

  addToRecoveryQueue(task, reason) {
    const existingIndex = this.recoveryQueue.findIndex(item => item.task.id === task.id);
    
    if (existingIndex >= 0) {
      // Update existing entry
      this.recoveryQueue[existingIndex] = { task, reason, addedAt: Date.now() };
    } else {
      // Add new entry
      this.recoveryQueue.push({ task, reason, addedAt: Date.now() });
    }
    
    // Process recovery queue
    setTimeout(() => this.processRecoveryQueue(), 1000);
  }

  async processRecoveryQueue() {
    if (this.recoveryQueue.length === 0) return;
    
    console.log(`[TaskRecovery] Processing recovery queue with ${this.recoveryQueue.length} items`);
    
    const item = this.recoveryQueue.shift();
    const plan = this.createRecoveryPlan([item.task]);
    
    if (plan.autoRecoverable.length > 0) {
      await this.performAutoRecovery(plan.autoRecoverable);
    } else if (plan.userActionRequired.length > 0) {
      this.showRecoveryUI(plan.userActionRequired);
    }
  }

  clearRecoveryQueue() {
    this.recoveryQueue = [];
  }

  removeTaskFromRecoveryUI(taskId) {
    const store = useCommandStore.getState();
    const recoveryUI = store.session?.recoveryUI;
    
    if (recoveryUI && recoveryUI.tasks) {
      const filteredTasks = recoveryUI.tasks.filter(task => task.id !== taskId);
      
      if (filteredTasks.length === 0) {
        this.hideRecoveryUI();
      } else {
        store.updateSession({
          recoveryUI: { ...recoveryUI, tasks: filteredTasks }
        });
      }
    }
  }

  getTaskFailureCount(taskId) {
    return this.recoveryHistory.filter(
      entry => entry.taskId === taskId && entry.result === 'failure'
    ).length;
  }

  recordRecoverySuccess(taskId, type, strategy) {
    this.recoveryHistory.push({
      taskId,
      type, // 'auto' or 'manual'
      strategy,
      result: 'success',
      timestamp: Date.now()
    });
    
    // Keep history limited
    if (this.recoveryHistory.length > 1000) {
      this.recoveryHistory = this.recoveryHistory.slice(-500);
    }
  }

  recordRecoveryFailure(taskId, type, error) {
    this.recoveryHistory.push({
      taskId,
      type,
      error,
      result: 'failure',
      timestamp: Date.now()
    });
  }

  showRecoveryNotification(message, type) {
    // This would integrate with your notification system
    console.log(`[TaskRecovery] ${type.toUpperCase()}: ${message}`);
    
    const store = useCommandStore.getState();
    store.addContext(message);
    
    if (type === 'success' && RECOVERY_CONFIG.UI.AUTO_HIDE_SUCCESS) {
      setTimeout(() => {
        // Auto-hide success notifications
      }, RECOVERY_CONFIG.UI.AUTO_HIDE_SUCCESS);
    }
  }

  registerWithStore() {
    const store = useCommandStore.getState();
    
    // Add recovery methods to store
    store.taskRecovery = {
      handleRecoveryAction: this.handleRecoveryAction.bind(this),
      hideRecoveryUI: this.hideRecoveryUI.bind(this),
      getRecoveryHistory: () => this.recoveryHistory,
      getRecoveryStats: () => this.getRecoveryStats()
    };
  }

  getRecoveryStats() {
    const total = this.recoveryHistory.length;
    const successful = this.recoveryHistory.filter(entry => entry.result === 'success').length;
    const auto = this.recoveryHistory.filter(entry => entry.type === 'auto').length;
    const manual = this.recoveryHistory.filter(entry => entry.type === 'manual').length;
    
    return {
      total,
      successful,
      failed: total - successful,
      successRate: total > 0 ? Math.round((successful / total) * 100) : 0,
      auto,
      manual
    };
  }

  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Public API
  getStatus() {
    return {
      isInitialized: this.isInitialized,
      recoveryQueueLength: this.recoveryQueue.length,
      recoveryHistoryLength: this.recoveryHistory.length,
      sessionTokensCount: this.sessionTokens.size,
      stats: this.getRecoveryStats()
    };
  }
}

// Create singleton instance
const taskRecoveryService = new TaskRecoveryService();

export default taskRecoveryService;

// React hook for easy integration
export const useTaskRecovery = () => {
  const [status, setStatus] = React.useState(taskRecoveryService.getStatus());
  const store = useCommandStore();
  
  React.useEffect(() => {
    // Initialize service
    taskRecoveryService.initialize();
    
    // Update status periodically
    const interval = setInterval(() => {
      setStatus(taskRecoveryService.getStatus());
    }, 10000);
    
    // Cleanup on unmount
    return () => {
      clearInterval(interval);
      taskRecoveryService.destroy();
    };
  }, []);
  
  const recoveryUI = store.session?.recoveryUI;
  
  return {
    ...status,
    recoveryUI: recoveryUI?.visible ? recoveryUI : null,
    handleRecoveryAction: store.taskRecovery?.handleRecoveryAction,
    hideRecoveryUI: store.taskRecovery?.hideRecoveryUI
  };
};