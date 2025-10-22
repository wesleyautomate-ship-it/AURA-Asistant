import { useCommandStore } from '../store/commandStore';
import { TASK_LIFECYCLE_CONFIG } from '../config/taskLifecycle';
import api from './http';
import type { AxiosError } from 'axios';

let intervalId: number | null = null;
let watchdogId: number | null = null;
let retryCount = 0;
const MAX_RETRIES = 3;
const SYNC_INTERVAL = 10000; // 10 seconds
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
      const { data } = await api.get<any>('/tasks/sync');
      
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
    } catch (error) {
      const axiosError = error as AxiosError<any>;
      console.warn('[TaskSync] Sync failed:', axiosError.message || axiosError);
      
      if (axiosError.response) {
        console.warn('[TaskSync] Server response:', {
          status: axiosError.response.status,
          statusText: axiosError.response.statusText,
          body: axiosError.response.data,
        });
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
    const { data } = await api.get<any>('/tasks/sync');
    
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
  } catch (error) {
    console.error('[TaskSync] Manual sync failed:', (error as AxiosError<any>).message || error);
    throw error;
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
