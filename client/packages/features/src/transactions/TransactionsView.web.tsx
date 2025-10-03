import React, { useMemo, useState } from 'react';
import { TransactionTimeline, DocumentManager } from '@propertypro/ui';
import { Transaction } from '@propertypro/features/types';
import { MOCK_TRANSACTIONS } from './mockTransactions';

type Props = {
  onBack?: () => void;
};

const statusColor: Record<Transaction['status'], string> = {
  draft: 'bg-gray-200 text-gray-700',
  in_progress: 'bg-orange-100 text-orange-800',
  pending_approval: 'bg-amber-100 text-amber-800',
  completed: 'bg-emerald-100 text-emerald-800',
  cancelled: 'bg-rose-100 text-rose-800',
};

const TransactionsView: React.FC<Props> = ({ onBack }) => {
  const [txs, setTxs] = useState<Transaction[]>(MOCK_TRANSACTIONS as unknown as Transaction[]);
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(txs[0] || null);

  const progress = useMemo(() => {
    if (!selectedTx?.milestones?.length) return 0;
    const done = selectedTx.milestones.filter((m) => m.completed).length;
    return Math.round((done / selectedTx.milestones.length) * 100);
  }, [selectedTx]);

  const handleDocumentChange = (docs: Transaction['documents']) => {
    if (!selectedTx) return;
    const updated = { ...selectedTx, documents: docs, updatedAt: new Date().toISOString() };
    setSelectedTx(updated);
    setTxs((prev) => prev.map((tx) => (tx.id === updated.id ? updated : tx)));
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b px-4 py-3">
        {onBack ? (
          <button onClick={onBack} className="text-sm text-gray-600 transition hover:text-gray-900">
            &lt; Back
          </button>
        ) : (
          <span />
        )}
        <h1 className="text-lg font-semibold">Transactions</h1>
        <div />
      </div>

      <div className="flex flex-1 overflow-hidden">
        <aside className="w-72 border-r">
          <div className="flex items-center justify-between border-b px-4 py-3">
            <span className="font-medium">All Transactions</span>
            <button className="rounded bg-orange-600 px-3 py-1 text-sm text-white">New</button>
          </div>
          <ul className="divide-y">
            {txs.map((tx) => {
              const pct = Math.round((tx.milestones.filter((m) => m.completed).length / tx.milestones.length) * 100);
              const active = selectedTx?.id === tx.id;
              return (
                <li key={tx.id}>
                  <button
                    className={`flex w-full flex-col gap-2 px-4 py-3 text-left transition ${
                      active ? 'bg-gray-50' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setSelectedTx(tx)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900">{tx.id}</span>
                      <span className={`text-xs px-2 py-0.5 rounded ${statusColor[tx.status]}`}>
                        {tx.status.replace('_', ' ')}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">
                      Closing: {new Date(tx.expectedClosingDate).toLocaleDateString()}
                    </span>
                    <div className="h-1 overflow-hidden rounded bg-gray-200">
                      <div className="h-full rounded bg-orange-600" style={{ width: `${pct}%` }} />
                    </div>
                  </button>
                </li>
              );
            })}
          </ul>
        </aside>

        <main className="flex-1 overflow-y-auto">
          {!selectedTx ? (
            <div className="p-10 text-center text-gray-500">Select a transaction to review progress.</div>
          ) : (
            <div className="flex flex-col gap-5 p-6">
              <section className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">Transaction {selectedTx.id}</h2>
                  <p className="text-sm text-gray-500">
                    Expected closing {new Date(selectedTx.expectedClosingDate).toLocaleDateString()}
                  </p>
                </div>
                <div className="w-48 rounded-lg border border-gray-200 px-4 py-3">
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>Progress</span>
                    <span>{progress}%</span>
                  </div>
                  <div className="mt-2 h-2 overflow-hidden rounded bg-gray-200">
                    <div className="h-full rounded bg-orange-600" style={{ width: `${progress}%` }} />
                  </div>
                </div>
              </section>

              <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-base font-medium text-gray-900">Milestone Timeline</h3>
                  <button className="text-sm text-orange-700 hover:underline">Send update</button>
                </div>
                <TransactionTimeline milestones={selectedTx.milestones} />
              </section>

              <section className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-base font-medium text-gray-900">Documents</h3>
                  <span className="text-sm text-gray-500">
                    {(selectedTx.documents?.length ?? 0)} file{(selectedTx.documents?.length ?? 0) === 1 ? '' : 's'}
                  </span>
                </div>
                <DocumentManager documents={selectedTx.documents ?? []} onDocumentsChange={handleDocumentChange} />
              </section>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default TransactionsView;