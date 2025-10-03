import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';

export interface PropertyFormValues {
  title: string;
  description: string;
  location: string;
  propertyType: string;
  price?: number;
  beds?: number;
  baths?: number;
  sqft?: number;
  imageUrl?: string;
}

export interface PropertyFormProps {
  initial?: PropertyFormValues;
  submitting?: boolean;
  onSubmit: (values: PropertyFormValues) => void;
  onCancel?: () => void;
}

const PROPERTY_TYPES = ['apartment', 'villa', 'townhouse', 'penthouse', 'plot'];

export default function PropertyForm({ initial, submitting, onSubmit, onCancel }: PropertyFormProps) {
  const [title, setTitle] = useState(initial?.title ?? '');
  const [description, setDescription] = useState(initial?.description ?? '');
  const [location, setLocation] = useState(initial?.location ?? 'Dubai Marina');
  const [propertyType, setPropertyType] = useState(initial?.propertyType ?? 'apartment');
  const [price, setPrice] = useState(initial?.price?.toString() ?? '');
  const [beds, setBeds] = useState(initial?.beds?.toString() ?? '');
  const [baths, setBaths] = useState(initial?.baths?.toString() ?? '');
  const [sqft, setSqft] = useState(initial?.sqft?.toString() ?? '');
  const [imageUrl, setImageUrl] = useState(initial?.imageUrl ?? '');

  const handleSubmit = () => {
    onSubmit({
      title: title.trim(),
      description: description.trim() || `${title.trim()} property summary`,
      location: location.trim() || 'Dubai',
      propertyType,
      price: price ? Number(price) : undefined,
      beds: beds ? Number(beds) : undefined,
      baths: baths ? Number(baths) : undefined,
      sqft: sqft ? Number(sqft) : undefined,
      imageUrl: imageUrl || undefined,
    });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Property Details</Text>
      <TextInput style={styles.input} placeholder="Title" value={title} onChangeText={setTitle} />
      <TextInput
        style={[styles.input, styles.textarea]}
        placeholder="Marketing description"
        multiline
        numberOfLines={3}
        value={description}
        onChangeText={setDescription}
      />
      <TextInput style={styles.input} placeholder="Location" value={location} onChangeText={setLocation} />

      <View style={styles.typeSection}>
        <Text style={styles.label}>Property Type</Text>
        <View style={styles.typeRow}>
          {PROPERTY_TYPES.map((type) => {
            const isActive = propertyType === type;
            return (
              <TouchableOpacity
                key={type}
                onPress={() => setPropertyType(type)}
                style={[styles.typePill, isActive && styles.typePillActive]}
              >
                <Text style={[styles.typePillText, isActive && styles.typePillTextActive]}>{type}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      <View style={styles.row}>
        <TextInput style={[styles.input, styles.rowItem]} placeholder="Price (AED)" keyboardType="numeric" value={price} onChangeText={setPrice} />
        <TextInput style={[styles.input, styles.rowItem]} placeholder="Beds" keyboardType="numeric" value={beds} onChangeText={setBeds} />
      </View>
      <View style={styles.row}>
        <TextInput style={[styles.input, styles.rowItem]} placeholder="Baths" keyboardType="numeric" value={baths} onChangeText={setBaths} />
        <TextInput style={[styles.input, styles.rowItem]} placeholder="Square Feet" keyboardType="numeric" value={sqft} onChangeText={setSqft} />
      </View>
      <TextInput style={styles.input} placeholder="Image URL" value={imageUrl} onChangeText={setImageUrl} />

      <View style={styles.actions}>
        {!!onCancel && (
          <TouchableOpacity style={[styles.btn, styles.cancel]} onPress={onCancel} disabled={submitting}>
            <Text style={styles.btnText}>Cancel</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={[styles.btn, styles.submit]}
          onPress={handleSubmit}
          disabled={submitting || !title.trim()}
        >
          {submitting ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Save</Text>}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: '#fff', borderRadius: 12, padding: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  header: { fontSize: 16, fontWeight: '700', marginBottom: 8, color: '#111827' },
  label: { fontSize: 12, fontWeight: '700', color: '#0f172a', marginBottom: 6, textTransform: 'uppercase' },
  input: { backgroundColor: '#fff', borderColor: '#93C5FD', borderWidth: 1, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 10, marginBottom: 10 },
  textarea: { minHeight: 72, textAlignVertical: 'top' },
  row: { flexDirection: 'row', gap: 10 },
  rowItem: { flex: 1 },
  typeSection: { marginBottom: 12 },
  typeRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  typePill: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 9999, borderWidth: 1, borderColor: '#E5E7EB' },
  typePillActive: { backgroundColor: '#1d4ed8', borderColor: '#1d4ed8' },
  typePillText: { color: '#0f172a', fontSize: 12, fontWeight: '600', textTransform: 'capitalize' },
  typePillTextActive: { color: '#fff' },
  actions: { flexDirection: 'row', justifyContent: 'flex-end', gap: 10, marginTop: 6 },
  btn: { paddingHorizontal: 14, paddingVertical: 10, borderRadius: 10 },
  cancel: { backgroundColor: '#1f2937' },
  submit: { backgroundColor: '#2563eb' },
  btnText: { color: '#fff', fontWeight: '700' },
});
