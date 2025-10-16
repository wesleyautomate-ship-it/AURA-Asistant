import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Users, Filter, Plus, Search, Tag, Archive, CheckSquare, MoreVertical } from 'lucide-react';
import { addTag as addTagApi } from '../../../services/contactsApi';

type ContactStatus = 'Active' | 'New' | 'Warm' | 'Cold';
type ListFilter = 'All' | ContactStatus | 'Segments';
type Segment = 'Investors' | 'Waterfront' | 'High Intent' | 'Dormant 14d';

export interface ContactItem {
  id: string;
  name: string;
  status: ContactStatus;
  lastActivity?: string;
  lastActivityIso?: string;
  tags?: string[];
}

const statusStyles: Record<ContactStatus, { bg: string; text: string; dot: string }> = {
  Active: { bg: 'bg-green-100', text: 'text-green-700', dot: 'bg-green-500' },
  New: { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
  Warm: { bg: 'bg-amber-100', text: 'text-amber-700', dot: 'bg-amber-500' },
  Cold: { bg: 'bg-gray-100', text: 'text-gray-700', dot: 'bg-gray-400' },
};

const FILTERS: Array<ListFilter> = ['All', 'Active', 'New', 'Warm', 'Cold', 'Segments'];
const SEGMENT_CHIPS: Segment[] = ['Investors', 'Waterfront', 'High Intent', 'Dormant 14d'];

export interface ContactsWorkspaceProps {
  contacts?: ContactItem[];
  onAddContact?: () => void;
}

export default function ContactsWorkspaceV2({ contacts = [], onAddContact }: ContactsWorkspaceProps) {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState<ListFilter>('All');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [selectionMode, setSelectionMode] = useState(false);
  const [segment, setSegment] = useState<Segment | null>(null);
  const [tagsMap, setTagsMap] = useState<Record<string, string[]>>({});

  useEffect(() => {
    const map: Record<string, string[]> = {};
    contacts.forEach(c => { if (c.tags && c.tags.length) map[c.id] = c.tags; });
    setTagsMap(map);
  }, [contacts]);

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search.trim().toLowerCase()), 300);
    return () => clearTimeout(t);
  }, [search]);

  const filtered = useMemo(() => {
    let list = contacts.map(c => ({ ...c, tags: tagsMap[c.id] ?? c.tags ?? [] }));
    if (activeFilter !== 'All' && activeFilter !== 'Segments') list = list.filter(c => c.status === activeFilter);
    if (activeFilter === 'Segments' && segment) list = list.filter(c => inSegment(c, segment));
    if (debouncedSearch) list = list.filter(c => c.name.toLowerCase().includes(debouncedSearch) || (c.tags || []).some(t => t.toLowerCase().includes(debouncedSearch)));
    return list;
  }, [activeFilter, debouncedSearch, contacts, tagsMap, segment]);

  const clearSelection = () => { setSelectedIds(new Set()); setSelectionMode(false); };
  const toggleSelect = (id: string) => setSelectedIds(prev => { const next = new Set(prev); if (next.has(id)) next.delete(id); else next.add(id); return next; });
  const beginLongPressSelect = (id: string) => { setSelectionMode(true); setSelectedIds(prev => new Set(prev).add(id)); };

  return (
    <section className="w-full">
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
        <div className="px-4 pt-4 pb-3 sm:px-6 sm:pt-5 sm:pb-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center justify-center w-9 h-9 rounded-xl bg-emerald-100">
                <Users className="w-5 h-5 text-emerald-600" />
              </span>
              <div>
                <h2 className="text-base sm:text-lg font-semibold text-gray-900">Your Contacts</h2>
                <p className="text-xs sm:text-sm text-gray-500">{filtered.length} shown · {contacts.length} total</p>
              </div>
            </div>
            <button onClick={onAddContact} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 text-white text-xs sm:text-sm font-medium hover:bg-blue-700 active:scale-95 transition" aria-label="Add contact">
              <Plus className="w-4 h-4" />
              <span className="hidden xs:inline">Add</span>
            </button>
          </div>
        </div>

        <div className="flex flex-col max-h-[60vh] sm:max-h-[65vh]">
          <div className="overflow-y-auto overscroll-contain">
            <div className="sticky top-0 z-10 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/70 border-b border-gray-100">
              <div className="px-4 pt-2 pb-2 sm:px-6">
                <div className="flex items-center gap-2 overflow-x-auto scrollbar-hide -mx-1 px-1">
                  <div className="flex items-center text-gray-500 mr-1 shrink-0"><Filter className="w-4 h-4" /></div>
                  {FILTERS.map(f => (
                    <button key={f} onClick={() => { setActiveFilter(f); if (f !== 'Segments') setSegment(null); }} className={`px-3 py-1.5 text-xs sm:text-sm rounded-full border transition whitespace-nowrap ${activeFilter === f ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`} aria-pressed={activeFilter === f}>
                      {f}
                    </button>
                  ))}
                </div>
                {activeFilter === 'Segments' && (
                  <div className="mt-2 flex items-center gap-2 overflow-x-auto scrollbar-hide -mx-1 px-1">
                    {SEGMENT_CHIPS.map(s => (
                      <button key={s} onClick={() => setSegment(prev => prev === s ? null : s)} className={`px-3 py-1.5 text-xs sm:text-sm rounded-full border transition whitespace-nowrap ${segment === s ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'}`} aria-pressed={segment === s}>
                        {s}
                      </button>
                    ))}
                  </div>
                )}
                <div className="mt-2">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search contacts" className="w-full pl-9 pr-3 py-2 text-sm sm:text-base rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" aria-label="Search contacts" />
                  </div>
                </div>
              </div>
            </div>

            <ul className="divide-y divide-gray-100">
              {filtered.map((c, idx) => (
                <motion.li key={c.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2, delay: Math.min(idx * 0.02, 0.2) }} className="px-4 py-3 sm:px-6 sm:py-4 cursor-pointer" onClick={() => {
                  if (selectionMode) toggleSelect(c.id); else navigate(`/contacts/${c.id}` as const, { state: { contact: { id: c.id, name: c.name, temperature: c.status, lastActivityAt: c.lastActivityIso ?? c.lastActivity } } });
                }}>
                  <ContactRow
                    contact={c}
                    selected={selectedIds.has(c.id)}
                    selectionMode={selectionMode}
                    onToggleSelect={() => toggleSelect(c.id)}
                    onLongPressSelect={() => beginLongPressSelect(c.id)}
                    onAddTag={async () => {
                      const t = window.prompt('Add tag');
                      if (t && t.trim()) {
                        const updated = await addTagApi(c.id, t.trim());
                        setTagsMap(prev => ({ ...prev, [c.id]: updated }));
                      }
                    }}
                  />
                </motion.li>
              ))}
              {filtered.length === 0 && (<li className="px-4 py-6 text-center text-sm text-gray-500">No contacts match your search/filter.</li>)}
            </ul>

            {selectedIds.size > 0 && (
              <div className="sticky bottom-0 z-10">
                <div className="m-3 rounded-xl border border-gray-200 bg-white shadow-md px-3 py-2 sm:px-4 sm:py-2 flex items-center justify-between gap-2">
                  <div className="text-xs sm:text-sm text-gray-700">{selectedIds.size} selected</div>
                  <div className="flex items-center gap-2">
                    <button className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-gray-300 text-gray-700 text-xs sm:text-sm hover:bg-gray-50" onClick={() => { const t = window.prompt('Add tag to selected'); if (t && t.trim()) { selectedIds.forEach(async id => { const updated = await addTagApi(id, t.trim()); setTagsMap(prev => ({ ...prev, [id]: updated })); }); } }}>
                      <Tag className="w-4 h-4" />
                      <span className="hidden xs:inline">Add Tag</span>
                    </button>
                    <button className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-amber-600 text-white text-xs sm:text-sm hover:bg-amber-700" onClick={() => { /* TODO: archive */ }}>
                      <Archive className="w-4 h-4" />
                      <span className="hidden xs:inline">Archive</span>
                    </button>
                    <button className="ml-1 text-xs text-gray-500 hover:text-gray-700" onClick={clearSelection}>Clear</button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function ContactRow({ contact, selected, selectionMode, onToggleSelect, onLongPressSelect, onAddTag }: { contact: ContactItem; selected?: boolean; selectionMode?: boolean; onToggleSelect?: () => void; onLongPressSelect?: () => void; onAddTag?: () => void; }) {
  const style = statusStyles[contact.status];
  const initials = getInitials(contact.name);
  const pressTimer = useRef<number | null>(null);

  return (
    <div className="flex items-center gap-3 select-none"
      onPointerDown={() => { if (pressTimer.current) window.clearTimeout(pressTimer.current); pressTimer.current = window.setTimeout(() => { onLongPressSelect?.(); }, 500); }}
      onPointerUp={() => { if (pressTimer.current) window.clearTimeout(pressTimer.current); pressTimer.current = null; }}
      onPointerCancel={() => { if (pressTimer.current) window.clearTimeout(pressTimer.current); pressTimer.current = null; }}
    >
      {selectionMode && (
        <button aria-pressed={!!selected} onClick={(e) => { e.stopPropagation(); onToggleSelect?.(); }} className={`shrink-0 inline-flex items-center justify-center w-5 h-5 rounded border ${selected ? 'bg-blue-600 border-blue-600 text-white' : 'bg-white border-gray-300 text-transparent'} focus:outline-none focus:ring-2 focus:ring-blue-500`}>
          <CheckSquare className="w-3.5 h-3.5 text-white" />
        </button>
      )}

      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-purple-100 border border-gray-200 flex items-center justify-center">
        <span className="text-sm font-semibold text-gray-700">{initials}</span>
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm sm:text-base font-medium text-gray-900 truncate">{contact.name}</p>
          <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-[11px] sm:text-xs ${style.bg} ${style.text}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} aria-hidden="true" />
            {contact.status}
          </span>
        </div>
        <p className="text-xs text-gray-500 mt-0.5">Last activity · {contact.lastActivity ?? '—'}</p>
        {contact.tags && contact.tags.length > 0 && (
          <div className="mt-1 -mx-1 px-1 overflow-x-auto scrollbar-hide flex items-center gap-1">
            {contact.tags.map((t, i) => (
              <span key={i} className="shrink-0 inline-flex px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 text-[11px]">{t}</span>
            ))}
          </div>
        )}
      </div>

      {!selectionMode && (
        <div className="ml-auto flex items-center gap-1">
          <button className="hidden sm:inline-flex items-center gap-1.5 px-2 py-1 rounded-md border border-gray-300 text-gray-700 text-xs hover:bg-gray-50" onClick={(e) => { e.stopPropagation(); onLongPressSelect?.(); }}>Select</button>
          <button aria-label="More" className="p-2 rounded-md hover:bg-gray-100" onClick={(e) => { e.stopPropagation(); onAddTag?.(); }} title="Add tag">
            <MoreVertical className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      )}
    </div>
  );
}

function getInitials(name: string) {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

function inSegment(c: ContactItem, s: Segment): boolean {
  const tags = (c.tags || []).map(t => t.toLowerCase());
  const now = Date.now();
  const last = c.lastActivityIso ? new Date(c.lastActivityIso).getTime() : undefined;
  switch (s) {
    case 'Investors':
      return tags.includes('investor') || tags.includes('investment');
    case 'Waterfront':
      return tags.includes('waterfront') || tags.includes('sea view') || tags.includes('sea-view');
    case 'High Intent':
      return c.status === 'Active' || c.status === 'Warm' || (last !== undefined && (now - last) <= 24*60*60*1000);
    case 'Dormant 14d':
      return last !== undefined && (now - last) >= 14*24*60*60*1000;
    default:
      return false;
  }
}

