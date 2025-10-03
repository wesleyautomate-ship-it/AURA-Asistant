import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';

export interface PropertyDetailProps {
  title: string;
  price?: number;
  beds?: number;
  baths?: number;
  sqft?: number;
  imageUrl?: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  status?: 'draft' | 'active' | 'pending' | 'sold';
  onBack?: () => void;
}

export default function PropertyDetail({ title, price, beds, baths, sqft, imageUrl, address, city, state, zip, status, onBack }: PropertyDetailProps) {
  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        {!!onBack && (
          <TouchableOpacity onPress={onBack} style={styles.backBtn}>
            <Text style={styles.backText}>Back</Text>
          </TouchableOpacity>
        )}
        <Text style={styles.title}>{title}</Text>
      </View>

      <View style={styles.imageWrap}>
        {imageUrl ? (
          <Image source={{ uri: imageUrl }} style={styles.image} />
        ) : (
          <View style={styles.imagePlaceholder} />
        )}
        {!!status && (
          <View style={[styles.statusBadge, statusStyles[status] || statusStyles.draft]}>
            <Text style={styles.statusText}>{status.toUpperCase()}</Text>
          </View>
        )}
      </View>

      <Text style={styles.meta}>
        {(beds ?? 0)} BR • {(baths ?? 0)} BA • {(sqft ?? 0)} sqft
      </Text>
      {typeof price === 'number' && (
        <Text style={styles.price}>{Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(price)}</Text>
      )}
      <Text style={styles.addr}>{[address, city, state, zip].filter(Boolean).join(', ')}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  headerRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12, gap: 12 },
  backBtn: { backgroundColor: '#1f2937', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 6 },
  backText: { color: '#fff', fontWeight: '700' },
  title: { fontSize: 20, fontWeight: '800', color: '#111827' },
  imageWrap: { height: 220, borderRadius: 12, overflow: 'hidden', backgroundColor: '#EFF6FF', position: 'relative' },
  image: { width: '100%', height: '100%' },
  imagePlaceholder: { flex: 1, backgroundColor: '#DBEAFE' },
  statusBadge: { position: 'absolute', top: 10, left: 10, paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  statusText: { color: '#fff', fontSize: 12, fontWeight: '700' },
  meta: { color: '#6B7280', marginTop: 10 },
  price: { color: '#111827', fontSize: 18, fontWeight: '800', marginTop: 6 },
  addr: { color: '#111827', marginTop: 6 },
});

const statusStyles: Record<string, any> = {
  draft: { backgroundColor: '#9CA3AF' },
  active: { backgroundColor: '#2563eb' },
  pending: { backgroundColor: '#F59E0B' },
  sold: { backgroundColor: '#10B981' },
};


