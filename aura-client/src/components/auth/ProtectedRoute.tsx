/**
 * Protected Route Component
 * =========================
 * 
 * A wrapper component that protects routes requiring authentication.
 * Works seamlessly with the development auth store for local testing.
 * 
 * Usage:
 * <ProtectedRoute>
 *   <YourProtectedComponent />
 * </ProtectedRoute>
 */

import React from 'react'
import { useAuth } from '../../store/authStore'

interface ProtectedRouteProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  requireRole?: string
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  fallback,
  requireRole 
}) => {
  const { user, isAuthenticated, isLoading } = useAuth()

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="flex flex-col items-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
          <p className="text-gray-400">Authenticating...</p>
        </div>
      </div>
    )
  }

  // Not authenticated - show fallback or login prompt
  if (!isAuthenticated || !user) {
    if (fallback) {
      return <>{fallback}</>
    }

    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="max-w-md w-full bg-gray-800 rounded-lg p-8 text-center">
          <div className="mb-6">
            <div className="mx-auto w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mb-4">
              <span className="text-xl">🔒</span>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Authentication Required</h1>
            <p className="text-gray-400">
              Please log in to access this area.
            </p>
          </div>
          
          <div className="space-y-3">
            <button 
              onClick={() => window.location.href = '/login'}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Go to Login
            </button>
            
            <div className="text-sm text-gray-500">
              Development Mode: Authentication is automatically handled
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Check role requirements
  if (requireRole && user.role !== requireRole) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="max-w-md w-full bg-gray-800 rounded-lg p-8 text-center">
          <div className="mb-6">
            <div className="mx-auto w-12 h-12 bg-red-500 rounded-full flex items-center justify-center mb-4">
              <span className="text-xl">⚠️</span>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Access Denied</h1>
            <p className="text-gray-400">
              Your role ({user.role}) doesn't have permission to access this area.
            </p>
            <p className="text-gray-500 text-sm mt-2">
              Required role: {requireRole}
            </p>
          </div>
          
          <button 
            onClick={() => window.history.back()}
            className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  // User is authenticated and authorized - render protected content
  return <>{children}</>
}

export default ProtectedRoute