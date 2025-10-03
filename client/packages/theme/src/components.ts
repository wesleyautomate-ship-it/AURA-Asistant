import { palette } from './colors';
import { spacing } from './spacing';
import { typography } from './typography';

export interface ComponentVariant {
  backgroundColor?: string;
  borderColor?: string;
  textColor?: string;
  iconColor?: string;
  radius?: number;
  paddingVertical?: number;
  paddingHorizontal?: number;
  shadow?: string;
  gap?: number;
}

export interface ComponentTokens {
  card: ComponentVariant;
  cardElevated: ComponentVariant;
  badge: ComponentVariant;
  buttonPrimary: ComponentVariant;
  buttonSecondary: ComponentVariant;
  buttonGhost: ComponentVariant;
  input: ComponentVariant;
  sectionHeader: {
    titleColor: string;
    subtitleColor: string;
    titleSize: number;
    subtitleSize: number;
    titleWeight: number;
    subtitleWeight: number;
    gap: number;
  };
}

export const components: ComponentTokens = {
  card: {
    backgroundColor: palette['surface.raised'],
    borderColor: palette['border.subtle'],
    textColor: palette['text.primary'],
    radius: spacing.radii.lg,
    paddingVertical: spacing.space['4'],
    paddingHorizontal: spacing.space['5'],
    shadow: spacing.shadows.none,
    gap: spacing.space['4'],
  },
  cardElevated: {
    backgroundColor: palette['surface.raised'],
    borderColor: palette['border.subtle'],
    textColor: palette['text.primary'],
    radius: spacing.radii.lg,
    paddingVertical: spacing.space['4'],
    paddingHorizontal: spacing.space['5'],
    shadow: spacing.shadows.md,
    gap: spacing.space['4'],
  },
  badge: {
    backgroundColor: palette['surface.raised'],
    borderColor: palette['border.subtle'],
    textColor: palette['text.secondary'],
    radius: spacing.radii.pill,
    paddingVertical: spacing.space['1'],
    paddingHorizontal: spacing.space['2'],
    gap: spacing.space['1'],
  },
  buttonPrimary: {
    backgroundColor: palette['brand.primary'],
    textColor: palette['text.inverse'],
    radius: spacing.radii.md,
    paddingVertical: spacing.space['3'],
    paddingHorizontal: spacing.space['5'],
    shadow: spacing.shadows.sm,
    gap: spacing.space['2'],
  },
  buttonSecondary: {
    backgroundColor: palette['surface.raised'],
    borderColor: palette['border.emphasis'],
    textColor: palette['text.primary'],
    radius: spacing.radii.md,
    paddingVertical: spacing.space['3'],
    paddingHorizontal: spacing.space['5'],
    gap: spacing.space['2'],
  },
  buttonGhost: {
    backgroundColor: 'transparent',
    borderColor: 'transparent',
    textColor: palette['brand.primary'],
    radius: spacing.radii.md,
    paddingVertical: spacing.space['3'],
    paddingHorizontal: spacing.space['5'],
    gap: spacing.space['2'],
  },
  input: {
    backgroundColor: palette['surface.raised'],
    borderColor: palette['border.subtle'],
    textColor: palette['text.primary'],
    radius: spacing.radii.md,
    paddingVertical: spacing.space['3'],
    paddingHorizontal: spacing.space['4'],
    gap: spacing.space['2'],
  },
  sectionHeader: {
    titleColor: palette['text.primary'],
    subtitleColor: palette['text.secondary'],
    titleSize: typography.scale['xl'].fontSize,
    subtitleSize: typography.scale['sm'].fontSize,
    titleWeight: typography.weights.semibold,
    subtitleWeight: typography.weights.medium,
    gap: spacing.space['2'],
  },
};
