import { FormEvent, useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Loader2, Lock, LogIn, Mail, Shield } from 'lucide-react'
import { useAuth, useAuthActions } from '../store/authStore'

interface LocationState {
  from?: {
    pathname: string
  }
}

const USE_REAL_API = import.meta.env.VITE_USE_REAL_API === 'true'
const DEV_EMAIL = import.meta.env.VITE_DEV_LOGIN_EMAIL || 'admin@propertypro.ai'
const DEV_PASSWORD = import.meta.env.VITE_DEV_LOGIN_PASSWORD || 'Admin123!'

export default function Login() {
  const location = useLocation()
  const navigate = useNavigate()
  const { isAuthenticated, isLoading } = useAuth()
  const { login } = useAuthActions()

  const [email, setEmail] = useState<string>(USE_REAL_API ? '' : DEV_EMAIL)
  const [password, setPassword] = useState<string>(USE_REAL_API ? '' : DEV_PASSWORD)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const redirectPath = useMemo(() => {
    const state = location.state as LocationState | undefined
    return state?.from?.pathname || '/'
  }, [location.state])

  useEffect(() => {
    if (isAuthenticated) {
      navigate(redirectPath, { replace: true })
    }
  }, [isAuthenticated, navigate, redirectPath])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)
    setSubmitting(true)

    try {
      if (!email || !password) {
        throw new Error('Email and password are required.')
      }

      await login({ email, password })
      navigate(redirectPath, { replace: true })
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unable to sign in. Please try again.'
      setError(message)
      setSubmitting(false)
    }
  }

  const effectiveLoading = isLoading || submitting
  const showDevNotice = !USE_REAL_API

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-12">
      <div className="grid w-full max-w-5xl gap-10 rounded-3xl bg-slate-900/70 p-8 shadow-2xl backdrop-blur">
        <div className="flex flex-col gap-6 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-500 text-white shadow-lg">
            <Shield className="h-7 w-7" />
          </div>
          <div>
            <h1 className="text-3xl font-semibold text-white">Sign in to Aura</h1>
            <p className="mt-2 text-sm text-slate-300">
              Access the RealtorProAI workspace to manage intelligent workflows, clients, and
              marketing automation.
            </p>
          </div>
          {showDevNotice && (
            <div className="rounded-xl border border-blue-500/40 bg-blue-500/10 p-4 text-sm text-slate-100">
              <p className="font-medium text-blue-100">
                Development mode is active - authentication is simulated.
              </p>
              <p className="mt-1 text-slate-200">
                Use the default credentials below or any values to explore the app. Toggle
                `VITE_USE_REAL_API=true` to connect to the live backend.
              </p>
            </div>
          )}
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-5 rounded-2xl border border-slate-800 bg-slate-950/60 p-8 text-left shadow-inner"
        >
          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-medium text-slate-200">
              Email
            </label>
            <div className="flex items-center rounded-xl border border-slate-800 bg-slate-900/70 px-4">
              <Mail className="mr-3 h-4 w-4 text-slate-400" />
              <input
                id="email"
                type="email"
                autoComplete="email"
                inputMode="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="h-12 w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-500"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="block text-sm font-medium text-slate-200">
              Password
            </label>
            <div className="flex items-center rounded-xl border border-slate-800 bg-slate-900/70 px-4">
              <Lock className="mr-3 h-4 w-4 text-slate-400" />
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="h-12 w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-500"
                placeholder="Enter your password"
              />
            </div>
          </div>

          {error && (
            <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-100">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={effectiveLoading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-500 py-3 text-sm font-medium text-white transition hover:from-blue-400 hover:to-indigo-400 disabled:cursor-not-allowed disabled:opacity-70"
          >
            {effectiveLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <LogIn className="h-4 w-4" />
                <span>Sign in</span>
              </>
            )}
          </button>

          <div className="text-center text-xs text-slate-400">
            By continuing you agree to the Workspace Terms and acknowledge the Privacy Policy.
          </div>
        </form>
      </div>
    </div>
  )
}
