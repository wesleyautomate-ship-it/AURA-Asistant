export type BrochureTemplateKey = 'clean-minimal' | 'luxury-showcase' | 'neighborhood-highlight';

export interface BrochureDraft {
  id: string;                 // uuid
  template: BrochureTemplateKey;
  createdAt: string;          // ISO
  updatedAt: string;          // ISO
  status: 'draft' | 'rendering' | 'generating' | 'ready' | 'error';
  propertyId?: string;
  listingData?: any;          // hydrated property details
  brand?: { logoUrl?: string; primary?: string; secondary?: string };
  content?: { title?: string; description?: string; highlights?: string[]; images?: string[] };
  output?: { html?: string; pdfUrl?: string };
  error?: string;
}
