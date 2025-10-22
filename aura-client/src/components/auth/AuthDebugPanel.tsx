import type { FC } from 'react'
import { useAuth, useAuthActions, getAuthToken, getCurrentUser } from '../../store/authStore'

const storage = typeof window !== 'undefined' ? window.localStorage : null

const AuthDebugPanel: FC = () => {
  const { user, isAuthenticated, isLoading, mode } = useAuth()
  const { login, logout, updateUser } = useAuthActions()

  if (import.meta.env.MODE !== 'development') {
    return null
  }

  const handleTestLogin = async () => {
    try {
      await login({ email: 'admin@propertypro.ai', password: 'Admin123!' })
      console.log('[AuthDebugPanel] Test login completed')
    } catch (error) {
      console.error('[AuthDebugPanel] Test login failed:', error)
    }
  }

  const handleUpdateProfile = () => {
    const currentUser = getCurrentUser()
    if (!currentUser) return

    updateUser({
      name: `${currentUser.name} (updated)`,
      preferences: {
        ...currentUser.preferences,
        lastUpdated: new Date().toISOString(),
      },
    })
  }

  const statusBadgeClass = isAuthenticated ? 'bg-green-600 text-white' : 'bg-red-600 text-white'

  return (
    <div className="fixed bottom-4 right-4 z-50 w-full max-w-sm rounded-lg border border-slate-700 bg-slate-900 p-4 text-xs text-slate-200 shadow-lg">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold">Auth Debug Panel</h3>
        <span className={`rounded px-2 py-1 font-medium ${statusBadgeClass}`}>
          {isAuthenticated ? 'Authenticated' : 'Signed out'}
        </span>
      </div>

      <div className="space-y-3">
        <section>
          <p className="mb-1 font-semibold text-slate-100">Status</p>
          <p>Loading: {isLoading ? 'Yes' : 'No'}</p>
          <p>Authenticated: {isAuthenticated ? 'Yes' : 'No'}</p>
          <p>Token present: {getAuthToken() ? 'Yes' : 'No'}</p>
          <p>Mode: {mode}</p>
        </section>

        {user && (
          <section>
            <p className="mb-1 font-semibold text-slate-100">User</p>
            <p>Name: {user.name}</p>
            <p>Email: {user.email}</p>
            <p>Role: {user.role}</p>
          </section>
        )}

        <section>
          <p className="mb-1 font-semibold text-slate-100">Token (preview)</p>
          <p className="break-all">
            {getAuthToken() ? `${getAuthToken()?.slice(0, 24)}...` : 'None'}
          </p>
        </section>

        <section>
          <p className="mb-1 font-semibold text-slate-100">Storage</p>
          <p>authToken key: {storage?.getItem('authToken') ? 'Yes' : 'No'}</p>
          <p>aura-auth key: {storage?.getItem('aura-auth') ? 'Yes' : 'No'}</p>
        </section>

        <section className="space-y-2 border-t border-slate-700 pt-2">
          {!isAuthenticated ? (
            <button
              onClick={handleTestLogin}
              disabled={isLoading}
              className="w-full rounded bg-blue-600 px-2 py-1 text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-600"
            >
              {isLoading ? 'Authorising...' : 'Test login'}
            </button>
          ) : (
            <>
              <button
                onClick={handleUpdateProfile}
                className="w-full rounded bg-green-600 px-2 py-1 text-white transition hover:bg-green-500"
              >
                Touch profile
              </button>
              <button
                onClick={logout}
                className="w-full rounded bg-red-600 px-2 py-1 text-white transition hover:bg-red-500"
              >
                Logout
              </button>
            </>
          )}
        </section>
      </div>
    </div>
  )
}

export default AuthDebugPanel

