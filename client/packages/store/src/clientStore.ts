import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { apiDelete, apiGet, apiPost, apiPut } from '@propertypro/services';
import type { BaseAsyncSlice, RequestStatus, Id, WithTimestamps } from './types';

export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'nurturing' | 'converted' | 'archived';

export interface Client extends WithTimestamps<{
  id: Id;
  name: string;
  email?: string;
  phone?: string;
  leadScore?: number;
  status: LeadStatus;
  lastContactedAt?: string;
  notes?: string;
}> {}

export interface CommunicationLog extends WithTimestamps<{
  id: Id;
  clientId: Id;
  type: 'call' | 'email' | 'sms' | 'meeting';
  content?: string;
  at: string;
}> {}

export interface ClientState {
  clients: Client[];
  logs: CommunicationLog[];
  fetch: BaseAsyncSlice;
  mutate: BaseAsyncSlice;
  // actions
  fetchClients: () => Promise<void>;
  addClient: (payload: Omit<Client, 'id'>) => Promise<Client>;
  updateClient: (id: Id, updates: Partial<Client>) => Promise<Client>;
  logCommunication: (payload: Omit<CommunicationLog, 'id'>) => Promise<CommunicationLog>;
  setLeadStatus: (id: Id, status: LeadStatus) => Promise<Client>;
  deleteClient: (id: Id) => Promise<void>;
}

const initialAsync: BaseAsyncSlice = { status: 'idle', error: null };

function toFrontendClient(apiClient: any): Client {
  const status = (apiClient.client_status || 'active').toLowerCase();
  const leadScore = apiClient.preferences?.lead_score ?? apiClient.preferences?.score ?? apiClient.lead_score ?? 50;

  return {
    id: String(apiClient.id),
    name: apiClient.name,
    email: apiClient.email ?? undefined,
    phone: apiClient.phone ?? undefined,
    leadScore: Number.isFinite(leadScore) ? Number(leadScore) : 50,
    status: (['new', 'contacted', 'qualified', 'nurturing', 'converted', 'archived'].includes(status) ? status : 'contacted') as LeadStatus,
    lastContactedAt: apiClient.preferences?.last_contacted_at ?? apiClient.updated_at ?? undefined,
    notes: apiClient.notes ?? apiClient.requirements ?? undefined,
    createdAt: apiClient.created_at ?? undefined,
    updatedAt: apiClient.updated_at ?? undefined,
  };
}

function toApiClientPayload(updates: Partial<Client>, existing?: Client) {
  const body: Record<string, unknown> = {};
  if (updates.name !== undefined) body.name = updates.name;
  if (updates.email !== undefined) body.email = updates.email;
  if (updates.phone !== undefined) body.phone = updates.phone;
  if (updates.notes !== undefined) body.notes = updates.notes;
  if (updates.status !== undefined) body.client_status = updates.status;

  if (updates.leadScore !== undefined || updates.lastContactedAt !== undefined) {
    const prefs: Record<string, unknown> = {};
    const currentScore = updates.leadScore ?? existing?.leadScore ?? 50;
    prefs.lead_score = currentScore;
    if (updates.lastContactedAt) {
      prefs.last_contacted_at = updates.lastContactedAt;
    }
    body.preferences = prefs;
  }

  return body;
}

export const useClientStore = create<ClientState>()(devtools((set, get) => ({
  clients: [],
  logs: [],
  fetch: initialAsync,
  mutate: initialAsync,

  fetchClients: async () => {
    set({ fetch: { status: 'loading', error: null } });
    try {
      const data = await apiGet<any[]>('/api/v1/clients');
      const normalized = Array.isArray(data) ? data.map(toFrontendClient) : [];
      set({ clients: normalized, fetch: { status: 'success', error: null, lastUpdated: new Date().toISOString() } });
    } catch (e: any) {
      set({ fetch: { status: 'error', error: e.message } });
    }
  },

  addClient: async (payload) => {
    set({ mutate: { status: 'loading', error: null } });
    try {
      const requestBody = {
        name: payload.name,
        email: payload.email,
        phone: payload.phone,
        client_status: payload.status ?? 'new',
        notes: payload.notes,
        preferences: {
          lead_score: payload.leadScore ?? 50,
          last_contacted_at: payload.lastContactedAt ?? null,
        },
      };
      const created = await apiPost<any>('/api/v1/clients', requestBody);
      const normalized = toFrontendClient(created);
      set({ clients: [normalized, ...get().clients], mutate: { status: 'success', error: null, lastUpdated: new Date().toISOString() } });
      return normalized;
    } catch (e: any) {
      set({ mutate: { status: 'error', error: e.message } });
      throw e;
    }
  },

  updateClient: async (id, updates) => {
    set({ mutate: { status: 'loading', error: null } });
    try {
      const existing = get().clients.find(c => c.id === String(id));
      const requestBody = toApiClientPayload(updates, existing);
      const updated = await apiPut<any>(`/api/v1/clients/${id}`, requestBody);
      const normalized = toFrontendClient(updated);
      set({ clients: get().clients.map(c => c.id === String(id) ? normalized : c), mutate: { status: 'success', error: null, lastUpdated: new Date().toISOString() } });
      return normalized;
    } catch (e: any) {
      set({ mutate: { status: 'error', error: e.message } });
      throw e;
    }
  },

  deleteClient: async (id) => {
    set({ mutate: { status: 'loading', error: null } });
    try {
      await apiDelete(`/api/v1/clients/${id}`);
      set({ clients: get().clients.filter(c => c.id !== String(id)), mutate: { status: 'success', error: null, lastUpdated: new Date().toISOString() } });
    } catch (e: any) {
      set({ mutate: { status: 'error', error: e.message } });
      throw e;
    }
  },

  logCommunication: async (payload) => {
    const { clientId, type, content, at } = payload;
    const entry: CommunicationLog = {
      id: `${clientId}-${Date.now()}`,
      clientId: String(clientId),
      type,
      content,
      at,
      createdAt: new Date().toISOString(),
    };

    set({ logs: [entry, ...get().logs] });

    try {
      await get().updateClient(clientId, {
        notes: `${type.toUpperCase()} @ ${new Date(at).toLocaleString()}: ${content ?? ''}`,
        lastContactedAt: at,
        leadScore: Math.min((get().clients.find(c => c.id === String(clientId))?.leadScore ?? 50) + 2, 100),
      });
    } catch (error) {
      // non-fatal
    }

    return entry;
  },

  setLeadStatus: async (id, status) => {
    return get().updateClient(id, { status });
  },
})));

// Selectors
export const selectClients = (s: ClientState) => s.clients;
export const selectClientById = (id: Id) => (s: ClientState) => s.clients.find(c => c.id === id) || null;
export const selectClientFetchStatus = (s: ClientState): RequestStatus => s.fetch.status;
export const selectClientMutateStatus = (s: ClientState): RequestStatus => s.mutate.status;
