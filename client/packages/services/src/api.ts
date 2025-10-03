import { CONFIG } from './config';
import { useUserStore } from '@propertypro/store';

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

type RequestOptions = {
  body?: unknown;
  init?: RequestInit;
};

const BASE_URL = (CONFIG.apiBaseUrl || '').replace(/\/$/, '');

function resolveUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  const normalized = path.startsWith('/') ? path : `/${path}`;
  return `${BASE_URL}${normalized}`;
}

function mergeHeaders(token: string | null, initHeaders: HeadersInit | undefined): HeadersInit {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  if (!initHeaders) {
    return headers;
  }

  if (initHeaders instanceof Headers) {
    initHeaders.forEach((value, key) => {
      headers[key] = value;
    });
    return headers;
  }

  if (Array.isArray(initHeaders)) {
    for (const [key, value] of initHeaders) {
      headers[key] = value as string;
    }
    return headers;
  }

  return { ...headers, ...initHeaders };
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('Content-Type') || '';
  if (contentType.includes('application/json')) {
    return response.json() as Promise<T>;
  }

  const text = await response.text();
  return text as unknown as T;
}

async function apiRequest<T>(method: HttpMethod, path: string, { body, init }: RequestOptions = {}): Promise<T> {
  const { token, logout } = useUserStore.getState();

  const requestInit: RequestInit = {
    method,
    headers: mergeHeaders(token, init?.headers),
    ...init,
  };

  if (body !== undefined) {
    requestInit.body = body instanceof FormData ? body : JSON.stringify(body);
    if (body instanceof FormData) {
      // Allow browser to set appropriate multipart boundary
      if (requestInit.headers && 'Content-Type' in (requestInit.headers as Record<string, string>)) {
        delete (requestInit.headers as Record<string, string>)['Content-Type'];
      }
    }
  }

  let response: Response;
  try {
    response = await fetch(resolveUrl(path), requestInit);
  } catch (error) {
    throw new Error(`Network error contacting API: ${(error as Error).message}`);
  }

  if (!response.ok) {
    if (response.status === 401) {
      logout?.();
    }

    let detail: unknown;
    try {
      detail = await parseResponse<unknown>(response);
    } catch (error) {
      detail = (error as Error).message;
    }

    const message = typeof detail === 'string'
      ? detail
      : (detail && typeof detail === 'object' && 'detail' in detail)
        ? (detail as { detail: unknown }).detail
        : `${response.status} ${response.statusText}`;

    throw new Error(
      typeof message === 'string'
        ? `API ${method} ${path} failed: ${message}`
        : `API ${method} ${path} failed`
    );
  }

  return parseResponse<T>(response);
}

export function apiGet<T>(path: string, init?: RequestInit) {
  return apiRequest<T>('GET', path, { init });
}

export function apiPost<T>(path: string, body?: unknown, init?: RequestInit) {
  return apiRequest<T>('POST', path, { body, init });
}

export function apiPut<T>(path: string, body?: unknown, init?: RequestInit) {
  return apiRequest<T>('PUT', path, { body, init });
}

export function apiPatch<T>(path: string, body?: unknown, init?: RequestInit) {
  return apiRequest<T>('PATCH', path, { body, init });
}

export function apiDelete<T>(path: string, body?: unknown, init?: RequestInit) {
  return apiRequest<T>('DELETE', path, { body, init });
}

export { apiRequest };
