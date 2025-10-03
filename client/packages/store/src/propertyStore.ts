import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { apiDelete, apiGet, apiPost, apiPut } from '@propertypro/services';
import type { BaseAsyncSlice, RequestStatus, Id, WithTimestamps } from './types';

export interface Property extends WithTimestamps<{
  id: Id;
  title: string;
  description: string;
  price: number;
  location: string;
  propertyType: string;
  beds: number;
  baths: number;
  sqft?: number;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  imageUrl?: string;
  status?: 'draft' | 'active' | 'pending' | 'sold';
}>{}

export interface PropertyState {
  items: Property[];
  selectedId: Id | null;
  fetch: BaseAsyncSlice;
  mutate: BaseAsyncSlice;
  // actions
  fetchProperties: () => Promise<void>;
  addProperty: (payload: Omit<Property, 'id'>) => Promise<Property>;
  updateProperty: (id: Id, updates: Partial<Property>) => Promise<Property>;
  deleteProperty: (id: Id) => Promise<void>;
  setSelected: (id: Id | null) => void;
}

const initialAsync: BaseAsyncSlice = { status: 'idle', error: null };

function toFrontendProperty(apiProperty: any): Property {
  const rawId = apiProperty?.id ?? apiProperty?.property_id ?? apiProperty?.uuid ?? '';
  const rawPrice = apiProperty?.price_aed ?? apiProperty?.price ?? apiProperty?.list_price ?? 0;
  const rawBeds = apiProperty?.bedrooms ?? apiProperty?.beds ?? apiProperty?.bed ?? 0;
  const rawBaths = apiProperty?.bathrooms ?? apiProperty?.baths ?? apiProperty?.bath ?? 0;
  const rawSqft = apiProperty?.area_sqft ?? apiProperty?.square_feet ?? apiProperty?.area;

  const price = Number(rawPrice);
  const beds = Number(rawBeds);
  const baths = Number(rawBaths);
  const sqft = Number(rawSqft);

  const normalizedId = rawId !== undefined && rawId !== null ? String(rawId) : '';

  return {
    id: normalizedId,
    title: apiProperty?.title ?? apiProperty?.name ?? '',
    description: apiProperty?.description ?? '',
    price: Number.isFinite(price) ? price : 0,
    location: apiProperty?.location ?? apiProperty?.city ?? '',
    propertyType: apiProperty?.property_type ?? apiProperty?.type ?? 'unknown',
    beds: Number.isFinite(beds) ? beds : 0,
    baths: Number.isFinite(baths) ? baths : 0,
    sqft: Number.isFinite(sqft) ? sqft : undefined,
    address: apiProperty?.location ?? apiProperty?.address ?? '',
    city: apiProperty?.city ?? undefined,
    state: apiProperty?.state ?? undefined,
    zip: apiProperty?.zip ?? undefined,
    imageUrl: apiProperty?.image_url ?? apiProperty?.imageUrl ?? undefined,
    status: apiProperty?.status ?? apiProperty?.listing_status ?? 'draft',
    createdAt: apiProperty?.created_at ?? apiProperty?.createdAt ?? undefined,
    updatedAt: apiProperty?.updated_at ?? apiProperty?.updatedAt ?? undefined,
  };
}

function toApiPayload(payload: Partial<Property>) {
  const body: Record<string, unknown> = {};
  if (payload.title !== undefined) body.title = payload.title;
  if (payload.description !== undefined) body.description = payload.description;
  if (payload.price !== undefined) body.price = payload.price;
  if (payload.location !== undefined) body.location = payload.location;
  if (payload.propertyType !== undefined) body.property_type = payload.propertyType;
  if (payload.beds !== undefined) body.bedrooms = payload.beds;
  if (payload.baths !== undefined) body.bathrooms = payload.baths;
  if (payload.sqft !== undefined) body.area_sqft = payload.sqft;
  return body;
}

export const usePropertyStore = create<PropertyState>()(devtools((set, get) => ({
  items: [],
  selectedId: null,
  fetch: initialAsync,
  mutate: initialAsync,

  setSelected: (id) => set({ selectedId: id === null ? null : String(id) }),

  fetchProperties: async () => {
    set({ fetch: { status: 'loading', error: null } });
    try {
      const data = await apiGet<any[]>('/api/v1/properties');
      const normalized = Array.isArray(data) ? data.map(toFrontendProperty) : [];
      set((state) => {
        const nextSelected =
          state.selectedId && normalized.some((property) => property.id === state.selectedId)
            ? state.selectedId
            : normalized[0]?.id ?? null;
        return {
          items: normalized,
          selectedId: nextSelected,
          fetch: { status: 'success', error: null, lastUpdated: new Date().toISOString() },
        };
      });
    } catch (e: any) {
      const message = e?.message ?? 'Failed to fetch properties';
      set({ fetch: { status: 'error', error: message } });
    }
  },

  addProperty: async (payload) => {
    set({ mutate: { status: 'loading', error: null } });
    try {
      const requestBody = toApiPayload(payload);
      // Backfill required fields if caller omitted them
      if (!requestBody.description) {
        requestBody.description = `${payload.title} marketing description`;
      }
      if (!requestBody.location) {
        requestBody.location = payload.address || payload.location || 'Dubai';
      }
      if (!requestBody.property_type) {
        requestBody.property_type = payload.propertyType || 'apartment';
      }
      if (requestBody.price === undefined) {
        requestBody.price = 0;
      }
      if (requestBody.bedrooms === undefined) {
        requestBody.bedrooms = payload.beds ?? 0;
      }
      if (requestBody.bathrooms === undefined) {
        requestBody.bathrooms = payload.baths ?? 0;
      }

      const created = await apiPost<any>('/api/v1/properties', requestBody);
      const normalized = toFrontendProperty(created);
      set({ items: [normalized, ...get().items], mutate: { status: 'success', error: null, lastUpdated: new Date().toISOString() } });
      return normalized;
    } catch (e: any) {
      set({ mutate: { status: 'error', error: e.message } });
      throw e;
    }
  },

  updateProperty: async (id, updates) => {
    set({ mutate: { status: 'loading', error: null } });
    try {
      const requestBody = toApiPayload(updates);
      const updated = await apiPut<any>(`/api/v1/properties/${id}`, requestBody);
      const normalized = toFrontendProperty(updated);
      const idString = String(id);
      set({
        items: get().items.map((item) => (item.id === idString ? normalized : item)),
        mutate: { status: 'success', error: null, lastUpdated: new Date().toISOString() },
      });
      return normalized;
    } catch (e: any) {
      set({ mutate: { status: 'error', error: e.message } });
      throw e;
    }
  },

  deleteProperty: async (id) => {
    set({ mutate: { status: 'loading', error: null } });
    try {
      await apiDelete(`/api/v1/properties/${id}`);
      const idString = String(id);
      set({
        items: get().items.filter((item) => item.id !== idString),
        mutate: { status: 'success', error: null, lastUpdated: new Date().toISOString() },
      });
    } catch (e: any) {
      set({ mutate: { status: 'error', error: e.message } });
      throw e;
    }
  },
})));

// Selectors
export const selectProperties = (s: PropertyState) => s.items;
export const selectSelectedProperty = (s: PropertyState) => s.items.find(i => i.id === s.selectedId) || null;
export const selectPropertyFetchStatus = (s: PropertyState): RequestStatus => s.fetch.status;
export const selectPropertyMutateStatus = (s: PropertyState): RequestStatus => s.mutate.status;





