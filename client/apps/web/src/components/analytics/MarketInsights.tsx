import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

type Insight = { label: string; value: string | number; color?: string };

const MOCK: Insight[] = [
  { label: 'Top Neighborhood', value: 'Downtown', color: '#0891b2' },
  { label: 'Avg DOM', value: 28, color: '#10B981' },
  { label: 'Inventory Change', value: '+4.2%', color: '#F59E0B' },
];

export default function MarketInsights() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Market Insights</Text>
      <View style={styles.row}>
        {MOCK.map(m => (
          <View key={m.label} style={styles.card}>
            <Text style={styles.label}>{m.label}</Text>
            <Text style={[styles.value, { color: m.color || '#0891b2' }]}>{m.value}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: '#fff', borderRadius: 12, padding: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  title: { fontSize: 16, fontWeight: '800', marginBottom: 8, color: '#0f172a' },
  row: { flexDirection: 'row', gap: 12 },
  card: { flex: 1, backgroundColor: '#F0FDFA', padding: 12, borderRadius: 12, borderWidth: 1, borderColor: '#A7F3D0' },
  label: { color: '#334155', fontWeight: '700' },
  value: { fontSize: 22, fontWeight: '900', marginTop: 6 },
});


