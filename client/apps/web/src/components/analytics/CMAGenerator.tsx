import React, { useMemo, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { usePropertyStore, selectProperties } from '../../store/propertyStore';
import { computeComps, summarizeComps, recommendStrategy, exportCSV } from '../../utils/analyticsUtils';

export default function CMAGenerator() {
  const properties = usePropertyStore(selectProperties);
  const [subjectId, setSubjectId] = useState<string | number | null>(properties[0]?.id ?? null);

  const subject = useMemo(() => properties.find(p => p.id === subjectId) || null, [properties, subjectId]);
  const comps = useMemo(() => subject ? computeComps(subject, properties.filter(p => p.id !== subject.id)) : [], [subject, properties]);
  const summary = useMemo(() => summarizeComps(comps), [comps]);
  const strategy = useMemo(() => subject ? recommendStrategy(subject, comps) : null, [subject, comps]);

  const handleExport = () => {
    try {
      const rows = comps.map(c => ({ id: c.id, title: c.title, price: c.price, beds: c.beds, baths: c.baths, sqft: c.sqft }));
      const csv = exportCSV(rows);
      // In web, trigger download; in RN, you would integrate with FileSystem. For now, show preview length.
      Alert.alert('Export Ready', `CSV length: ${csv.length} chars`);
    } catch (e: any) {
      Alert.alert('Export Failed', e?.message || 'Unknown error');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>CMA Generator</Text>
      <ScrollView horizontal style={styles.selector} contentContainerStyle={{ gap: 8 }}>
        {properties.map(p => (
          <TouchableOpacity key={String(p.id)} onPress={() => setSubjectId(p.id)} style={[styles.chip, subjectId === p.id && styles.chipActive]}>
            <Text style={[styles.chipText, subjectId === p.id && styles.chipTextActive]}>{p.title}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {subject && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Subject Property</Text>
          <Text style={styles.rowText}>{subject.title}</Text>
          <Text style={styles.rowMeta}>Beds {subject.beds ?? '-'} • Baths {subject.baths ?? '-'} • {subject.sqft ?? '-'} sqft</Text>
        </View>
      )}

      <View style={styles.row}>
        <View style={[styles.card, { flex: 1 }]}> 
          <Text style={styles.cardTitle}>Summary</Text>
          <Text style={styles.rowText}>Comps: {summary.count}</Text>
          <Text style={styles.rowText}>Avg Price: {Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(summary.averagePrice || 0)}</Text>
          <Text style={styles.rowText}>Median PPS: {summary.medianPricePerSqft.toFixed(0)}</Text>
        </View>
        <View style={[styles.card, { flex: 1 }]}> 
          <Text style={styles.cardTitle}>Strategy</Text>
          <Text style={styles.rowText}>{strategy?.strategy.toUpperCase() ?? '-'}</Text>
          <Text style={styles.rowMeta}>{strategy?.rationale ?? '-'}</Text>
        </View>
      </View>

      <TouchableOpacity style={styles.exportBtn} onPress={handleExport}>
        <Text style={styles.exportText}>Export Comps CSV</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: '#fff', borderRadius: 12, padding: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  title: { fontSize: 16, fontWeight: '800', marginBottom: 8, color: '#0f172a' },
  selector: { marginBottom: 8 },
  chip: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 999, borderWidth: 1, borderColor: '#0891b2' },
  chipActive: { backgroundColor: '#0891b2' },
  chipText: { color: '#0891b2', fontWeight: '700' },
  chipTextActive: { color: '#fff' },
  card: { backgroundColor: '#F0FDFA', borderRadius: 12, padding: 12, borderWidth: 1, borderColor: '#A7F3D0' },
  cardTitle: { color: '#0f172a', fontWeight: '800', marginBottom: 6 },
  row: { flexDirection: 'row', gap: 12, marginTop: 10 },
  rowText: { color: '#0f172a', fontWeight: '700' },
  rowMeta: { color: '#334155', marginTop: 2 },
  exportBtn: { marginTop: 12, backgroundColor: '#0891b2', paddingVertical: 10, borderRadius: 10, alignItems: 'center' },
  exportText: { color: '#fff', fontWeight: '800' }
});


