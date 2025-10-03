import React, { useMemo } from 'react';
import { View, TextInput, StyleSheet } from 'react-native';

export interface PropertySearchProps {
  query: string;
  onChangeQuery: (q: string) => void;
}

export default function PropertySearch({ query, onChangeQuery }: PropertySearchProps) {
  // Controlled input for simplicity; debouncing can be added later if needed
  return (
    <View style={styles.container}>
      <TextInput
        style={styles.input}
        placeholder="Search properties..."
        placeholderTextColor="#6B7280"
        value={query}
        onChangeText={onChangeQuery}
        autoCorrect={false}
        autoCapitalize="none"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { marginBottom: 12 },
  input: {
    backgroundColor: '#fff',
    borderColor: '#93C5FD',
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    color: '#111827'
  },
});


