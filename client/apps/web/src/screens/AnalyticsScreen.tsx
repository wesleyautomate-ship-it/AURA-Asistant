import React, { useMemo, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import CMAGenerator from '../components/analytics/CMAGenerator';
import PerformanceMetrics from '../components/analytics/PerformanceMetrics';
import MarketInsights from '../components/analytics/MarketInsights';
import { usePropertyStore, selectProperties } from '../store/propertyStore';
import { DateRange, filterByDateRange } from '../utils/analyticsUtils';

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
  const properties = usePropertyStore(selectProperties);
  const [rangeKey, setRangeKey] = useState<'7d' | '30d' | '90d' | 'ytd'>('30d');

  const range: DateRange | undefined = useMemo(() => {
    const end = new Date();
    const start = new Date();
    if (rangeKey === '7d') start.setDate(end.getDate() - 7);
    else if (rangeKey === '30d') start.setDate(end.getDate() - 30);
    else if (rangeKey === '90d') start.setDate(end.getDate() - 90);
    else {
      start.setMonth(0, 1);
      start.setHours(0, 0, 0, 0);
    }
    return { start, end };
  }, [rangeKey]);

  const filtered = useMemo(() => filterByDateRange(properties as any, range), [properties, range]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Analytics</Text>

      <View style={styles.filters}>
        {(['7d','30d','90d','ytd'] as const).map(k => (
          <TouchableOpacity key={k} onPress={() => setRangeKey(k)} style={[styles.filterChip, rangeKey === k && styles.filterActive]}>
            <Text style={[styles.filterText, rangeKey === k && styles.filterTextActive]}>{k.toUpperCase()}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.kpis}>
        {KPIS.map(k => (
          <View key={k.label} style={styles.kpiCard}>
            <Text style={styles.kpiLabel}>{k.label}</Text>
            <Text style={[styles.kpiValue, { color: k.color }]}>{k.value}</Text>
          </View>
        ))}
      </View>

      <PerformanceMetrics />
      <View style={{ height: 12 }} />
      <MarketInsights />
      <View style={{ height: 12 }} />
      <CMAGenerator />

      <Text style={styles.sectionCaption}>Filtered properties: {filtered.length}</Text>
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
  filters: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  filterChip: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 999, borderWidth: 1, borderColor: '#0891b2' },
  filterActive: { backgroundColor: '#0891b2' },
  filterText: { color: '#0891b2', fontWeight: '700' },
  filterTextActive: { color: '#fff' },
  sectionCaption: { marginTop: 12, color: '#334155' }
});
