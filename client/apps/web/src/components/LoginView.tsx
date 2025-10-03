import React, { useState } from 'react';
import { login as apiLogin, extractUserDisplayName } from '@propertypro/services';
import { useUserStore } from '@propertypro/store';

const DEMO_CREDENTIALS = {
  email: 'agent1@dubai-estate.com',
  password: 'Agent123!',
};

function mapUserProfile(raw: Record<string, unknown>) {
  const id = raw?.id ?? raw?.user_id ?? '0';
  const first = typeof raw?.first_name === 'string' ? raw.first_name : '';
  const last = typeof raw?.last_name === 'string' ? raw.last_name : '';
  const role = typeof raw?.role === 'string' ? raw.role : 'agent';
  const email = typeof raw?.email === 'string' ? raw.email : DEMO_CREDENTIALS.email;
  const name = [first, last].filter(Boolean).join(' ').trim() || extractUserDisplayName(raw);

  return {
    id: String(id),
    name,
    email,
    role: role as 'agent' | 'admin' | 'manager' | string,
  };
}

const inputClass = 'w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500';

const LoginView: React.FC = () => {
  const [email, setEmail] = useState(DEMO_CREDENTIALS.email);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const login = useUserStore((state) => state.login);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await apiLogin(email.trim(), password);
      const profile = mapUserProfile(response.user ?? {});
      const expiresAt = response.expires_in ? Date.now() + response.expires_in * 1000 : null;
      login({
        user: profile,
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        expiresAt,
      });
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Unable to authenticate';
      setError(message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="w-full max-w-md bg-white/95 backdrop-blur rounded-3xl shadow-2xl p-8 space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-semibold text-slate-900">PropertyPro AI</h1>
          <p className="text-sm text-slate-500">Sign in with your brokerage credentials to unlock AURA workflows.</p>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-600" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className={inputClass}
              placeholder="you@propertypro.ae"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-600" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className={inputClass}
              placeholder="Enter your password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          {error && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-600">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 text-white font-semibold py-3 transition hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="rounded-2xl bg-slate-50 border border-slate-200 p-4 text-xs text-slate-500 space-y-2">
          <div className="font-semibold text-slate-600">Demo Access</div>
          <div>Email: {DEMO_CREDENTIALS.email}</div>
          <div>Password: {DEMO_CREDENTIALS.password}</div>
          <button
            className="mt-2 inline-flex items-center gap-1 text-blue-600 hover:text-blue-700"
            onClick={() => {
              setEmail(DEMO_CREDENTIALS.email);
              setPassword(DEMO_CREDENTIALS.password);
            }}
          >
            Use demo credentials
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginView;
