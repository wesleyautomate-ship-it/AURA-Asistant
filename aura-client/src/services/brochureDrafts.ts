import { BrochureTemplateKey, BrochureDraft } from '../types/brochure';
import * as api from '../features/brochure/api/brochure';

export type { BrochureDraft, BrochureTemplateKey };

// Simple service passthrough for now; place for future API integration
function fromServer(d: api.BrochureDraftOut): BrochureDraft {
  const data = d.data || {} as any;
  const brand = data.branding ? {
    logoUrl: data.branding?.logo?.url || undefined,
    primary: data.branding?.primary || undefined,
    secondary: data.branding?.secondary || undefined,
  } : undefined;
  const content = {
    title: data.hero?.title || data.about?.heading || undefined,
    description: data.about?.body || undefined,
    highlights: data.whyInvest?.bullets || [],
    images: data.about?.gallery || [],
  };
  return {
    id: d.id,
    template: (data.templateKey || 'clean-minimal') as BrochureTemplateKey,
    createdAt: d.created_at,
    updatedAt: d.updated_at,
    status: (d.status as any) || 'draft',
    propertyId: data.propertyId || undefined,
    listingData: data.listingData || undefined,
    brand,
    content,
    output: d.download_url ? { pdfUrl: d.download_url } : undefined,
    error: data.meta?.error || undefined,
  };
}

async function createDraft(template: BrochureTemplateKey): Promise<BrochureDraft> {
  const server = await api.createDraft({ templateKey: template });
  return fromServer(server);
}

async function getDraft(id: string): Promise<BrochureDraft> {
  const server = await api.getDraft(id);
  return fromServer(server);
}

async function updateDraft(id: string, patch: Partial<BrochureDraft>): Promise<BrochureDraft> {
  // Map client patch to server patch under data
  const dataPatch: any = {};
  if (patch.propertyId !== undefined) dataPatch.propertyId = patch.propertyId;
  if (patch.listingData) dataPatch.listingData = patch.listingData;
  if (patch.brand) {
    dataPatch.branding = {
      primary: patch.brand.primary,
      secondary: patch.brand.secondary,
      logo: patch.brand.logoUrl ? { url: patch.brand.logoUrl } : null,
    };
  }
  if (patch.content) {
    dataPatch.hero = { title: patch.content.title || '' };
    dataPatch.about = { body: patch.content.description || '', heading: patch.content.title || '' };
    dataPatch.whyInvest = { bullets: patch.content.highlights || [] };
  }
  const payload: api.BrochureDraftPatch = {};
  if (Object.keys(dataPatch).length) payload.data = dataPatch;
  if (patch.status !== undefined) payload.status = patch.status;
  if (patch.propertyId !== undefined) payload.property_id = patch.propertyId;
  if (patch.error !== undefined) payload.error = patch.error;
  if (patch.output?.pdfUrl) payload.download_url = patch.output.pdfUrl;
  const server = await api.updateDraft(id, payload);
  return fromServer(server);
}

async function listDrafts(): Promise<BrochureDraft[]> {
  // No list endpoint yet; return empty to keep UI stable
  return [];
}

export const brochureDraftService = { createDraft, getDraft, updateDraft, listDrafts };

// Helper to map UI template IDs to keys
export function mapTemplateIdToKey(id: string): BrochureTemplateKey {
  switch (id) {
    case 'clean':
      return 'clean-minimal';
    case 'luxury':
      return 'luxury-showcase';
    case 'neighborhood':
      return 'neighborhood-highlight';
    default:
      return 'clean-minimal';
  }
}
