import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { palette, spacing, typography } from '../theme';
import type { PropertyDetailProps } from './PropertyDetail';

export default function PropertyDetailMobile(props: PropertyDetailProps) {
  const {
    title,
    price,
    beds,
    baths,
    sqft,
    imageUrl,
    address,
    city,
    state,
    zip,
    status,
    onBack,
  } = props;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.contentContainer}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.headerRow}>
        {!!onBack && (
          <TouchableOpacity accessibilityRole="button" onPress={onBack} style={styles.backBtn}>
            <Text style={styles.backText}>Back</Text>
          </TouchableOpacity>
        )}
        <View style={styles.titleWrap}>
          <Text style={styles.title}>{title}</Text>
          {!!status && (
            <View style={[styles.statusBadge, statusStyles[status] || statusStyles.draft]}>
              <Text style={styles.statusText}>{status.toUpperCase()}</Text>
            </View>
          )}
        </View>
      </View>

      <View style={styles.imageWrap}>
        {imageUrl ? (
          <Image source={{ uri: imageUrl }} style={styles.image} resizeMode="cover" />
        ) : (
          <View style={styles.imagePlaceholder} />
        )}
      </View>

      <View style={styles.summaryCard}>
        <Text style={styles.meta}>
          {(beds ?? 0)} BR • {(baths ?? 0)} BA • {(sqft ?? 0)} sqft
        </Text>
        {typeof price === 'number' && (
          <Text style={styles.price}>
            {Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(price)}
          </Text>
        )}
        <Text style={styles.addr}>{[address, city, state, zip].filter(Boolean).join(', ')}</Text>
      </View>
    </ScrollView>
  );
}

const titleFont = typography.scale['2xl'];
const priceFont = typography.scale.xl;
const bodyFont = typography.scale.base;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: palette['surface.base'],
  },
  contentContainer: {
    paddingBottom: spacing.space['12'],
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.space['4'],
    paddingTop: spacing.space['6'],
    paddingBottom: spacing.space['4'],
    gap: spacing.space['3'],
  },
  backBtn: {
    backgroundColor: palette['surface.raised'],
    borderRadius: spacing.radii.md,
    paddingHorizontal: spacing.space['4'],
    paddingVertical: spacing.space['2.5'],
    shadowColor: 'transparent',
    borderWidth: 1,
    borderColor: palette['border.subtle'],
  },
  backText: {
    color: palette['text.primary'],
    fontWeight: '600',
    fontSize: bodyFont.fontSize,
  },
  titleWrap: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: spacing.space['3'],
  },
  title: {
    flexShrink: 1,
    color: palette['text.primary'],
    fontSize: titleFont.fontSize,
    lineHeight: titleFont.lineHeight,
    fontWeight: typography.weights.bold.toString() as unknown as number,
  },
  imageWrap: {
    marginHorizontal: spacing.space['4'],
    borderRadius: spacing.radii.xl,
    overflow: 'hidden',
    backgroundColor: palette['surface.raised'],
    shadowColor: 'transparent',
  },
  image: {
    width: '100%',
    height: 240,
  },
  imagePlaceholder: {
    width: '100%',
    height: 240,
    backgroundColor: palette['accent.properties'] + '22',
  },
  statusBadge: {
    backgroundColor: palette['accent.properties'],
    borderRadius: spacing.radii.pill,
    paddingHorizontal: spacing.space['3'],
    paddingVertical: spacing.space['1.5'],
  },
  statusText: {
    color: palette['text.inverse'],
    fontSize: typography.scale.sm.fontSize,
    fontWeight: typography.weights.semibold.toString() as unknown as number,
  },
  summaryCard: {
    marginHorizontal: spacing.space['4'],
    marginTop: spacing.space['5'],
    backgroundColor: palette['surface.raised'],
    borderRadius: spacing.radii.lg,
    paddingHorizontal: spacing.space['4'],
    paddingVertical: spacing.space['5'],
    gap: spacing.space['3'],
    borderWidth: 1,
    borderColor: palette['border.subtle'],
    shadowColor: 'transparent',
  },
  meta: {
    color: palette['text.secondary'],
    fontSize: bodyFont.fontSize,
    lineHeight: bodyFont.lineHeight,
    fontWeight: typography.weights.medium.toString() as unknown as number,
  },
  price: {
    color: palette['accent.properties'],
    fontSize: priceFont.fontSize,
    lineHeight: priceFont.lineHeight,
    fontWeight: typography.weights.bold.toString() as unknown as number,
  },
  addr: {
    color: palette['text.primary'],
    fontSize: bodyFont.fontSize,
    lineHeight: bodyFont.lineHeight,
  },
});

const statusStyles: Record<string, { backgroundColor: string }> = {
  draft: { backgroundColor: palette['border.subtle'] },
  active: { backgroundColor: palette['accent.properties'] },
  pending: { backgroundColor: palette['accent.packages'] },
  sold: { backgroundColor: palette['status.success'] },
};
