import { apiPost } from './api';

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: Record<string, unknown>;
}

export interface RefreshResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  return apiPost<LoginResponse>('/api/v1/auth/login', { email, password });
}

export async function refresh(refreshToken: string): Promise<RefreshResponse> {
  return apiPost<RefreshResponse>('/api/v1/auth/refresh', { refresh_token: refreshToken });
}

export function extractUserDisplayName(user: Record<string, unknown> | undefined): string {
  if (!user) return 'Agent';
  const first = typeof user.first_name === 'string' ? user.first_name : '';
  const last = typeof user.last_name === 'string' ? user.last_name : '';
  const fallback = typeof user.email === 'string' ? user.email.split('@')[0] : 'Agent';
  return [first, last].filter(Boolean).join(' ').trim() || fallback;
}
