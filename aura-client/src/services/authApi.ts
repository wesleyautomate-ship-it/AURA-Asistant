import api, { storeTokens, clearTokens } from './http'

interface LoginResponse {
  access_token: string
  refresh_token: string
  [key: string]: unknown
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const { data } = await api.post<LoginResponse>('/auth/login', { email, password })

  if (!data?.access_token || !data?.refresh_token) {
    throw new Error('Login response missing tokens')
  }

  storeTokens(data.access_token, data.refresh_token)
  return data
}

export function logout(): void {
  clearTokens()
}
