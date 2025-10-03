import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import { apiGet } from '../services/api';

type Property = {
  id: number;
  title: string;
  description?: string;
  price?: number;
  location?: string;
  property_type?: string;
  bedrooms?: number;
  bathrooms?: number;
  area_sqft?: number | null;
};

export default function PropertiesScreen() {
  const [data, setData] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        // After simplifying the router prefix, the properties list is at /api/properties
        const res = await apiGet<Property[]>(`/api/properties`);
        if (!cancelled) {
          setData(res);
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? 'Failed to load properties');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Properties</Text>
      {loading && (
        <View style={{ paddingTop: 24 }}>
          <ActivityIndicator />
        </View>
      )}
      {!!error && !loading && (
        <Text style={{ color: '#B91C1C', marginBottom: 8 }}>Error: {error}</Text>
      )}
      {!loading && (
        <FlatList
          data={data}
          keyExtractor={(item) => String(item.id)}
          ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
          renderItem={({ item }) => (
            <TouchableOpacity style={styles.card}>
              <View style={styles.thumb}>
                <View style={styles.thumbPlaceholder} />
              </View>
              <View style={styles.info}>
                <Text style={styles.propTitle}>{item.title}</Text>
                <Text style={styles.meta}>
                  {(item.location || 'Unknown')} • {(item.area_sqft ?? 0)} sqft • {(item.bedrooms ?? 0)}BR/{(item.bathrooms ?? 0)}BA
                </Text>
                {typeof item.price === 'number' && (
                  <Text style={styles.price}>
                    {Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(item.price)}
                  </Text>
                )}
              </View>
            </TouchableOpacity>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 12 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 12, flexDirection: 'row', gap: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  thumb: { width: 84, height: 84, borderRadius: 8, overflow: 'hidden', backgroundColor: '#F3F4F6' },
  thumbPlaceholder: { flex: 1, backgroundColor: '#E5E7EB' },
  info: { flex: 1 },
  propTitle: { color: '#111827', fontWeight: '700' },
  meta: { color: '#6B7280', fontSize: 12, marginTop: 2 },
  price: { color: '#111827', fontWeight: '800', marginTop: 6 }
});
