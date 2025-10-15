/**
 * Auth Components Export Index
 * ============================
 * 
 * Centralized exports for all auth-related components and utilities.
 */

export { default as ProtectedRoute } from './ProtectedRoute'
export { default as AuthDebugPanel } from './AuthDebugPanel'

// Re-export auth store utilities for convenience
export {
  useAuth,
  useAuthActions,
  getAuthToken,
  isUserAuthenticated,
  getCurrentUser,
  enableDevAuth,
  disableDevAuth
} from '../../store/authStore'

export type { User } from '../../store/authStore'