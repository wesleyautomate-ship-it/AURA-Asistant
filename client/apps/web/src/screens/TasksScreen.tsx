import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import type { Task } from '../types';

interface Props {
  tasks: Task[];
  setTasks: (updater: (prev: Task[]) => Task[] | Task[]) => void;
}

export default function TasksScreen({ tasks, setTasks }: Props) {
  const toggle = (id: string) => {
    setTasks(prev => prev.map(t => t.id === id ? ({
      ...t,
      status: t.status === 'completed' ? 'pending' : 'completed'
    }) : t));
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Tasks</Text>
      <FlatList
        data={tasks}
        keyExtractor={(item) => item.id}
        ItemSeparatorComponent={() => <View style={styles.sep} />}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <View style={{ flex: 1 }}>
              <Text style={styles.taskTitle}>{item.title}</Text>
              {item.dueDate ? (
                <Text style={styles.meta}>Due {item.dueDate}</Text>
              ) : null}
            </View>
            <TouchableOpacity style={[styles.badge, item.status === 'completed' && styles.badgeDone]} onPress={() => toggle(item.id)}>
              <Text style={[styles.badgeText, item.status === 'completed' && styles.badgeTextDone]}>
                {item.status === 'completed' ? 'Done' : 'Mark Done'}
              </Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 12 },
  row: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10 },
  taskTitle: { color: '#111827', fontWeight: '600' },
  meta: { color: '#6B7280', fontSize: 12, marginTop: 2 },
  sep: { height: 1, backgroundColor: '#F3F4F6' },
  badge: { paddingHorizontal: 10, paddingVertical: 6, borderRadius: 9999, backgroundColor: '#111827' },
  badgeText: { color: '#fff', fontWeight: '700' },
  badgeDone: { backgroundColor: '#E5E7EB' },
  badgeTextDone: { color: '#111827' }
});
