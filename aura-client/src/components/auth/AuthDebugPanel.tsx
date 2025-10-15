/**
 * Auth Debug Panel
 * ================
 * 
 * Development component to test and debug authentication state.
 * Shows current auth status and provides controls for testing auth flows.
 */

import React from 'react'
import { useAuth, useAuthActions, getAuthToken, getCurrentUser } from '../../store/authStore'

const AuthDebugPanel: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const { login, logout, updateUser } = useAuthActions()
  
  const handleTestLogin = async () => {
    try {
      await login({ email: 'test@aura.ai' })
      console.log('[AuthDebugPanel] Test login completed')
    } catch (error) {
      console.error('[AuthDebugPanel] Test login failed:', error)
    }
  }

  const handleUpdateProfile = () => {
    updateUser({ 
      name: 'AURA Developer (Updated)',
      preferences: { ...user?.preferences, lastUpdated: new Date().toISOString() }
    })
  }

  // Only show in development mode
  if (import.meta.env.MODE !== 'development') {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 bg-gray-800 border border-gray-600 rounded-lg p-4 max-w-sm shadow-lg z-50">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-white">Auth Debug Panel</h3>
        <span className={`text-xs px-2 py-1 rounded ${
          isAuthenticated ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
        }`}>
          {isAuthenticated ? 'Authenticated' : 'Not Auth'}
        </span>
      </div>
      
      <div className="space-y-3 text-xs text-gray-300">
        {/* Auth Status */}
        <div>
          <div className="font-medium text-gray-200 mb-1">Status:</div>
          <div>Loading: {isLoading ? '✅' : '❌'}</div>
          <div>Authenticated: {isAuthenticated ? '✅' : '❌'}</div>
          <div>Token: {getAuthToken() ? '✅' : '❌'}</div>
        </div>

        {/* User Info */}
        {user && (
          <div>
            <div className="font-medium text-gray-200 mb-1">User:</div>
            <div>Name: {user.name}</div>
            <div>Email: {user.email}</div>
            <div>Role: {user.role}</div>
            <div>Avatar: {user.avatar}</div>
          </div>
        )}

        {/* Token Info */}
        <div>
          <div className="font-medium text-gray-200 mb-1">Token:</div>
          <div className="break-all">
            {getAuthToken()?.substring(0, 20)}...
          </div>
        </div>

        {/* Storage Info */}
        <div>
          <div className="font-medium text-gray-200 mb-1">Storage:</div>
          <div>localStorage: {localStorage.getItem('authToken') ? '✅' : '❌'}</div>
          <div>Persist Store: {localStorage.getItem('aura-auth') ? '✅' : '❌'}</div>
        </div>

        {/* Actions */}
        <div className="space-y-2 pt-2 border-t border-gray-600">
          {!isAuthenticated ? (
            <button
              onClick={handleTestLogin}
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white text-xs py-1 px-2 rounded transition-colors"
            >
              {isLoading ? 'Logging in...' : 'Test Login'}
            </button>
          ) : (
            <>
              <button
                onClick={handleUpdateProfile}
                className="w-full bg-green-600 hover:bg-green-700 text-white text-xs py-1 px-2 rounded transition-colors"
              >
                Update Profile
              </button>
              <button
                onClick={logout}
                className="w-full bg-red-600 hover:bg-red-700 text-white text-xs py-1 px-2 rounded transition-colors"
              >
                Logout
              </button>
            </>
          )}
        </div>

        {/* Dev Info */}
        <div className="pt-2 border-t border-gray-600 text-xs text-gray-500">
          <div>Mode: {import.meta.env.MODE}</div>
          <div>Dev Panel: Development Only</div>
        </div>
      </div>
    </div>
  )
}

export default AuthDebugPanel