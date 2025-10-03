import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function ClientsScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Clients</Text>
      <Text>Client list will appear here.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 8 }
});
