import { api } from './http';
export type FollowUpChannel = 'call' | 'email' | 'whatsapp' | 'meeting';

export interface FollowUpItem {
  id: string;
  contactId: string;
  channel: FollowUpChannel;
  dueAt: string; // ISO
  notes?: string;
  createdAt: string; // ISO
}

const STORAGE_KEY = 'mock_followups_v1';

function readStore(): FollowUpItem[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed as FollowUpItem[];
  } catch {}
  return [];
}

function writeStore(items: FollowUpItem[]) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(items)); } catch {}
}

const delay = (ms: number, signal?: AbortSignal) => new Promise<void>((resolve, reject) => {
  const t = setTimeout(() => resolve(), ms);
  const onAbort = () => { clearTimeout(t); reject(new DOMException('Aborted', 'AbortError')); };
  if (signal) {
    if (signal.aborted) { clearTimeout(t); reject(new DOMException('Aborted', 'AbortError')); }
    else signal.addEventListener('abort', onAbort, { once: true });
  }
});

export async function listFollowUps(contactId: string, signal?: AbortSignal): Promise<FollowUpItem[]> {
  if (api.enabled) {
    return api.get<FollowUpItem[]>(`/followups?contactId=${encodeURIComponent(contactId)}`, signal);
  }
  await delay(180, signal);
  return readStore().filter(i => i.contactId === contactId).sort((a,b) => new Date(a.dueAt).getTime() - new Date(b.dueAt).getTime());
}

export async function createFollowUp(input: { contactId: string; channel: FollowUpChannel; dueAt: string; notes?: string }, signal?: AbortSignal): Promise<FollowUpItem> {
  if (api.enabled) {
    const item: FollowUpItem = {
      id: `${input.contactId}-${Date.now()}`,
      contactId: input.contactId,
      channel: input.channel,
      dueAt: input.dueAt,
      notes: input.notes,
      createdAt: new Date().toISOString(),
    };
    return api.post<FollowUpItem>(`/followups`, item);
  }
  await delay(220, signal);
  const item: FollowUpItem = {
    id: `${input.contactId}-${Date.now()}`,
    contactId: input.contactId,
    channel: input.channel,
    dueAt: input.dueAt,
    notes: input.notes,
    createdAt: new Date().toISOString(),
  };
  const all = readStore();
  all.push(item);
  writeStore(all);
  return item;
}

export async function nextFollowUp(contactId: string, signal?: AbortSignal): Promise<FollowUpItem | null> {
  await delay(100, signal);
  const now = Date.now();
  const items = readStore().filter(i => i.contactId === contactId && new Date(i.dueAt).getTime() >= now)
    .sort((a,b) => new Date(a.dueAt).getTime() - new Date(b.dueAt).getTime());
  return items[0] ?? null;
}
