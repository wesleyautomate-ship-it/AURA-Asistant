import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { login as loginApi, logout as logoutApi } from '../services/authApi'
import api, { storeTokens, clearTokens } from '../services/http'

const AUTH_MODE_ENV = ((import.meta.env.VITE_AUTH_MODE as string) || 'api').toLowerCase()
const DEV_AUTH_BYPASS = import.meta.env.VITE_DEV_AUTH_BYPASS === 'true'
const FORCE_DEV_AUTH = AUTH_MODE_ENV === 'mock' || DEV_AUTH_BYPASS
const USE_AUTH_API = !FORCE_DEV_AUTH && import.meta.env.VITE_USE_REAL_API === 'true'
const DEV_TOKEN = 'dev-token-12345-aura-ai'

export interface User {
  id: string
  email: string
  name: string
  role: string
  firstName?: string
  lastName?: string
  avatar?: string
  preferences?: Record<string, unknown>
}

export interface LoginCredentials {
  email: string
  password: string
}

type AuthMode = 'api' | 'mock'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  tokenExpiresAt: number | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  mode: AuthMode
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  updateUser: (updates: Partial<User>) => void
  refreshAccessToken: () => Promise<boolean>
  setDevMode: (enabled: boolean) => void
}

const buildUser = (payload: any): User => {
  const derivedName = [payload.first_name, payload.last_name]
    .filter(Boolean)
    .join(' ')
    .trim()

  const fallbackName = (derivedName || payload.email || 'Aura User') as string

  return {
    id: String(payload.id ?? payload.user_id ?? 'user'),
    email: payload.email ?? 'user@propertypro.ai',
    name: payload.name ?? fallbackName,
    role: payload.role ?? 'agent',
    firstName: payload.first_name,
    lastName: payload.last_name,
    avatar: payload.avatar ?? undefined,
    preferences: payload.preferences,
  }
}

const persistTokens = (accessToken: string | null, refreshToken: string | null) => {
  if (accessToken) {
    storeTokens(accessToken, refreshToken)
  } else {
    clearTokens()
  }
}

const defaultDevUser: User = {
  id: 'dev-user-001',
  email: 'admin@propertypro.ai',
  name: 'Aura Developer',
  role: 'admin',
  firstName: 'Aura',
  lastName: 'Developer',
  preferences: {
    theme: 'dark',
    notifications: true,
  },
}

type InternalAuthState = AuthState & {
  _devInitialized?: boolean;
};

