import React, { useEffect, useMemo, useState } from 'react';
import ContactsWorkspaceV2 from "../components/Dashboard/Contacts/ContactsWorkspaceV2";
import type { Contact } from '../types/contacts';
import { getContacts } from '../services/contactsApi';

export default function Contacts() {
  const [data, setData] = useState<Contact[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    setLoading(true);
    setError(null);
    getContacts(ac.signal)
      .then((list) => setData(list))
      .catch((e) => {
        if (e?.name !== 'AbortError') setError('Failed to load contacts');
      })
      .finally(() => setLoading(false));
    return () => ac.abort();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-blue-50">
      <div className="max-w-4xl mx-auto px-4 py-6 sm:py-8">
        {loading && (
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
            <p className="text-sm text-gray-600">Loading contacts…</p>
          </div>
        )}

        {!loading && error && (
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {!loading && !error && data && data.length === 0 && (
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 text-center">
            <p className="text-sm text-gray-600">No contacts yet.</p>
          </div>
        )}

        {!loading && !error && data && data.length > 0 && (
          <ContactsWorkspaceV2 contacts={data.map(c => ({
            id: c.id,
            name: c.name,
            status: (c.temperature === 'Dormant' ? 'Cold' : c.temperature) as any,
            lastActivity: c.lastActivityAt ? timeAgo(c.lastActivityAt) : undefined,
            lastActivityIso: c.lastActivityAt,
            tags: c.tags || [],
          }))} />
        )}
      </div>
    </div>
  );
}

function timeAgo(iso: string) {
  const d = new Date(iso);
  const diff = Date.now() - d.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}
