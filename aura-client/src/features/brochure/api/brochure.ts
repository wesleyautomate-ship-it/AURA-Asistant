const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface BrochureDraftOut {
  id: string;
  data: any;
  status: 'draft' | 'rendering' | 'ready' | 'error' | string;
  download_url?: string | null;
  created_at: string;
  updated_at: string;
}

export async function createDraft(templateKey: string): Promise<BrochureDraftOut> {
  const res = await fetch(`${API_BASE_URL}/api/v1/brochures`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ templateKey }),
  });
  if (!res.ok) throw new Error(`Failed to create draft: ${res.status}`);
  return res.json();
}

export async function getDraft(id: string): Promise<BrochureDraftOut> {
  const res = await fetch(`${API_BASE_URL}/api/v1/brochures/${id}`);
  if (!res.ok) throw new Error(`Draft not found: ${id}`);
  return res.json();
}

export async function updateDraft(id: string, patch: Partial<BrochureDraftOut>): Promise<BrochureDraftOut> {
  const res = await fetch(`${API_BASE_URL}/api/v1/brochures/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(`Failed to update draft: ${res.status}`);
  return res.json();
}

export async function renderDraft(id: string): Promise<{ download_url: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/brochures/${id}/render`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to render draft: ${res.status}`);
  return res.json();
}

export async function getDownloadUrl(id: string): Promise<{ download_url: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/brochures/${id}/download`);
  if (!res.ok) throw new Error(`Download not available`);
  return res.json();
}

