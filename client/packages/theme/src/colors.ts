export type ColorToken =
  | 'brand.primary'
  | 'brand.secondary'
  | 'brand.tertiary'
  | 'surface.base'
  | 'surface.raised'
  | 'surface.overlay'
  | 'surface.inverted'
  | 'border.subtle'
  | 'border.emphasis'
  | 'text.primary'
  | 'text.secondary'
  | 'text.muted'
  | 'text.inverse'
  | 'accent.properties'
  | 'accent.crm'
  | 'accent.marketing'
  | 'accent.packages'
  | 'accent.analytics'
  | 'accent.chat'
  | 'status.success'
  | 'status.warning'
  | 'status.error';

export type AccentKey =
  | 'properties'
  | 'crm'
  | 'marketing'
  | 'packages'
  | 'analytics'
  | 'chat';

type Palette = Record<ColorToken, string> & {
  accents: Record<AccentKey, string>;
};

export const palette: Palette = {
  'brand.primary': '#2563eb',
  'brand.secondary': '#0f172a',
  'brand.tertiary': '#1e293b',
  'surface.base': '#f8fafc',
  'surface.raised': '#ffffff',
  'surface.overlay': 'rgba(15, 23, 42, 0.72)',
  'surface.inverted': '#0b1120',
  'border.subtle': 'rgba(15, 23, 42, 0.08)',
  'border.emphasis': 'rgba(15, 23, 42, 0.18)',
  'text.primary': '#0f172a',
  'text.secondary': '#334155',
  'text.muted': '#64748b',
  'text.inverse': '#f8fafc',
  'accent.properties': '#2563eb',
  'accent.crm': '#059669',
  'accent.marketing': '#7c3aed',
  'accent.packages': '#ea580c',
  'accent.analytics': '#0891b2',
  'accent.chat': '#dc2626',
  'status.success': '#16a34a',
  'status.warning': '#facc15',
  'status.error': '#ef4444',
  accents: {
    properties: '#2563eb',
    crm: '#059669',
    marketing: '#7c3aed',
    packages: '#ea580c',
    analytics: '#0891b2',
    chat: '#dc2626',
  },
};

export const getAccentColor = (key: AccentKey): string => palette.accents[key];
