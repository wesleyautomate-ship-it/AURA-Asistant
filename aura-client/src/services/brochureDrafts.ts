import { BrochureTemplateKey, BrochureDraft } from '../types/brochure';
import { createDraft, getDraft, updateDraft, listDrafts } from '../store/brochureDraftStore';

export type { BrochureDraft, BrochureTemplateKey };

// Simple service passthrough for now; place for future API integration
export const brochureDraftService = {
  createDraft,
  getDraft,
  updateDraft,
  listDrafts,
};

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

