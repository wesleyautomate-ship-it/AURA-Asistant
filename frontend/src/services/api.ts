
import { CONFIG } from '../config';
import { useUserStore } from '../store/userStore';

async function apiPost<T>(path: string, body: unknown, init?: RequestInit): Promise<T> {
  const token = useUserStore.getState().token;
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...(init?.headers || {}),
  };

  const res = await fetch(`${CONFIG.apiBaseUrl}${path}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API POST ${path} failed: ${res.status} ${res.statusText} - ${text}`);
  }
  return res.json();
}

async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const token = useUserStore.getState().token;
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...(init?.headers || {}),
  };

  const res = await fetch(`${CONFIG.apiBaseUrl}${path}`, {
    method: 'GET',
    headers,
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API GET ${path} failed: ${res.status} ${res.statusText} - ${text}`);
  }
  return res.json();
}

export { apiGet, apiPost };
