export interface BrochureSection {
  label: string;
  body?: string;
  bullets?: string[];
}

export interface BrochureStructuredData {
  listingId?: string;
  title?: string;
  subtitle?: string;
  price?: string;
  location?: string;
  propertyType?: string;
  bedrooms?: number | string;
  bathrooms?: number | string;
  areaSqft?: number | string;
  highlights: string[];
  description?: string;
  sections: BrochureSection[];
  neighborhoodInsights: string[];
  amenities: Record<string, string[]>;
  callToAction?: string;
}

const coerceNumber = (value: unknown): number | undefined => {
  const num = typeof value === 'string' ? Number(value) : typeof value === 'number' ? value : undefined;
  return Number.isFinite(num) ? Number(num) : undefined;
};

export const parseBrochureStructuredData = (raw: Record<string, unknown> | null | undefined): BrochureStructuredData => {
  const data = raw || {};

  const sections = Array.isArray(data['sections'])
    ? (data['sections'] as Array<Record<string, unknown>>).map((section) => ({
        label: String(section['label'] || ''),
        body: section['body'] ? String(section['body']) : undefined,
        bullets: Array.isArray(section['bullets'])
          ? (section['bullets'] as unknown[]).map((bullet) => String(bullet))
          : []
      }))
    : [];

  const amenities = (data['amenities'] && typeof data['amenities'] === 'object')
    ? Object.entries(data['amenities'] as Record<string, unknown>).reduce<Record<string, string[]>>((acc, [key, value]) => {
        if (Array.isArray(value)) {
          acc[key] = value.map((item) => String(item));
        }
        return acc;
      }, {})
    : {};

  return {
    listingId: data['listing_id'] ? String(data['listing_id']) : undefined,
    title: data['title'] ? String(data['title']) : undefined,
    subtitle: data['subtitle'] ? String(data['subtitle']) : undefined,
    price: data['price'] ? String(data['price']) : undefined,
    location: data['location'] ? String(data['location']) : undefined,
    propertyType: data['property_type'] ? String(data['property_type']) : undefined,
    bedrooms: coerceNumber(data['bedrooms']) ?? (data['bedrooms'] ? String(data['bedrooms']) : undefined),
    bathrooms: coerceNumber(data['bathrooms']) ?? (data['bathrooms'] ? String(data['bathrooms']) : undefined),
    areaSqft: coerceNumber(data['area_sqft']) ?? (data['area_sqft'] ? String(data['area_sqft']) : undefined),
    highlights: Array.isArray(data['highlights']) ? (data['highlights'] as unknown[]).map((item) => String(item)) : [],
    description: data['description'] ? String(data['description']) : undefined,
    sections,
    neighborhoodInsights: Array.isArray(data['neighborhood_insights'])
      ? (data['neighborhood_insights'] as unknown[]).map((item) => String(item))
      : [],
    amenities,
    callToAction: data['call_to_action'] ? String(data['call_to_action']) : undefined,
  };
};

export const formatSqft = (value: number | string | undefined): string | undefined => {
  if (value === undefined || value === null) return undefined;
  const num = typeof value === 'string' ? Number(value) : value;
  if (!Number.isFinite(num)) {
    return String(value);
  }
  return `${Math.round(num).toLocaleString()} sq ft`;
};

export const formatBedrooms = (value: number | string | undefined): string | undefined => {
  if (value === undefined || value === null) return undefined;
  const num = typeof value === 'string' ? Number(value) : value;
  if (!Number.isFinite(num)) {
    return String(value);
  }
  return `${num} ${num === 1 ? 'bed' : 'beds'}`;
};

export const formatBathrooms = (value: number | string | undefined): string | undefined => {
  if (value === undefined || value === null) return undefined;
  const num = typeof value === 'string' ? Number(value) : value;
  if (!Number.isFinite(num)) {
    return String(value);
  }
  return `${num} ${num === 1 ? 'bath' : 'baths'}`;
};
