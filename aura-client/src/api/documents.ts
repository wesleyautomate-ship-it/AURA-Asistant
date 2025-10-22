import api from '../services/http';

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
  const { data } = await api.post<BrochureResult>('/export/brochure-mock', input || {});
  return data;
}

// Generic HTML save via export service; returns a file URL in BrochureResult shape
export async function saveHtml(payload: { html: string; prefix?: string }): Promise<BrochureResult> {
  const { data } = await api.post<BrochureResult>('/export/html-save', {
    html: payload.html,
    prefix: payload.prefix || 'brochure',
  });
  return data;
}
