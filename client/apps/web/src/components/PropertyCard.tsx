import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';

export interface PropertyCardProps {
  id: string | number;
  title: string;
  price?: number;
  beds?: number;
  baths?: number;
  sqft?: number;
  imageUrl?: string;
  status?: 'draft' | 'active' | 'pending' | 'sold';
  onPress?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

export default function PropertyCard({ title, price, beds, baths, sqft, imageUrl, status, onPress, onEdit, onDelete }: PropertyCardProps) {
  return (
    <TouchableOpacity onPress={onPress} style={styles.card}>
      <View style={styles.thumb}>
        {imageUrl ? (
          <Image source={{ uri: imageUrl }} style={styles.image} />
        ) : (
          <View style={styles.thumbPlaceholder} />
        )}
        {!!status && (
          <View style={[styles.statusBadge, statusStyles[status] || statusStyles.draft]}>
            <Text style={styles.statusText}>{status.toUpperCase()}</Text>
          </View>
        )}
      </View>
      <View style={styles.info}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.meta}>
          {(beds ?? 0)} BR • {(baths ?? 0)} BA • {(sqft ?? 0)} sqft
        </Text>
        {typeof price === 'number' && (
          <Text style={styles.price}>{Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(price)}</Text>
        )}
        <View style={styles.actions}>
          {!!onEdit && (
            <TouchableOpacity onPress={onEdit} style={styles.actionBtn}>
              <Text style={styles.actionText}>Edit</Text>
            </TouchableOpacity>
          )}
          {!!onDelete && (
            <TouchableOpacity onPress={onDelete} style={[styles.actionBtn, styles.deleteBtn]}>
              <Text style={styles.actionText}>Delete</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 12, flexDirection: 'row', gap: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  thumb: { width: 96, height: 96, borderRadius: 8, overflow: 'hidden', backgroundColor: '#EFF6FF', position: 'relative' },
  thumbPlaceholder: { flex: 1, backgroundColor: '#DBEAFE' },
  image: { width: '100%', height: '100%' },
  info: { flex: 1 },
  title: { color: '#111827', fontWeight: '700' },
  meta: { color: '#6B7280', fontSize: 12, marginTop: 2 },
  price: { color: '#111827', fontWeight: '800', marginTop: 6 },
  actions: { flexDirection: 'row', gap: 8, marginTop: 8 },
  actionBtn: { backgroundColor: '#2563eb', paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8 },
  deleteBtn: { backgroundColor: '#1f2937' },
  actionText: { color: '#fff', fontWeight: '600' },
  statusBadge: { position: 'absolute', top: 6, left: 6, paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  statusText: { color: '#fff', fontSize: 10, fontWeight: '700' },
});

const statusStyles: Record<string, any> = {
  draft: { backgroundColor: '#9CA3AF' },
  active: { backgroundColor: '#2563eb' },
  pending: { backgroundColor: '#F59E0B' },
  sold: { backgroundColor: '#10B981' },
};


