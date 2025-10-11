/**
 * Task Lifecycle Configuration
 * ============================
 * 
 * Configuration constants for task timeout, recovery, and lifecycle management
 */

export const TASK_LIFECYCLE_CONFIG = {
  // Timeout settings (in milliseconds)
  STALE_TASK_TIMEOUT: 15 * 60 * 1000, // 15 minutes
  PROCESSING_TIMEOUT: 10 * 60 * 1000, // 10 minutes for processing tasks
  PENDING_TIMEOUT: 5 * 60 * 1000,     // 5 minutes for pending tasks
  
  // Watchdog interval (how often to check for stale tasks)
  WATCHDOG_INTERVAL: 60 * 1000, // 1 minute
  
  // Retry settings
  MAX_RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 2000, // 2 seconds between retries
  
  // Error messages
  ERROR_MESSAGES: {
    TIMEOUT_GENERIC: 'Task timed out (auto-resolved)',
    TIMEOUT_PROCESSING: 'Processing timeout - task may have failed',
    TIMEOUT_PENDING: 'Task remained pending too long - auto-resolved',
    RETRY_FAILED: 'Retry attempt failed',
    MAX_RETRIES_EXCEEDED: 'Maximum retry attempts exceeded'
  }
} as const;

export const RECOVERABLE_STATUSES = ['Pending', 'Processing'] as const;
export const RETRYABLE_STATUSES = ['Error'] as const;

export type RecoverableStatus = typeof RECOVERABLE_STATUSES[number];
export type RetryableStatus = typeof RETRYABLE_STATUSES[number];

/**
 * Calculate timeout duration based on task status
 */
export function getTimeoutForStatus(status: string): number {
  switch (status) {
    case 'Processing':
      return TASK_LIFECYCLE_CONFIG.PROCESSING_TIMEOUT;
    case 'Pending':
      return TASK_LIFECYCLE_CONFIG.PENDING_TIMEOUT;
    default:
      return TASK_LIFECYCLE_CONFIG.STALE_TASK_TIMEOUT;
  }
}

/**
 * Get appropriate error message for timeout
 */
export function getTimeoutErrorMessage(status: string): string {
  switch (status) {
    case 'Processing':
      return TASK_LIFECYCLE_CONFIG.ERROR_MESSAGES.TIMEOUT_PROCESSING;
    case 'Pending':
      return TASK_LIFECYCLE_CONFIG.ERROR_MESSAGES.TIMEOUT_PENDING;
    default:
      return TASK_LIFECYCLE_CONFIG.ERROR_MESSAGES.TIMEOUT_GENERIC;
  }
}

/**
 * Check if a task status is recoverable (can be auto-resolved)
 */
export function isRecoverableStatus(status: string): status is RecoverableStatus {
  return RECOVERABLE_STATUSES.includes(status as RecoverableStatus);
}

/**
 * Check if a task status allows retry
 */
export function isRetryableStatus(status: string): status is RetryableStatus {
  return RETRYABLE_STATUSES.includes(status as RetryableStatus);
}

/**
 * Calculate how long a task has been in current status
 */
export function getTaskAge(timestamp: number): number {
  return Date.now() - timestamp;
}

/**
 * Check if a task has exceeded its timeout
 */
export function isTaskStale(timestamp: number, status: string): boolean {
  const age = getTaskAge(timestamp);
  const timeout = getTimeoutForStatus(status);
  return age > timeout;
}