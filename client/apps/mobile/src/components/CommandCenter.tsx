import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { ACTION_ITEMS } from '../constants';

interface Props {
  onClose: () => void;
}

const CommandCenter: React.FC<Props> = ({ onClose }) => {
  return (
    <View style={styles.overlay}>
      <View style={styles.sheet}>
        <View style={styles.header}>
          <Text style={styles.title}>Command Center</Text>
          <TouchableOpacity onPress={onClose}><Text style={styles.close}>Close</Text></TouchableOpacity>
        </View>
        <ScrollView contentContainerStyle={styles.content}>
          {ACTION_ITEMS.map(item => (
            <View key={item.id} style={styles.action}>
              <Text style={styles.actionTitle}>{item.title}</Text>
            </View>
          ))}
        </ScrollView>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.25)',
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  sheet: {
    width: '100%',
    backgroundColor: '#fff',
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    maxHeight: '70%',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#E5E7EB',
  },
  title: { fontSize: 16, fontWeight: '700', color: '#111827' },
  close: { color: '#4B5563', fontWeight: '600' },
  content: { padding: 16, gap: 12 },
  action: { padding: 12, backgroundColor: '#F9FAFB', borderRadius: 10 },
  actionTitle: { color: '#111827', fontWeight: '600' },
});

export default CommandCenter;
