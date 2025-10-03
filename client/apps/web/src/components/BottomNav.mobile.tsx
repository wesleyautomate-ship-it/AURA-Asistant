import React from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import type { View as AppView } from '../types';

interface Props {
  activeView: AppView;
  onNavigate: (v: AppView) => void;
  onOpenCommandCenter: () => void;
}

const BottomNav: React.FC<Props> = ({ activeView, onNavigate, onOpenCommandCenter }) => {
  return (
    <View style={styles.container}>
      <TouchableOpacity onPress={() => onNavigate('dashboard')} style={styles.item}>
        <Text style={[styles.label, activeView === 'dashboard' && styles.active]}>Dashboard</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => onNavigate('tasks')} style={styles.item}>
        <Text style={[styles.label, activeView === 'tasks' && styles.active]}>Tasks</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={onOpenCommandCenter} style={[styles.item, styles.cta]}>
        <Text style={styles.ctaText}>+</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => onNavigate('chat')} style={styles.item}>
        <Text style={[styles.label, activeView === 'chat' && styles.active]}>Chat</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => onNavigate('analytics')} style={styles.item}>
        <Text style={[styles.label, activeView === 'analytics' && styles.active]}>Analytics</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#fff',
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#E5E7EB',
  },
  item: { padding: 8 },
  label: { color: '#6B7280', fontSize: 12, fontWeight: '600' },
  active: { color: '#111827' },
  cta: {
    backgroundColor: '#111827',
    borderRadius: 20,
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ctaText: { color: 'white', fontSize: 22, fontWeight: '800', marginTop: -2 },
});

export default BottomNav;
