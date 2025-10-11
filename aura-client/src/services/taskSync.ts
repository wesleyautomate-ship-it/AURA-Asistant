import { useCommandStore } from '../store/commandStore';
import { TASK_LIFECYCLE_CONFIG } from '../config/taskLifecycle';

let intervalId: number | null = null;
let watchdogId: number | null = null;
let retryCount = 0;
const MAX_RETRIES = 3;
const SYNC_INTERVAL = 10000; // 10 seconds
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BACKEND_ENABLED = import.meta.env.VITE_BACKEND_ENABLED !== 'false'; // Disable with VITE_BACKEND_ENABLED=false

export interface TaskSyncResponse {
  id: string;
  title?: string;
  command?: string;
  status: string;
  type?: string;
  created_at: string;
  metadata?: any;
}

/**
 * Calculate exponential backoff delay
 */
function getBackoffDelay(attempt: number): number {
  return Math.min(1000 * Math.pow(2, attempt), 30000); // Max 30 seconds
}

/**
 * Start periodic task synchronization with the backend
 */
export function startTaskSync(): void {
  if (!BACKEND_ENABLED) {
    console.log('[TaskSync] Backend disabled, skipping task sync');
    return;
  }

  const store = useCommandStore.getState();

  if (intervalId) {
    console.log('[TaskSync] Sync already running, stopping previous instance');
    clearInterval(intervalId);
  }

  console.log('[TaskSync] Starting periodic task sync...');

  // Start lifecycle watchdog
  startLifecycleWatchdog();

  const syncTasks = async () => {
    try {
      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken') || import.meta.env.VITE_DEV_AUTH_TOKEN || 'mock-token'}`,
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/tasks/sync`, {
        method: 'GET',
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch tasks: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // ✅ Guard against invalid or empty responses
      if (!data || typeof data !== 'object') {
        console.warn('[TaskSync] Invalid or empty response format:', data);
        return;
      }
      
      // Extract tasks array (handle both {tasks: [...]} and direct array responses)
      const tasks = data.tasks || data;

      if (!Array.isArray(tasks)) {
        console.warn('[TaskSync] Invalid response format - expected array:', data);
        return;
      }
      
      store.syncTasks(tasks);
      console.log(`[TaskSync] Synced ${tasks.length} tasks from backend`);
      retryCount = 0; // Reset retry count on success
      
      // Auto-recovery: Check for incomplete mock/offline tasks
      performAutoRecovery(tasks);
    } catch (err: any) {
      console.warn('[TaskSync] Sync failed:', err.message || err);
      
      // Log detailed error information for debugging
      if (err.response) {
        try {
          const errorText = await err.response.text();
          console.warn('[TaskSync] Server response:', {
            status: err.response.status,
            statusText: err.response.statusText,
            body: errorText
          });
        } catch (textErr) {
          console.warn('[TaskSync] Could not read error response body');
        }
      }
      
      retryCount++;

      if (retryCount <= MAX_RETRIES) {
        const delay = getBackoffDelay(retryCount);
        console.log(`[TaskSync] Retrying in ${delay}ms (attempt ${retryCount}/${MAX_RETRIES})`);
        
        setTimeout(() => {
          if (intervalId) { // Only retry if sync is still active
            syncTasks();
          }
        }, delay);
      } else {
        console.error('[TaskSync] Max retries exceeded, will continue on next interval');
        retryCount = 0; // Reset for next interval
      }
    }
  };

  // Initial sync
  syncTasks();

  // Set up periodic sync
  intervalId = setInterval(syncTasks, SYNC_INTERVAL);
}

/**
 * Stop task synchronization
 */
export function stopTaskSync(): void {
  if (intervalId) {
    clearInterval(intervalId);
    console.log('[TaskSync] Stopped periodic task sync');
    intervalId = null;
    retryCount = 0;
  }
  
  if (watchdogId) {
    clearInterval(watchdogId);
    console.log('[TaskSync] Stopped lifecycle watchdog');
    watchdogId = null;
  }
}

/**
 * Check if task sync is currently active
 */
export function isTaskSyncActive(): boolean {
  return intervalId !== null;
}

/**
 * Manually trigger a task sync (useful for immediate updates)
 */
export async function triggerTaskSync(): Promise<void> {
  const store = useCommandStore.getState();

  try {
    console.log('[TaskSync] Manual sync triggered');
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('authToken') || import.meta.env.VITE_DEV_AUTH_TOKEN || 'mock-token'}`,
    };

    const response = await fetch(`${API_BASE_URL}/api/v1/tasks/sync`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch tasks: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    // ✅ Guard against invalid or empty responses
    if (!data || typeof data !== 'object') {
      console.warn('[TaskSync] Invalid or empty response format:', data);
      return;
    }
    
    // Extract tasks array (handle both {tasks: [...]} and direct array responses)
    const tasks = data.tasks || data;

    if (!Array.isArray(tasks)) {
      console.warn('[TaskSync] Invalid response format - expected array:', data);
      return;
    }
    
    store.syncTasks(tasks);
    console.log(`[TaskSync] Manual sync completed: ${tasks.length} tasks`);
  } catch (err) {
    console.error('[TaskSync] Manual sync failed:', err);
    throw err;
  }
}

/**
 * Start the lifecycle watchdog timer
 */
function startLifecycleWatchdog(): void {
  if (watchdogId) {
    clearInterval(watchdogId);
  }
  
  console.log('[TaskSync] Starting lifecycle watchdog...');
  
  const runWatchdog = () => {
    const store = useCommandStore.getState();
    const result = store.checkStaleTasks();
    
    if (result.updated > 0) {
      console.log(`[TaskSync] Watchdog auto-resolved ${result.updated} stale task(s):`, result.staleTaskIds);
    }
  };
  
  // Run immediately, then on interval
  runWatchdog();
  watchdogId = setInterval(runWatchdog, TASK_LIFECYCLE_CONFIG.WATCHDOG_INTERVAL);
}

/**
 * Perform auto-recovery checks after sync
 */
function performAutoRecovery(backendTasks: TaskSyncResponse[]): void {
  const store = useCommandStore.getState();
  const localTasks = store.requests;
  
  // Check for local tasks that don't exist on backend (mock/offline created)
  const orphanedTasks = localTasks.filter(localTask => 
    !backendTasks.find(backendTask => backendTask.id === localTask.id) &&
    (localTask.status === 'Pending' || localTask.status === 'Processing')
  );
  
  if (orphanedTasks.length > 0) {
    console.warn(`[TaskSync] Found ${orphanedTasks.length} orphaned local tasks, auto-resolving...`);
    
    orphanedTasks.forEach(task => {
      // Mark orphaned tasks as complete if they're older than 2 minutes
      if (Date.now() - task.timestamp > 2 * 60 * 1000) {
        console.log(`[TaskSync] Auto-completing orphaned task: ${task.title}`);
        store.updateRequestStatus(task.id, 'Complete');
      }
    });
  }
  
  // If no backend tasks but we have local tasks, validate local store
  if (backendTasks.length === 0 && localTasks.length > 0) {
    console.warn('[TaskSync] No backend tasks found, validating local store...');
    const result = store.checkStaleTasks();
    if (result.updated > 0) {
      console.log(`[TaskSync] Cleaned up ${result.updated} stale local task(s)`);
    }
  }
}

/**
 * Check if watchdog is currently active
 */
export function isWatchdogActive(): boolean {
  return watchdogId !== null;
}

/**
 * Force run stale task check (for testing/debugging)
 */
export function forceStaleTaskCheck(): void {
  const store = useCommandStore.getState();
  const result = store.checkStaleTasks();
  console.log(`[TaskSync] Force check resolved ${result.updated} stale task(s):`, result.staleTaskIds);
}

/**
 * Future-proofing: WebSocket support stub
 */
export function connectWebSocket(): void {
  console.log('[TaskSync] WebSocket mode not yet enabled (future patch v3.0)');
}
