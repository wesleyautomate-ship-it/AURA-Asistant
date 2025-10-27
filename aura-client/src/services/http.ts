import axios, {
  AxiosError,
  AxiosInstance,
  InternalAxiosRequestConfig,
} from 'axios'

const baseURL =
  import.meta.env.VITE_API_BASE ||
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000/api/v1'

export const ACCESS_TOKEN_KEY = 'access_token'
export const REFRESH_TOKEN_KEY = 'refresh_token'

const getAccessToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

const getRefreshToken = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export const storeTokens = (accessToken: string, refreshToken: string | null) => {
  if (typeof window === 'undefined') return
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem('authToken', accessToken)
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  } else {
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }
}

export const clearTokens = () => {
  if (typeof window === 'undefined') return
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem('authToken')
}

const redirectToLogin = () => {
  if (typeof window === 'undefined') return
  if (import.meta.env.DEV && import.meta.env.VITE_DEV_AUTH_BYPASS === 'true') {
    console.warn('Dev auth bypass active \u2014 skipping login redirect')
    const devWhoamiUrl = (() => {
      try {
        const url = new URL(baseURL)
        url.pathname = '/_dev/whoami'
        return url.toString()
      } catch {
        return '/_dev/whoami'
      }
    })()
    void fetch(devWhoamiUrl, { credentials: 'include' }).catch((err) => {
      console.debug('Dev auth bypass probe failed', err)
    })
    return
  }
  if (window.location.pathname !== '/login') {
    window.location.replace('/login')
  }
}

interface AxiosRequestConfigWithRetry extends InternalAxiosRequestConfig {
  _retry?: boolean
}

interface RefreshResponse {
  access_token: string
  refresh_token?: string
}

type AuraAxiosInstance = AxiosInstance & { enabled: boolean }
const useRealApi = import.meta.env.VITE_USE_REAL_API === 'true'

const api = axios.create({
  baseURL,
}) as AuraAxiosInstance

api.enabled = useRealApi

let isRefreshing = false
let pendingRequests: Array<(token: string | null) => void> = []

const subscribePendingRequest = (callback: (token: string | null) => void) => {
  pendingRequests.push(callback)
}

const resolvePendingRequests = (token: string | null) => {
  pendingRequests.forEach((callback) => callback(token))
  pendingRequests = []
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const { response, config } = error
    const originalRequest = config as AxiosRequestConfigWithRetry

    if (response?.status === 401 && originalRequest && !originalRequest._retry) {
      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        clearTokens()
        redirectToLogin()
        return Promise.reject(error)
      }

      originalRequest._retry = true

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          subscribePendingRequest((token) => {
            if (!token) {
              reject(error)
              return
            }
            originalRequest.headers = originalRequest.headers ?? {}
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          })
        })
      }

      isRefreshing = true

      return new Promise((resolve, reject) => {
        axios
          .post<RefreshResponse>(
            `${baseURL}/auth/refresh`,
            { refresh_token: refreshToken },
            { headers: { 'Content-Type': 'application/json' } }
          )
          .then(({ data }) => {
            const newAccessToken = data.access_token
            const newRefreshToken = data.refresh_token ?? refreshToken

            storeTokens(newAccessToken, newRefreshToken)
            resolvePendingRequests(newAccessToken)

            originalRequest.headers = originalRequest.headers ?? {}
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
            resolve(api(originalRequest))
          })
          .catch((refreshError) => {
            resolvePendingRequests(null)
            clearTokens()
            redirectToLogin()
            reject(refreshError)
          })
          .finally(() => {
            isRefreshing = false
          })
      })
    }

    return Promise.reject(error)
  }
)

export { api }
export default api
