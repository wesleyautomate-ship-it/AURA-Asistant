const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const USE_REAL = (import.meta.env.VITE_USE_REAL_API === 'true');

export const api = {
  enabled: USE_REAL,
  async get<T>(path: string, signal?: AbortSignal): Promise<T> {
    const r = await fetch(`${BASE}${path}`, { signal, headers: { 'Authorization': `Bearer ${import.meta.env.VITE_DEV_AUTH_TOKEN || 'dev'}` } });
    if (!r.ok) throw new Error(await r.text());
    return r.json() as Promise<T>;
  },
  async post<T>(path: string, body: any): Promise<T> {
    const r = await fetch(`${BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${import.meta.env.VITE_DEV_AUTH_TOKEN || 'dev'}` },
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json() as Promise<T>;
  },
};

