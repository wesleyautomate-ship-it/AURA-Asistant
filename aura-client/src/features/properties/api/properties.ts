import { api } from '../../../services/http'

export interface PropertyPhotoOut {
  id: string
  url: string
  sort_order: number
}

export interface PropertyOut {
  id: string
  created_at: string
  updated_at: string
  title: string
  building: string
  community?: string | null
  unit?: string | null
  property_type: string
  beds?: number | null
  baths?: number | null
  area_sqft?: number | null
  price_aed?: number | null
  description?: string | null
  status: string
  photos: PropertyPhotoOut[]
}

export interface PropertyCreate {
  title: string
  building: string
  community?: string
  unit?: string
  property_type?: string
  beds?: number
  baths?: number
  area_sqft?: number
  price_aed?: number
  description?: string
  photos?: Array<{ url: string; sort_order: number }>
}

export interface SearchParams {
  q?: string
  building?: string
  unit?: string
  status?: string
  limit?: number
  offset?: number
}

const USE_REAL_API = import.meta.env.VITE_USE_REAL_API === 'true'

export async function search(params: SearchParams = {}): Promise<PropertyOut[]> {
  if (!USE_REAL_API) {
    return []
  }

  const urlParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      urlParams.set(key, String(value))
    }
  })

  const query = urlParams.toString()
  const endpoint = query ? `/properties?${query}` : '/properties'

  const { data } = await api.get<PropertyOut[]>(endpoint)
  return data
}

export async function create(payload: PropertyCreate): Promise<PropertyOut> {
  if (!USE_REAL_API) {
    return {
      id: `prop-${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      title: payload.title,
      building: payload.building,
      community: payload.community || null,
      unit: payload.unit || null,
      property_type: payload.property_type || 'apartment',
      beds: payload.beds ?? null,
      baths: payload.baths ?? null,
      area_sqft: payload.area_sqft ?? null,
      price_aed: payload.price_aed ?? null,
      description: payload.description ?? null,
      status: 'draft',
      photos: [],
    }
  }

  const { data } = await api.post<PropertyOut>('/properties', payload)
  return data
}

export async function getById(id: string): Promise<PropertyOut> {
  const { data } = await api.get<PropertyOut>(`/properties/${id}`)
  return data
}

export async function update(
  id: string,
  payload: Partial<PropertyCreate>
): Promise<PropertyOut> {
  const { data } = await api.patch<PropertyOut>(`/properties/${id}`, payload)
  return data
}

export async function getSample(): Promise<PropertyOut[]> {
  const { data } = await api.get<PropertyOut[]>('/properties/_sample')
  return data
}

export function buildPropertyTitle(intent: { building?: string; beds?: number; unit?: string }): string {
  const { building, beds, unit } = intent
  const parts: string[] = []

  if (beds) {
    parts.push(`${beds}BR`)
  }

  if (building) {
    parts.push(`at ${building}`)
  }

  if (unit) {
    parts.push(unit)
  }

  return parts.join(' ') || 'Property'
}

export function buildMinimalProperty(
  prompt: string,
  intent: { building?: string; beds?: number; unit?: string }
): PropertyCreate {
  const { building, beds, unit } = intent

  return {
    title: buildPropertyTitle(intent),
    building: building || 'Unknown Building',
    beds,
    unit,
    property_type: 'apartment',
    description: `Property listing created from: "${prompt}"`,
  }
}
