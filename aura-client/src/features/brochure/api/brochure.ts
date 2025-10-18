const API_BASE =
  import.meta.env.VITE_API_BASE ||
  `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1`;

export interface BrochureDraftOut {
  id: string;
  data: any;
  status: 'draft' | 'rendering' | 'ready' | 'error' | string;
  download_url?: string | null;
  created_at: string;
  updated_at: string;
}

export interface BrochureTemplateOut {
  id: string;
  name: string;
  description?: string | null;
  file_path: string;
  created_at: string;
}

const USE_REAL = (import.meta.env.VITE_USE_REAL_API === 'true');

export async function createDraft(templateKey: string): Promise<BrochureDraftOut> {
  const res = await fetch(`${API_BASE}/brochures`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ templateKey }),
  });
  if (!res.ok) throw new Error(`Failed to create draft: ${res.status}`);
  return res.json();
}

export async function getDraft(id: string): Promise<BrochureDraftOut> {
  const res = await fetch(`${API_BASE}/brochures/${id}`);
  if (!res.ok) throw new Error(`Draft not found: ${id}`);
  return res.json();
}

export async function updateDraft(id: string, patch: Partial<BrochureDraftOut>): Promise<BrochureDraftOut> {
  const res = await fetch(`${API_BASE}/brochures/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(`Failed to update draft: ${res.status}`);
  return res.json();
}

export async function renderDraft(id: string): Promise<{ download_url: string }> {
  const res = await fetch(`${API_BASE}/brochures/${id}/render`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to render draft: ${res.status}`);
  return res.json();
}

export async function getDownloadUrl(id: string): Promise<{ download_url: string }> {
  const res = await fetch(`${API_BASE}/brochures/${id}/download`);
  if (!res.ok) throw new Error(`Download not available`);
  return res.json();
}

export async function listTemplates(): Promise<BrochureTemplateOut[]> {
  if (!USE_REAL) {
    return [
      { id: 'mock-clean', name: 'Clean Minimal', description: 'Light, modern brochure with focus on imagery.', file_path: 'templates/brochure/clean-minimal.html', created_at: new Date().toISOString() },
      { id: 'mock-luxury', name: 'Luxury Showcase', description: 'Premium layout for high-end properties.', file_path: 'templates/brochure/luxury-showcase.html', created_at: new Date().toISOString() },
      { id: 'mock-neighborhood', name: 'Neighborhood Highlight', description: 'Area highlights with local amenities.', file_path: 'templates/brochure/neighborhood-highlight.html', created_at: new Date().toISOString() },
    ];
  }
  const res = await fetch(`${API_BASE}/templates`);
  if (!res.ok) throw new Error(`Failed to list templates: ${res.status}`);
  return res.json();
}

export async function listDrafts(limit = 20, offset = 0): Promise<BrochureDraftOut[]> {
  if (!USE_REAL) return [];
  const url = new URL(`${API_BASE}/brochures`);
  url.searchParams.set('limit', String(limit));
  url.searchParams.set('offset', String(offset));
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to list drafts: ${res.status}`);
  return res.json();
}
