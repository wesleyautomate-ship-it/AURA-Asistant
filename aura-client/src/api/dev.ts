import api from '../services/http';

export async function fetchHealth(): Promise<boolean> {
  try {
    const { data } = await api.get<{ ok?: boolean }>('/healthz');
    return Boolean(data?.ok);
  } catch {
    return false;
  }
}

export async function fetchVersion(): Promise<string> {
  try {
    const { data } = await api.get<{ version?: string }>('/version');
    return typeof data?.version === 'string' ? data.version : 'dev';
  } catch {
    return 'dev';
  }
}
