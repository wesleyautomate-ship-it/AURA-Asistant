export interface AsyncState<T = unknown> {
  data: T;
  loading: boolean;
  error: string | null;
  success: boolean;
}

export type Id = string;

export interface Paginated<T> {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
}

export type WithTimestamps<T> = T & { createdAt?: string; updatedAt?: string };

export type RequestStatus = 'idle' | 'loading' | 'success' | 'error';

export interface BaseAsyncSlice {
  status: RequestStatus;
  error: string | null;
  lastUpdated?: string;
}

export const asyncInitial: BaseAsyncSlice = {
  status: 'idle',
  error: null,
};

export const startLoading = (slice: BaseAsyncSlice) => ({ ...slice, status: 'loading', error: null });
export const setError = (slice: BaseAsyncSlice, error: string) => ({ ...slice, status: 'error', error });
export const setSuccess = (slice: BaseAsyncSlice) => ({ ...slice, status: 'success', error: null, lastUpdated: new Date().toISOString() });