export const useAuthStore = create<InternalAuthState>()(
  persist(
    (set, get) => ({
      user: USE_AUTH_API ? null : defaultDevUser,
      accessToken: USE_AUTH_API ? null : DEV_TOKEN,
      refreshToken: USE_AUTH_API ? null : DEV_TOKEN,
      tokenExpiresAt: null,
      isAuthenticated: !USE_AUTH_API,
      isLoading: false,
      error: null,
      mode: USE_AUTH_API ? 'api' : 'mock',

      login: async ({ email, password }: LoginCredentials) => {
        set({ isLoading: true, error: null })

        if (!USE_AUTH_API) {
          await new Promise((resolve) => setTimeout(resolve, 350))
          persistTokens(DEV_TOKEN, DEV_TOKEN)
          set({
            user: { ...defaultDevUser, email },
            accessToken: DEV_TOKEN,
            refreshToken: DEV_TOKEN,
            tokenExpiresAt: Date.now() + 60 * 60 * 1000,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
          return
        }

        try {
          const data = await loginApi(email, password)
          const user = buildUser(data.user)
          const expiresIn = Number(data.expires_in ?? 0)
          const expiresAt = expiresIn > 0 ? Date.now() + expiresIn * 1000 : null

          persistTokens(data.access_token, data.refresh_token ?? null)

          set({
            user,
            accessToken: data.access_token,
            refreshToken: data.refresh_token ?? null,
            tokenExpiresAt: expiresAt,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } catch (error) {
          persistTokens(null, null)
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            tokenExpiresAt: null,
            isAuthenticated: false,
            isLoading: false,
            error: error instanceof Error ? error.message : 'Authentication failed.',
          })
          throw error instanceof Error ? error : new Error('Authentication failed.')
        }
      },

      logout: () => {
        if (USE_AUTH_API) {
          logoutApi()
        }
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          tokenExpiresAt: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        })
      },

      updateUser: (updates: Partial<User>) => {
        const current = get().user
        if (!current) return
        set({ user: { ...current, ...updates } })
      },

      refreshAccessToken: async () => {
        if (!USE_AUTH_API) {
          return true
        }

        const refreshToken = get().refreshToken
        if (!refreshToken) {
          get().logout()
          return false
        }

        try {
          const { data } = await api.post<{ access_token: string; refresh_token?: string; expires_in?: number }>(
            '/auth/refresh',
            { refresh_token: refreshToken }
          )
          const expiresIn = Number(data.expires_in ?? 0)
          const expiresAt = expiresIn > 0 ? Date.now() + expiresIn * 1000 : null

          persistTokens(data.access_token, data.refresh_token ?? refreshToken)
          set({
            accessToken: data.access_token,
            refreshToken: data.refresh_token ?? refreshToken,
            tokenExpiresAt: expiresAt,
            isAuthenticated: true,
          })
          return true
        } catch (error) {
          console.error('[AuthStore] Failed to refresh token:', error)
          get().logout()
          return false
        }
      },

      setDevMode: (enabled: boolean) => {
        if (enabled) {
          persistTokens(DEV_TOKEN, DEV_TOKEN)
          set({
            user: defaultDevUser,
            accessToken: DEV_TOKEN,
            refreshToken: DEV_TOKEN,
            tokenExpiresAt: Date.now() + 60 * 60 * 1000,
            isAuthenticated: true,
            mode: 'mock',
          })
        } else {
          persistTokens(null, null)
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            tokenExpiresAt: null,
            isAuthenticated: false,
            mode: 'api',
          })
        }
      },
    }),
    {
      name: 'aura-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        tokenExpiresAt: state.tokenExpiresAt,
        isAuthenticated: state.isAuthenticated,
        mode: state.mode,
      }),
    }
  )
)

if (!USE_AUTH_API) {
  const ensureDevState = () => {
    const state = useAuthStore.getState()
    if (state._devInitialized) {
      return
    }
    persistTokens(DEV_TOKEN, DEV_TOKEN)
    useAuthStore.setState({
      user: defaultDevUser,
      accessToken: DEV_TOKEN,
      refreshToken: DEV_TOKEN,
      tokenExpiresAt: Date.now() + 60 * 60 * 1000,
      isAuthenticated: true,
      mode: 'mock',
      _devInitialized: true,
      isLoading: false,
      error: null,
    })
  }

  ensureDevState()

  const storeWithPersist = useAuthStore as typeof useAuthStore & {
    persist?: {
      onFinish?: (callback: () => void) => void
    }
  }

  storeWithPersist.persist?.onFinish?.(ensureDevState)
}

export const useAuth = () => {
  const { user, isAuthenticated, isLoading, error, mode } = useAuthStore()
  return { user, isAuthenticated, isLoading, error, mode }
}

export const useAuthActions = () => {
  const { login, logout, updateUser, refreshAccessToken, setDevMode } = useAuthStore()
  return { login, logout, updateUser, refreshAccessToken, setDevMode }
}

export const getAuthToken = (): string | null => useAuthStore.getState().accessToken
export const isUserAuthenticated = (): boolean => useAuthStore.getState().isAuthenticated
export const getCurrentUser = (): User | null => useAuthStore.getState().user
export const enableDevAuth = () => useAuthStore.getState().setDevMode(true)
export const disableDevAuth = () => useAuthStore.getState().setDevMode(false)

export default useAuthStore
