export function requireAuth(): boolean {
  if (typeof window === 'undefined') return false
  return Boolean(localStorage.getItem('access_token'))
}

