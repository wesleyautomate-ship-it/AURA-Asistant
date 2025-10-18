import type { Contact, ContactDetail } from '../types/contacts';
import { api } from './http';

// Simulated network latency
const delay = (ms: number, signal?: AbortSignal) => new Promise<void>((resolve, reject) => {
  const t = setTimeout(() => resolve(), ms);
  const onAbort = () => {
    clearTimeout(t);
    reject(new DOMException('Aborted', 'AbortError'));
  };
  if (signal) {
    if (signal.aborted) {
      clearTimeout(t);
      reject(new DOMException('Aborted', 'AbortError'));
    } else {
      signal.addEventListener('abort', onAbort, { once: true });
    }
  }
});

export async function getContacts(signal?: AbortSignal): Promise<Contact[]> {
  if (api.enabled) {
    const list = await api.get<Array<Contact & { status?: string }>>('/contacts', signal);
    const tagMap = readTagsStore();
    return list.map(c => ({ ...c, temperature: (c.temperature || (c as any).status || 'Warm') as Contact['temperature'], tags: tagMap[c.id] }));
  }
  await delay(300, signal);
  const now = new Date();
  const list: Contact[] = [
    { id: '1', name: 'Alex Johnson', temperature: 'Active', lastActivityAt: new Date(now.getTime() - 2*60*60*1000).toISOString() },
    { id: '2', name: 'Briana Chen', temperature: 'New', lastActivityAt: now.toISOString() },
    { id: '3', name: 'Carlos Ramirez', temperature: 'Warm', lastActivityAt: new Date(now.getTime() - 24*60*60*1000).toISOString() },
    { id: '4', name: 'Danielle Brooks', temperature: 'Active', lastActivityAt: new Date(now.getTime() - 3*60*60*1000).toISOString() },
    { id: '5', name: 'Ethan Patel', temperature: 'Cold', lastActivityAt: new Date(now.getTime() - 5*24*60*60*1000).toISOString() },
  ];
  const tagMap = readTagsStore();
  return list.map(c => ({ ...c, tags: tagMap[c.id] }));
}

export async function getContactDetail(id: string, signal?: AbortSignal): Promise<ContactDetail> {
  if (api.enabled) {
    const d = await api.get<any>(`/contacts/${id}`, signal);
    const activity = await getTimeline(id, signal);
    const base: Contact = {
      id: d.id || id,
      name: d.name || mockNameFor(id),
      temperature: (d.temperature || 'Warm') as Contact['temperature'],
      email: d.email,
      phone: d.phone,
      lastActivityAt: d.lastActivityAt,
    };
    return {
      ...base,
      tags: readTagsStore()[id] || [],
      notes: d.notes || '',
      intentScore: d.intentScore ?? 62,
      timeline: activity,
    };
  }
  await delay(350, signal);
  const base: Contact = {
    id,
    name: mockNameFor(id),
    temperature: (['New','Active','Warm','Cold'][parseInt(id,10)%4] || 'Warm') as Contact['temperature'],
    email: `contact${id}@example.com`,
    phone: '+971 50 123 4567',
    lastActivityAt: new Date(Date.now() - 90 * 60 * 1000).toISOString(),
  };
  const detail: ContactDetail = {
    ...base,
    tags: readTagsStore()[id] || [],
    notes: 'Initial notes...\n- Preferences: Sea view, 2-3BR\n- Budget: ~6M AED',
    intentScore: 62,
    timeline: await getTimeline(id, signal),
  };
  return detail;
}

export async function getNotes(id: string, signal?: AbortSignal): Promise<string> {
  await delay(200, signal);
  return 'Initial notes...\n- Preferences: Sea view, 2-3BR\n- Budget: ~6M AED';
}

export async function saveNotes(id: string, notes: string, signal?: AbortSignal): Promise<{ ok: true }>{
  await delay(250, signal);
  // Stub save success
  return { ok: true };
}

export async function getTimeline(id: string, signal?: AbortSignal): Promise<ContactDetail['timeline']> {
  if (api.enabled) {
    const items = await api.get<Array<{id:string; type:string; at:string; text:string}>>(`/contacts/${id}/activity`, signal);
    return items.map(it => ({ id: it.id, ts: it.at, type: (it.type as any), text: it.text }));
  }
  await delay(280, signal);
  const now = Date.now();
  return [
    { id: `${id}-t1`, ts: new Date(now - 30 * 60 * 1000).toISOString(), type: 'call', text: 'Spoke about Marina waterfront options' },
    { id: `${id}-t2`, ts: new Date(now - 2 * 60 * 60 * 1000).toISOString(), type: 'email', text: 'Sent brochure PDF and comparables' },
    { id: `${id}-t3`, ts: new Date(now - 26 * 60 * 60 * 1000).toISOString(), type: 'ai', text: 'AI summarized last meeting notes' },
    { id: `${id}-t4`, ts: new Date(now - 3 * 24 * 60 * 60 * 1000).toISOString(), type: 'site-visit', text: 'Booked site visit for Palm Jumeirah' },
  ];
}

function mockNameFor(id: string) {
  const names = ['Alex Johnson','Briana Chen','Carlos Ramirez','Danielle Brooks','Ethan Patel','Fatima Khan','Grace Lee','Henry Nguyen'];
  const n = parseInt(id, 10);
  return Number.isFinite(n) ? names[n % names.length] : `Contact ${id}`;
}

// Tags persistence (mock via localStorage)
const TAGS_KEY = 'mock_contact_tags_v1';
function readTagsStore(): Record<string, string[]> {
  try {
    const raw = localStorage.getItem(TAGS_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object') return parsed;
  } catch {}
  return {};
}
function writeTagsStore(map: Record<string, string[]>) {
  try { localStorage.setItem(TAGS_KEY, JSON.stringify(map)); } catch {}
}

export async function getTags(contactId: string, signal?: AbortSignal): Promise<string[]> {
  await delay(80, signal);
  return readTagsStore()[contactId] || [];
}

export async function getTagsBulk(ids: string[], signal?: AbortSignal): Promise<Record<string, string[]>> {
  await delay(80, signal);
  const store = readTagsStore();
  const out: Record<string, string[]> = {};
  ids.forEach(id => { if (store[id]) out[id] = store[id]; });
  return out;
}

export async function addTag(contactId: string, tag: string, signal?: AbortSignal): Promise<string[]> {
  await delay(100, signal);
  const map = readTagsStore();
  const cur = new Set(map[contactId] || []);
  cur.add(tag.trim());
  map[contactId] = Array.from(cur);
  writeTagsStore(map);
  return map[contactId];
}

export async function removeTag(contactId: string, tag: string, signal?: AbortSignal): Promise<string[]> {
  await delay(100, signal);
  const map = readTagsStore();
  const cur = new Set(map[contactId] || []);
  cur.delete(tag.trim());
  map[contactId] = Array.from(cur);
  writeTagsStore(map);
  return map[contactId];
}
