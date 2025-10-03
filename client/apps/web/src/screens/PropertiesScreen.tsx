import React, { useEffect, useMemo, useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import PropertyCard from '../components/PropertyCard';
import PropertySearch from '../components/PropertySearch';
import PropertyDetail from '../components/PropertyDetail';
import PropertyForm, { PropertyFormValues } from '../components/PropertyForm';
import {
  usePropertyStore,
  selectProperties,
  selectPropertyFetchStatus,
  selectPropertyMutateStatus,
} from '../store/propertyStore';
import type { Property } from '@propertypro/store';

export default function PropertiesScreen() {
  const items = usePropertyStore(selectProperties);
  const fetchStatus = usePropertyStore(selectPropertyFetchStatus);
  const mutateStatus = usePropertyStore(selectPropertyMutateStatus);
  const fetchProperties = usePropertyStore((s) => s.fetchProperties);
  const addProperty = usePropertyStore((s) => s.addProperty);
  const updateProperty = usePropertyStore((s) => s.updateProperty);
  const deleteProperty = usePropertyStore((s) => s.deleteProperty);

  const [query, setQuery] = useState('');
  const [mode, setMode] = useState<'list' | 'detail' | 'form'>('list');
  const [selectedId, setSelectedId] = useState<string | number | null>(null);
  const [editingId, setEditingId] = useState<string | number | null>(null);

  useEffect(() => {
    if (fetchStatus === 'idle') {
      fetchProperties();
    }
  }, [fetchProperties, fetchStatus]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((i) => (i.title || '').toLowerCase().includes(q));
  }, [items, query]);

  const selectedItem = useMemo(() => items.find((i) => i.id === selectedId) || null, [items, selectedId]);
  const editingItem = useMemo(() => items.find((i) => i.id === editingId) || null, [items, editingId]);

  const handleOpenDetail = (id: string | number) => {
    setSelectedId(id);
    setMode('detail');
  };

  const handleOpenCreate = () => {
    setEditingId(null);
    setMode('form');
  };

  const handleOpenEdit = (id: string | number) => {
    setEditingId(id);
    setMode('form');
  };

  const handleDelete = async (id: string | number) => {
    try {
      await deleteProperty(id as any);
    } catch (e: any) {
      Alert.alert('Failed to delete property', e?.message || 'Unknown error');
    }
  };

  const handleSubmitForm = async (values: PropertyFormValues) => {
    try {
      if (editingId) {
        await updateProperty(editingId as any, values as Partial<Property>);
      } else {
        await addProperty(values as Omit<Property, 'id'>);
      }
      setMode('list');
      setEditingId(null);
    } catch (e: any) {
      Alert.alert('Failed to save property', e?.message || 'Unknown error');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Properties</Text>
      {mode === 'list' && (
        <>
          {fetchStatus === 'loading' && (
            <View style={{ paddingTop: 24 }}>
              <ActivityIndicator />
            </View>
          )}
          <PropertySearch query={query} onChangeQuery={setQuery} />
          {fetchStatus !== 'loading' && (
            <FlatList
              data={filtered as Property[]}
              keyExtractor={(item) => String(item.id)}
              ItemSeparatorComponent={() => <View style={{ height: 12 }} />}
              renderItem={({ item }) => (
                <PropertyCard
                  id={item.id}
                  title={item.title}
                  price={item.price}
                  beds={item.beds}
                  baths={item.baths}
                  sqft={item.sqft}
                  imageUrl={item.imageUrl}
                  status={item.status}
                  onPress={() => handleOpenDetail(item.id)}
                  onEdit={() => handleOpenEdit(item.id)}
                  onDelete={() => handleDelete(item.id)}
                />
              )}
            />
          )}

          <TouchableOpacity style={styles.fab} onPress={handleOpenCreate}>
            <Text style={styles.fabText}>+</Text>
          </TouchableOpacity>
        </>
      )}

      {mode === 'detail' && selectedItem && (
        <PropertyDetail
          title={selectedItem.title}
          price={selectedItem.price}
          beds={selectedItem.beds}
          baths={selectedItem.baths}
          sqft={selectedItem.sqft}
          imageUrl={selectedItem.imageUrl}
          address={selectedItem.location || selectedItem.address}
          city={selectedItem.city}
          state={selectedItem.state}
          zip={selectedItem.zip}
          status={selectedItem.status}
          onBack={() => setMode('list')}
        />
      )}

      {mode === 'form' && (
        <View style={styles.formOverlay}>
          <PropertyForm
            initial={editingItem ? {
              title: editingItem.title,
              description: editingItem.description,
              location: editingItem.location,
              propertyType: editingItem.propertyType,
              price: editingItem.price,
              beds: editingItem.beds,
              baths: editingItem.baths,
              sqft: editingItem.sqft,
              imageUrl: editingItem.imageUrl,
            } : undefined}
            submitting={mutateStatus === 'loading'}
            onSubmit={handleSubmitForm}
            onCancel={() => { setMode('list'); setEditingId(null); }}
          />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 12 },
  fab: { position: 'absolute', right: 20, bottom: 20, backgroundColor: '#2563eb', width: 56, height: 56, borderRadius: 28, alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOpacity: 0.2, shadowOffset: { width: 0, height: 2 }, shadowRadius: 4 },
  fabText: { color: '#fff', fontSize: 28, fontWeight: '800', lineHeight: 28 },
  formOverlay: { position: 'absolute', left: 16, right: 16, bottom: 90, backgroundColor: '#F9FAFB', borderRadius: 12, padding: 12, borderWidth: 1, borderColor: '#E5E7EB' },
});
