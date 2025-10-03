import React, { useMemo, useState } from 'react';
import { SafeAreaView, View, Text, StyleSheet, FlatList, TouchableOpacity, ScrollView } from 'react-native';

import { Transaction } from '@propertypro/features/types';
import { TransactionTimeline, DocumentManager } from '@propertypro/ui';

import { MOCK_TRANSACTIONS } from './mockTransactions';

type Props = {
  onBack?: () => void;
};

const statusColor: Record<Transaction['status'], string> = {
  draft: '#9ca3af',
  in_progress: '#ea580c',
  pending_approval: '#f59e0b',
  completed: '#10b981',
  cancelled: '#ef4444',
};

const statusLabel: Record<Transaction['status'], string> = {
  draft: 'Draft',
  in_progress: 'In Progress',
  pending_approval: 'Pending Approval',
  completed: 'Completed',
  cancelled: 'Cancelled',
};

const TransactionsView: React.FC<Props> = ({ onBack }) => {
  const [transactions, setTransactions] = useState<Transaction[]>(MOCK_TRANSACTIONS as Transaction[]);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(transactions[0] ?? null);

  const progress = useMemo(() => {
    if (!selectedTx || !selectedTx.milestones?.length) return 0;
    const completed = selectedTx.milestones.filter((m) => m.completed).length;
    return Math.round((completed / selectedTx.milestones.length) * 100);
  }, [selectedTx]);

  const updateDocuments = (docs: Transaction['documents']) => {
    if (!selectedTx) return;
    const updated = { ...selectedTx, documents: docs, updatedAt: new Date().toISOString() };
    setSelectedTx(updated);
    setTransactions((prev) => prev.map((tx) => (tx.id === updated.id ? updated : tx)));
  };

  const renderItem = ({ item }: { item: Transaction }) => {
    const completed = item.milestones?.filter((m) => m.completed).length ?? 0;
    const total = item.milestones?.length ?? 1;
    const pct = Math.round((completed / total) * 100);
    const active = selectedTx?.id === item.id;

    return (
      <TouchableOpacity
        style={[styles.transactionItem, active && styles.transactionItemActive]}
        onPress={() => setSelectedTx(item)}
        accessibilityRole="button"
      >
        <View style={styles.transactionRow}>
          <Text style={styles.transactionId}>{item.id}</Text>
          <View style={[styles.statusBadge, { backgroundColor: statusColor[item.status] }]}>
            <Text style={styles.statusText}>{statusLabel[item.status]}</Text>
          </View>
        </View>
        <Text style={styles.transactionMeta}>Closing {new Date(item.expectedClosingDate).toLocaleDateString()}</Text>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${pct}%`, backgroundColor: statusColor[item.status] }]} />
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        {onBack ? (
          <TouchableOpacity style={styles.backButton} onPress={onBack} accessibilityRole="button">
            <Text style={styles.backText}>Back</Text>
          </TouchableOpacity>
        ) : (
          <View style={styles.backPlaceholder} />
        )}
        <Text style={styles.headerTitle}>Transactions</Text>
        <View style={styles.backPlaceholder} />
      </View>

      <View style={styles.content}>
        <View style={styles.sidebar}>
          <View style={styles.sidebarHeader}>
            <Text style={styles.sidebarTitle}>All Transactions</Text>
            <TouchableOpacity style={styles.newButton}>
              <Text style={styles.newButtonText}>New</Text>
            </TouchableOpacity>
          </View>
          <FlatList
            data={transactions}
            keyExtractor={(item) => item.id}
            renderItem={renderItem}
            contentContainerStyle={styles.listContent}
          />
        </View>

        <ScrollView style={styles.detail} contentContainerStyle={styles.detailContent}>
          {!selectedTx ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyTitle}>Select a transaction</Text>
              <Text style={styles.emptyBody}>Choose a record from the list to review progress and documents.</Text>
            </View>
          ) : (
            <View style={styles.detailCard}>
              <View style={styles.detailHeader}>
                <View>
                  <Text style={styles.detailTitle}>Transaction {selectedTx.id}</Text>
                  <Text style={styles.detailSubtitle}>
                    Expected closing {new Date(selectedTx.expectedClosingDate).toLocaleDateString()}
                  </Text>
                </View>
                <View style={styles.progressSummary}>
                  <Text style={styles.progressSummaryLabel}>Progress</Text>
                  <Text style={styles.progressSummaryValue}>{progress}%</Text>
                </View>
              </View>

              <View style={styles.section}>
                <View style={styles.sectionHeader}>
                  <Text style={styles.sectionTitle}>Milestones</Text>
                  <Text style={styles.sectionMeta}>{selectedTx.milestones.length} total</Text>
                </View>
                <TransactionTimeline milestones={selectedTx.milestones} />
              </View>

              <View style={styles.section}>
                <View style={styles.sectionHeader}>
                  <Text style={styles.sectionTitle}>Documents</Text>
                  <Text style={styles.sectionMeta}>
                    {(selectedTx.documents?.length ?? 0)} file{(selectedTx.documents?.length ?? 0) === 1 ? '' : 's'}
                  </Text>
                </View>
                <DocumentManager documents={selectedTx.documents ?? []} onDocumentsChange={updateDocuments} />
              </View>
            </View>
          )}
        </ScrollView>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#ffffff',
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#e2e8f0',
  },
  backButton: {
    paddingVertical: 6,
    paddingHorizontal: 10,
  },
  backPlaceholder: {
    width: 48,
  },
  backText: {
    color: '#2563eb',
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#0f172a',
  },
  content: {
    flex: 1,
    flexDirection: 'row',
  },
  sidebar: {
    width: 260,
    borderRightWidth: StyleSheet.hairlineWidth,
    borderRightColor: '#e2e8f0',
    backgroundColor: '#ffffff',
  },
  sidebarHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#e2e8f0',
  },
  sidebarTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0f172a',
  },
  newButton: {
    backgroundColor: '#ea580c',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  newButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  listContent: {
    padding: 12,
  },
  transactionItem: {
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'transparent',
  },
  transactionItemActive: {
    backgroundColor: '#fff7ed',
    borderColor: '#fdba74',
  },
  transactionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  transactionId: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0f172a',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 999,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  transactionMeta: {
    fontSize: 12,
    color: '#475569',
    marginTop: 6,
  },
  progressBar: {
    marginTop: 10,
    height: 6,
    borderRadius: 999,
    backgroundColor: '#e2e8f0',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 999,
  },
  detail: {
    flex: 1,
  },
  detailContent: {
    padding: 16,
  },
  emptyState: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#0f172a',
    marginBottom: 8,
  },
  emptyBody: {
    fontSize: 14,
    color: '#475569',
    textAlign: 'center',
  },
  detailCard: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 12,
    elevation: 4,
  },
  detailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  detailTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0f172a',
  },
  detailSubtitle: {
    fontSize: 14,
    color: '#475569',
    marginTop: 4,
  },
  progressSummary: {
    alignItems: 'center',
    backgroundColor: '#f8fafc',
    paddingVertical: 12,
    paddingHorizontal: 18,
    borderRadius: 12,
  },
  progressSummaryLabel: {
    fontSize: 12,
    color: '#475569',
  },
  progressSummaryValue: {
    fontSize: 18,
    fontWeight: '700',
    color: '#0f172a',
  },
  section: {
    marginTop: 24,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0f172a',
  },
  sectionMeta: {
    fontSize: 12,
    color: '#64748b',
  },
});

export default TransactionsView;