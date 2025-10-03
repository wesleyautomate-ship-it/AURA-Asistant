import React, { useMemo, useState } from 'react';
import { SafeAreaView, View, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';

import DashboardScreen from './src/screens/DashboardScreen';
import TasksScreen from './src/screens/TasksScreen';
import ChatScreen from './src/screens/ChatScreen';
import AnalyticsScreen from './src/screens/AnalyticsScreen';
import PropertiesScreen from './src/screens/PropertiesScreen';
import ContentScreen from './src/screens/ContentScreen';
import WorkflowsScreen from './src/screens/WorkflowsScreen';
import TransactionsScreen from './src/screens/TransactionsScreen';

import BottomNav from './src/components/BottomNav';
import CommandCenter from './src/components/CommandCenter';
import { ACTION_ITEMS, MOCK_TASKS } from './src/constants';
import type { View as AppView, ActionId, Task } from './src/types';

export default function App() {
  const [currentView, setCurrentView] = useState<AppView>('dashboard');
  const [isCommandCenterOpen, setCommandCenterOpen] = useState(false);
  const [tasks, setTasks] = useState<Task[]>(MOCK_TASKS);

  const onActionClick = (id: ActionId) => {
    // Map action ids to top-level views where applicable
    if (id === 'workflows') return setCurrentView('workflows');
    if (id === 'properties') return setCurrentView('properties');
    if (id === 'content') return setCurrentView('content');
    if (id === 'analytics') return setCurrentView('analytics');
    if (id === 'transactions') return setCurrentView('transactions');
    // For now, other actions return to dashboard placeholder sections
    setCurrentView('dashboard');
  };

  const Screen = useMemo(() => {
    switch (currentView) {
      case 'dashboard':
        return (
          <DashboardScreen
            onActionClick={onActionClick}
            onNavigate={setCurrentView}
            actions={ACTION_ITEMS}
          />
        );
      case 'tasks':
        return <TasksScreen tasks={tasks} setTasks={setTasks} />;
      case 'chat':
        return <ChatScreen />;
      case 'properties':
        return <PropertiesScreen />;
      case 'content':
        return <ContentScreen />;
      case 'analytics':
        return <AnalyticsScreen />;
      case 'workflows':
        return <WorkflowsScreen onNavigate={setCurrentView} />;
      case 'transactions':
        return <TransactionsScreen />;
      default:
        return <DashboardScreen onActionClick={onActionClick} onNavigate={setCurrentView} actions={ACTION_ITEMS} />;
    }
  }, [currentView, tasks]);

  return (
    <SafeAreaView style={styles.safe}>
      <StatusBar style="dark" />
      <View style={styles.container}>
        <View style={styles.content}>{Screen}</View>
        <BottomNav
          activeView={currentView}
          onNavigate={setCurrentView}
          onOpenCommandCenter={() => setCommandCenterOpen(true)}
        />
        {isCommandCenterOpen && <CommandCenter onClose={() => setCommandCenterOpen(false)} />}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: '#fff' },
  container: { flex: 1 },
  content: { flex: 1 },
});
