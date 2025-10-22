import { api } from '../../../services/http'

const USE_REAL = import.meta.env.VITE_USE_REAL_API === 'true'

export interface BrochureDraftOut {
  id: string
  data: any
  status: 'draft' | 'rendering' | 'ready' | 'error' | string
  download_url?: string | null
  created_at: string
  updated_at: string
}

export interface BrochureTemplateOut {
  id: string
  name: string
  description?: string | null
  file_path: string
  created_at: string
}

export async function createDraft(payload: {
  templateKey: string
  property_id?: string
  data?: any
}): Promise<BrochureDraftOut> {
  if (!USE_REAL) {
    return {
      id: `draft-${Date.now()}`,
      data: { templateKey: payload.templateKey, ...payload.data },
      status: 'draft',
      download_url: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
  }

  const { data } = await api.post<BrochureDraftOut>('/brochures', payload)
  return data
}

export async function getDraft(id: string): Promise<BrochureDraftOut> {
  const { data } = await api.get<BrochureDraftOut>(`/brochures/${id}`)
  return data
}

export async function updateDraft(
  id: string,
  patch: Partial<BrochureDraftOut>
): Promise<BrochureDraftOut> {
  const { data } = await api.patch<BrochureDraftOut>(`/brochures/${id}`, patch)
  return data
}

export async function renderDraft(id: string): Promise<{ download_url: string }> {
  if (!USE_REAL) {
    await new Promise((resolve) => setTimeout(resolve, 1000))
    return {
      download_url: `http://localhost:8000/api/v1/assets/mock-brochures/${id}.pdf`,
    }
  }

  const { data } = await api.post<{ download_url: string }>(`/brochures/${id}/render`)
  return data
}

export async function getDownloadUrl(id: string): Promise<{ download_url: string }> {
  const { data } = await api.get<{ download_url: string }>(`/brochures/${id}/download`)
  return data
}

export async function listTemplates(): Promise<BrochureTemplateOut[]> {
  if (!USE_REAL) {
    return [
      {
        id: 'mock-clean',
        name: 'Clean Minimal',
        description: 'Light, modern brochure with focus on imagery.',
        file_path: 'templates/brochure/clean-minimal.html',
        created_at: new Date().toISOString(),
      },
      {
        id: 'mock-luxury',
        name: 'Luxury Showcase',
        description: 'Premium layout for high-end properties.',
        file_path: 'templates/brochure/luxury-showcase.html',
        created_at: new Date().toISOString(),
      },
      {
        id: 'mock-neighborhood',
        name: 'Neighborhood Highlight',
        description: 'Area highlights with local amenities.',
        file_path: 'templates/brochure/neighborhood-highlight.html',
        created_at: new Date().toISOString(),
      },
    ]
  }

  const { data } = await api.get<BrochureTemplateOut[]>('/templates')
  return data
}

export async function listDrafts(limit = 20, offset = 0): Promise<BrochureDraftOut[]> {
  if (!USE_REAL) {
    return []
  }

  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  })

  const { data } = await api.get<BrochureDraftOut[]>(`/brochures?${params.toString()}`)
  return data
}
