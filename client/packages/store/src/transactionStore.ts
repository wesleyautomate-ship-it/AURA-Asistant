import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { apiGet, apiPost, apiPut } from '@propertypro/services';
import type { BaseAsyncSlice, RequestStatus, Id, WithTimestamps } from './types';

export type MilestoneStatus = 'pending' | 'in_progress' | 'completed' | 'blocked';

export interface Milestone extends WithTimestamps<{ id: Id; name: string; dueDate: string; status: MilestoneStatus; notes?: string; }>{}

export interface Transaction extends WithTimestamps<{
  id: Id;
  propertyId: Id;
  buyerId?: Id;
  sellerId?: Id;
  status: 'pending' | 'in_progress' | 'closed' | 'canceled';
  offerPrice?: number;
  finalPrice?: number;
  transactionType: string;
  milestones: Milestone[];
  documents?: string[];
}> {}

export interface TransactionState {
  transactions: Transaction[];
  fetch: BaseAsyncSlice;
  mutate: BaseAsyncSlice;
  fetchTransactions: () => Promise<void>;
  createTransaction: (payload: { propertyId: Id; transactionType: string; offerPrice?: number }) => Promise<Transaction>;
  updateTransactionStatus: (id: Id, status: string) => Promise<Transaction>;
}

const initialAsync: BaseAsyncSlice = { status: 'idle', error: null };

function toFrontendTransaction(apiTransaction: any): Transaction {
  return {
    id: String(apiTransaction.id),
    propertyId: String(apiTransaction.property_id),
    buyerId: apiTransaction.buyer_id ? String(apiTransaction.buyer_id) : undefined,
    sellerId: apiTransaction.seller_id ? String(apiTransaction.seller_id) : undefined,
    status: (apiTransaction.transaction_status || 'pending') as Transaction['status'],
    offerPrice: apiTransaction.offer_price ? Number(apiTransaction.offer_price) : undefined,
    finalPrice: apiTransaction.final_price ? Number(apiTransaction.final_price) : undefined,
    transactionType: apiTransaction.transaction_type || 'sale',
    milestones: [],
    documents: [],
    createdAt: apiTransaction.created_at ?? undefined,
    updatedAt: apiTransaction.updated_at ?? undefined,
  };
}

export const useTransactionStore = create<TransactionState>()(devtools((set, get) => ({
  transactions: [],
  fetch: initialAsync,
  mutate: initialAsync,

  fetchTransactions: async () => {
    set({ fetch: { status: 'loading', error: null } });
    try {
      const data = await apiGet<any[]>('/api/v1/transactions');
      const normalized = Array.isArray(data) ? data.map(toFrontendTransaction) : [];
      set({ transactions: normalized, fetch: { status: 'success', error: null, lastUpdated: new Date().toISOString() } });
    } catch (e: any) {
      set({ fetch: { status: 'error', error: e.message } });
    }
  },

  createTransaction: async ({ propertyId, transactionType, offerPrice }) => {
    set({ mutate: { status: 'loading', error: null } });
    try {
      const payload = {
        property_id: Number(propertyId),
        transaction_type: transactionType,
        offer_price: offerPrice,
      };
      const created = await apiPost<any>('/api/v1/transactions', payload);
      const normalized = toFrontendTransaction(created);
      set({ transactions: [normalized, ...get().transactions], mutate: { status: 'success', error: null, lastUpdated: new Date().toISOString() } });
      return normalized;
    } catch (e: any) {
      set({ mutate: { status: 'error', error: e.message } });
      throw e;
    }
  },

  updateTransactionStatus: async (id, status) => {
    set({ mutate: { status: 'loading', error: null } });
    try {
      const updated = await apiPut<any>(`/api/v1/transactions/${id}`, { transaction_status: status });
      const normalized = toFrontendTransaction(updated);
      set({ transactions: get().transactions.map((tx) => (tx.id === String(id) ? normalized : tx)), mutate: { status: 'success', error: null, lastUpdated: new Date().toISOString() } });
      return normalized;
    } catch (e: any) {
      set({ mutate: { status: 'error', error: e.message } });
      throw e;
    }
  },
})));

export const selectTransactions = (s: TransactionState) => s.transactions;
export const selectTransactionById = (id: Id) => (s: TransactionState) => s.transactions.find((t) => t.id === id) || null;
export const selectUpcomingDeadlines = (daysAhead: number) => (s: TransactionState) => {
  const now = new Date();
  const cutoff = new Date(now.getTime() + daysAhead * 24 * 60 * 60 * 1000);
  return s.transactions.flatMap((t) =>
    t.milestones
      .filter((m) => new Date(m.dueDate) <= cutoff && m.status !== 'completed')
      .map((m) => ({ txId: t.id, milestone: m }))
  );
};
export const selectTransactionFetchStatus = (s: TransactionState): RequestStatus => s.fetch.status;
export const selectTransactionMutateStatus = (s: TransactionState): RequestStatus => s.mutate.status;
