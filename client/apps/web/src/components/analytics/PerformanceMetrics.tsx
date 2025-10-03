import React, { useMemo } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { usePropertyStore, selectProperties } from '../../store/propertyStore';
import { summarizeComps } from '../../utils/analyticsUtils';

export default function PerformanceMetrics() {
  const properties = usePropertyStore(selectProperties);
  const active = useMemo(() => properties.filter(p => p.status === 'active'), [properties]);
  const sold = useMemo(() => properties.filter(p => p.status === 'sold'), [properties]);
  const soldSummary = useMemo(() => summarizeComps(sold as any), [sold]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Performance Metrics</Text>
      <View style={styles.kpis}>
        <View style={styles.kpiCard}>
          <Text style={styles.kpiLabel}>Active Listings</Text>
          <Text style={[styles.kpiValue, { color: '#0891b2' }]}>{active.length}</Text>
        </View>
        <View style={styles.kpiCard}>
          <Text style={styles.kpiLabel}>Sold Listings</Text>
          <Text style={[styles.kpiValue, { color: '#10B981' }]}>{sold.length}</Text>
        </View>
        <View style={styles.kpiCard}>
          <Text style={styles.kpiLabel}>Median Sold PPS</Text>
          <Text style={[styles.kpiValue, { color: '#F59E0B' }]}>{soldSummary.medianPricePerSqft.toFixed(0)}</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: '#fff', borderRadius: 12, padding: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  title: { fontSize: 16, fontWeight: '800', marginBottom: 8, color: '#0f172a' },
  kpis: { flexDirection: 'row', gap: 12 },
  kpiCard: { flex: 1, backgroundColor: '#ECFEFF', padding: 12, borderRadius: 12, borderWidth: 1, borderColor: '#A5F3FC' },
  kpiLabel: { color: '#334155', fontWeight: '700' },
  kpiValue: { fontSize: 22, fontWeight: '900', marginTop: 6 },
});


