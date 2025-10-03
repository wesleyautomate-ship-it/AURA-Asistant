import React, { useEffect, useMemo, useState } from 'react';
import { useClientStore, selectClients, selectClientFetchStatus } from '../store';
import LeadScoring from '../components/LeadScoring';

export default function ClientsScreen() {
  const clients = useClientStore(selectClients);
  const fetchStatus = useClientStore(selectClientFetchStatus);
  const fetchClients = useClientStore(s => s.fetchClients);

  const [query, setQuery] = useState('');
  const [status, setStatus] = useState<'all' | 'new' | 'contacted' | 'qualified' | 'nurturing' | 'converted' | 'archived'>('all');

  useEffect(() => {
    if (fetchStatus === 'idle') {
      fetchClients();
    }
  }, [fetchStatus, fetchClients]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return clients.filter(c => {
      const matchesQuery = q === '' || c.name.toLowerCase().includes(q) || (c.email || '').toLowerCase().includes(q) || (c.phone || '').toLowerCase().includes(q);
      const matchesStatus = status === 'all' || c.status === status;
      return matchesQuery && matchesStatus;
    });
  }, [clients, query, status]);

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-800">Clients</h2>
        <div className="flex gap-2">
          <select value={status} onChange={e => setStatus(e.target.value as any)} className="text-sm border border-gray-300 rounded-md px-3 py-1">
            <option value="all">All</option>
            <option value="new">New</option>
            <option value="contacted">Contacted</option>
            <option value="qualified">Qualified</option>
            <option value="nurturing">Nurturing</option>
            <option value="converted">Converted</option>
            <option value="archived">Archived</option>
          </select>
          <input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search by name, email, phone" className="text-sm border border-gray-300 rounded-md px-3 py-1 w-64" />
        </div>
      </div>

      {fetchStatus === 'loading' && (
        <div className="text-sm text-gray-500">Loading clients...</div>
      )}

      <div className="grid gap-3">
        {filtered.map(c => (
          <div key={c.id} className="bg-white border rounded p-4">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <div className="font-semibold text-gray-800">{c.name}</div>
                  <span className="text-xs uppercase px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700">{c.status}</span>
                </div>
                <div className="text-sm text-gray-600">{c.email} • {c.phone}</div>
              </div>
              <div className="w-48">
                <LeadScoring score={c.leadScore} />
              </div>
            </div>
            <div className="flex gap-2 mt-3">
              {c.phone && <a href={`tel:${c.phone}`} className="text-xs px-3 py-1 rounded bg-emerald-600 text-white">Call</a>}
              {c.email && <a href={`mailto:${c.email}`} className="text-xs px-3 py-1 rounded bg-emerald-600 text-white">Email</a>}
              <button className="text-xs px-3 py-1 rounded bg-emerald-600 text-white">Message</button>
            </div>
          </div>
        ))}
        {filtered.length === 0 && fetchStatus === 'success' && (
          <div className="text-sm text-gray-500">No clients match your filters.</div>
        )}
      </div>
    </div>
  );
}

