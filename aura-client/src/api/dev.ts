const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/healthz`, { method: 'GET' });
    if (!res.ok) return false;
    const data = await res.json().catch(() => ({}));
    return Boolean(data?.ok);
  } catch {
    return false;
  }
}

export async function fetchVersion(): Promise<string> {
  try {
    const res = await fetch(`${API_BASE_URL}/version`, { method: 'GET' });
    if (!res.ok) return 'dev';
    const data = await res.json().catch(() => ({}));
    return typeof data?.version === 'string' ? data.version : 'dev';
  } catch {
    return 'dev';
  }
}

