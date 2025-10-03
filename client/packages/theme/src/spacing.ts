export type SpaceKey =
  | '0'
  | 'px'
  | '0.5'
  | '1'
  | '1.5'
  | '2'
  | '2.5'
  | '3'
  | '3.5'
  | '4'
  | '5'
  | '6'
  | '8'
  | '10'
  | '12'
  | '16';

type SpaceScale = Record<SpaceKey, number>;

export interface RadiiTokens {
  none: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  pill: number;
}

export interface ElevationTokens {
  none: string;
  sm: string;
  md: string;
  lg: string;
}

export interface SpacingTokens {
  space: SpaceScale;
  radii: RadiiTokens;
  shadows: ElevationTokens;
}

export const spacing: SpacingTokens = {
  space: {
    '0': 0,
    px: 1,
    '0.5': 2,
    '1': 4,
    '1.5': 6,
    '2': 8,
    '2.5': 10,
    '3': 12,
    '3.5': 14,
    '4': 16,
    '5': 20,
    '6': 24,
    '8': 32,
    '10': 40,
    '12': 48,
    '16': 64,
  },
  radii: {
    none: 0,
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    pill: 999,
  },
  shadows: {
    none: 'none',
    sm: '0 2px 6px rgba(15, 23, 42, 0.08)',
    md: '0 4px 12px rgba(15, 23, 42, 0.12)',
    lg: '0 12px 24px rgba(15, 23, 42, 0.18)',
  },
};
