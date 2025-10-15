/**
 * Authentication Store
 * ====================
 * 
 * Lightweight development-mode auth store that maintains fake authentication
 * so the rest of the app can function normally until full login integration is ready.
 * 
 * Features:
 * - Fake user session that persists across page reloads
 * - Development token that works with API calls
 * - Safe fallbacks for components expecting auth state
 * - Easy switching between dev and production modes
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Development mode configuration
const DEV_MODE = import.meta.env.MODE === 'development'
const DEV_TOKEN = 'dev-token-12345-aura-ai'

// User interface
export interface User {
  id: string
  email: string
  name: string
  role: string
  avatar?: string
  preferences?: Record<string, any>
}

// Auth store interface
interface AuthStore {
  // State
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  
  // Actions
  login: (credentials?: any) => Promise<void>
  logout: () => void
  updateUser: (updates: Partial<User>) => void
  refreshToken: () => Promise<void>
  
  // Development helpers
  setDevMode: (enabled: boolean) => void
}

// Create the auth store with persistence
export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // Initialize with fake dev data if in development mode
      user: DEV_MODE ? {
        id: 'dev-user-001',
        email: 'admin@aura.ai',
        name: 'AURA Developer',
        role: 'admin',
        avatar: 'ðŸ¤–',
        preferences: {
          theme: 'dark',
          notifications: true,
          autoSave: true
        }
      } : null,
      
      token: (() => {
        if (typeof window === 'undefined') return null;
        if (DEV_MODE) {
          // Always ensure token is set in localStorage for dev mode
          localStorage.setItem('authToken', DEV_TOKEN);
          console.log('[AuthStore] Dev token set in localStorage:', DEV_TOKEN);
          return DEV_TOKEN;
        }
        return localStorage.getItem('authToken');
      })(),
      isAuthenticated: (() => {
        if (typeof window === 'undefined') return false;
        if (DEV_MODE) return true;
        return Boolean(localStorage.getItem('authToken'));
      })(),
      isLoading: false,

      // Login method - fake for development, real for production
      login: async (credentials?: any) => {
        set({ isLoading: true })
        
        try {
          if (DEV_MODE) {
            // Simulate API delay in development
            await new Promise(resolve => setTimeout(resolve, 1000))
            
            console.log('[AuthStore] Developer mode active - fake user session loaded')
            console.log('[AuthStore] Using static token:', DEV_TOKEN)
            
            set({
              user: {
                id: 'dev-user-001',
                email: credentials?.email || 'admin@aura.ai',
                name: 'AURA Developer',
                role: 'admin',
                avatar: '🤖',
                preferences: {
                  theme: 'dark',
                  notifications: true,
                  autoSave: true
                }
              },
              token: DEV_TOKEN,
              isAuthenticated: true,
              isLoading: false
            })
            
            // Set token in localStorage for API client
            localStorage.setItem('authToken', DEV_TOKEN)
            
          } else {
            // TODO: Real authentication logic for production
            throw new Error('Production authentication not implemented yet')
          }
        } catch (error) {
          console.error('[AuthStore] Login failed:', error)
          set({ 
            user: null, 
            token: null, 
            isAuthenticated: false, 
            isLoading: false 
          })
          throw error
        }
      },

      // Logout method
      logout: () => {
        console.log('[AuthStore] Logging out user')
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false
        })
        
        // Clear tokens from storage
        localStorage.removeItem('authToken')
        localStorage.removeItem('auth_token')
        sessionStorage.removeItem('authToken')
        
        console.log('[AuthStore] User session cleared')
      },

      // Update user profile
      updateUser: (updates: Partial<User>) => {
        const currentUser = get().user
        if (currentUser) {
          const updatedUser = { ...currentUser, ...updates }
          set({ user: updatedUser })
          console.log('[AuthStore] User profile updated:', updates)
        }
      },

      // Refresh token (no-op in dev mode)
      refreshToken: async () => {
        if (DEV_MODE) {
          console.log('[AuthStore] Token refresh skipped in dev mode')
          return
        }
        
        // TODO: Real token refresh logic for production
        set({ isLoading: true })
        try {
          // Implement refresh token logic here
          console.log('[AuthStore] Token refreshed')
        } finally {
          set({ isLoading: false })
        }
      },

      // Development mode toggle
      setDevMode: (enabled: boolean) => {
        if (enabled) {
          console.log('[AuthStore] Enabling dev mode with fake auth')
          set({
            user: {
              id: 'dev-user-001',
              email: 'admin@aura.ai',
              name: 'AURA Developer',
              role: 'admin',
              avatar: '🤖'
            },
            token: DEV_TOKEN,
            isAuthenticated: true
          })
          localStorage.setItem('authToken', DEV_TOKEN)
        } else {
          console.log('[AuthStore] Disabling dev mode')
          get().logout()
        }
      }
    }),
    {
      name: 'aura-auth', // localStorage key
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)

// Initialize development token on store creation
if (DEV_MODE) {
  // Ensure localStorage has the dev token for API calls
  const currentToken = localStorage.getItem('authToken')
  if (!currentToken) {
    localStorage.setItem('authToken', DEV_TOKEN)
    console.log('[AuthStore] Development token initialized in localStorage')
  }
  
  // Log dev mode status
  console.log('[AuthStore] Developer mode active - fake authentication enabled')
  console.log('[AuthStore] Current user:', useAuthStore.getState().user?.name)
}

// Export convenience hooks
export const useAuth = () => {
  const { user, isAuthenticated, isLoading } = useAuthStore()
  return { user, isAuthenticated, isLoading }
}

export const useAuthActions = () => {
  const { login, logout, updateUser, refreshToken } = useAuthStore()
  return { login, logout, updateUser, refreshToken }
}

// Export helper functions
export const getAuthToken = (): string | null => {
  return useAuthStore.getState().token
}

export const isUserAuthenticated = (): boolean => {
  return useAuthStore.getState().isAuthenticated
}

export const getCurrentUser = (): User | null => {
  return useAuthStore.getState().user
}

// Development helpers
export const enableDevAuth = () => {
  useAuthStore.getState().setDevMode(true)
}

export const disableDevAuth = () => {
  useAuthStore.getState().setDevMode(false)
}

export default useAuthStore
