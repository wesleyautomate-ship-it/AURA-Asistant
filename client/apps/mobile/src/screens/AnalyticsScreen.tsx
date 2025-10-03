import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const KPIS = [
  { label: 'Market Activity', value: 87, color: '#10B981' },
  { label: 'Investment Potential', value: 92, color: '#3B82F6' },
  { label: 'Price Stability', value: 78, color: '#F59E0B' },
];

const TRENDING = [
  { name: 'Dubai Marina', price: 1450, change: 8.5, trend: 'up' },
  { name: 'Downtown Dubai', price: 1650, change: 3.2, trend: 'up' },
  { name: 'Palm Jumeirah', price: 2200, change: -1.2, trend: 'down' },
  { name: 'JBR', price: 1350, change: 6.8, trend: 'up' },
];

export default function AnalyticsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Analytics</Text>

      <View style={styles.kpis}>
        {KPIS.map(k => (
          <View key={k.label} style={styles.kpiCard}>
            <Text style={styles.kpiLabel}>{k.label}</Text>
            <Text style={[styles.kpiValue, { color: k.color }]}>{k.value}</Text>
          </View>
        ))}
      </View>

      <Text style={styles.sectionTitle}>Trending Areas</Text>
      <View style={{ gap: 8 }}>
        {TRENDING.map(t => (
          <View key={t.name} style={styles.trendRow}>
            <Text style={styles.trendName}>{t.name}</Text>
            <Text style={styles.trendMeta}>{t.price} AED/sqft</Text>
            <Text style={[styles.trendChange, { color: t.trend === 'up' ? '#10B981' : '#EF4444' }]}>
              {t.change}%
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 12, color: '#111827' },
  kpis: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  kpiCard: { flex: 1, backgroundColor: '#F9FAFB', padding: 12, borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  kpiLabel: { color: '#6B7280', fontWeight: '700' },
  kpiValue: { fontSize: 22, fontWeight: '900', marginTop: 6 },
  sectionTitle: { color: '#111827', fontWeight: '800', marginBottom: 8, marginTop: 4 },
  trendRow: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#fff', borderRadius: 10, padding: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  trendName: { flex: 1, color: '#111827', fontWeight: '700' },
  trendMeta: { color: '#6B7280' },
  trendChange: { fontWeight: '800' },
});
