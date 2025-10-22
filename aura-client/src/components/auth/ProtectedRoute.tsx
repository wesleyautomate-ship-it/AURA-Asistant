import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { Loader2 } from 'lucide-react'
import { useAuth } from '../../store/authStore'

interface ProtectedRouteProps {
  children: ReactNode
  fallback?: ReactNode
  requireRole?: string
}

const ProtectedRoute = ({ children, fallback, requireRole }: ProtectedRouteProps) => {
  const { user, isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="flex flex-col items-center space-y-4 text-slate-200">
          <Loader2 className="h-8 w-8 animate-spin text-blue-400" />
          <p>Authenticating...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !user) {
    if (fallback) {
      return <>{fallback}</>
    }

    return <Navigate to="/login" replace state={{ from: location }} />
  }

  if (requireRole && user.role !== requireRole) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <div className="w-full max-w-md rounded-lg bg-slate-800 p-8 text-center shadow-lg">
          <div className="mb-6">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-500 text-white">
              !
            </div>
            <h1 className="mb-2 text-2xl font-bold text-white">Access denied</h1>
            <p className="text-sm text-slate-300">
              Your role ({user.role}) does not have access to this area. Required role: {requireRole}
            </p>
          </div>

          <button
            onClick={() => window.history.back()}
            className="rounded-lg bg-slate-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-600"
          >
            Go back
          </button>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

export default ProtectedRoute
