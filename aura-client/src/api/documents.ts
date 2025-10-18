const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface BrochureInput {
  title?: string;
  subtitle?: string;
  address?: string;
  price?: string;
  bedrooms?: number;
  bathrooms?: number;
  area_sqft?: number;
  property_type?: string;
  highlights?: string[];
  amenities?: string[];
}

export interface BrochureResult {
  task_id: string;
  file_url: string;
  status: 'completed';
}

export async function createBrochure(input: Partial<BrochureInput>): Promise<BrochureResult> {
  const res = await fetch(`${API_BASE_URL}/api/v1/export/brochure-mock`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input || {}),
  });
  if (!res.ok) {
    throw new Error(`Failed to create brochure: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// Generic HTML save via export service; returns a file URL in BrochureResult shape
export async function saveHtml(payload: { html: string; prefix?: string }): Promise<BrochureResult> {
  const res = await fetch(`${API_BASE_URL}/api/v1/export/html-save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ html: payload.html, prefix: payload.prefix || 'brochure' }),
  });
  if (!res.ok) {
    throw new Error(`Failed to save HTML: ${res.status} ${res.statusText}`);
  }
  return res.json();
}
