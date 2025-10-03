export type FontScaleKey =
  | '2xs'
  | 'xs'
  | 'sm'
  | 'base'
  | 'lg'
  | 'xl'
  | '2xl'
  | '3xl'
  | '4xl';

export type FontWeightKey = 'regular' | 'medium' | 'semibold' | 'bold';

type FontScale = Record<FontScaleKey, { fontSize: number; lineHeight: number }>;

type FontWeights = Record<FontWeightKey, number>;

export interface TypographyTokens {
  fontFamily: {
    primary: string;
    secondary: string;
    monospace: string;
  };
  scale: FontScale;
  weights: FontWeights;
  letterSpacing: {
    tight: number;
    normal: number;
    wide: number;
  };
}

export const typography: TypographyTokens = {
  fontFamily: {
    primary: '"Inter", "Segoe UI", sans-serif',
    secondary: '"DM Sans", "Segoe UI", sans-serif',
    monospace: '"JetBrains Mono", monospace',
  },
  scale: {
    '2xs': { fontSize: 10, lineHeight: 14 },
    xs: { fontSize: 12, lineHeight: 16 },
    sm: { fontSize: 14, lineHeight: 20 },
    base: { fontSize: 16, lineHeight: 24 },
    lg: { fontSize: 18, lineHeight: 26 },
    xl: { fontSize: 20, lineHeight: 28 },
    '2xl': { fontSize: 24, lineHeight: 32 },
    '3xl': { fontSize: 30, lineHeight: 38 },
    '4xl': { fontSize: 36, lineHeight: 44 },
  },
  weights: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  letterSpacing: {
    tight: -0.15,
    normal: 0,
    wide: 0.2,
  },
};
