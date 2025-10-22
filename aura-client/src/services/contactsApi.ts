import type { Contact, ContactDetail } from '../types/contacts';
import { api } from './http';

const REQUIRE_REAL_API =
  'Contacts API requires VITE_USE_REAL_API=true and a reachable backend.';

function ensureRealApi(): void {
  if (!api.enabled) {
    throw new Error(REQUIRE_REAL_API);
  }
}

const inMemoryTags = new Map<string, string[]>();

export async function getContacts(signal?: AbortSignal): Promise<Contact[]> {
  ensureRealApi();
  const { data: rows } = await api.get<Array<Contact & { status?: string }>>(
    '/contacts',
    { signal },
  );
  return rows.map((row) => ({
    ...row,
    tags: inMemoryTags.get(row.id) || [],
  }));
}

export async function getContactDetail(
  id: string,
  signal?: AbortSignal,
): Promise<ContactDetail> {
  ensureRealApi();
  const { data: detail } = await api.get<any>(`/contacts/${id}`, { signal });
  const timeline = await getTimeline(id, signal);
  const base: Contact = {
    id: detail.id ?? id,
    name: detail.name,
    temperature: detail.temperature as Contact['temperature'],
    email: detail.email,
    phone: detail.phone,
    lastActivityAt: detail.lastActivityAt,
    tags: inMemoryTags.get(id) || [],
  };
  return {
    ...base,
    notes: detail.notes ?? '',
    intentScore: detail.intentScore ?? undefined,
    signals: detail.signals ?? undefined,
    timeline,
  };
}

export async function getTimeline(
  id: string,
  signal?: AbortSignal,
): Promise<ContactDetail['timeline']> {
  ensureRealApi();
  const { data: items } = await api.get<
    Array<{ id: string; type: string; at: string; text: string }>
  >(`/contacts/${id}/activity`, { signal });
  return items.map((item) => ({
    id: item.id,
    ts: item.at,
    type: item.type as ContactDetail['timeline'][number]['type'],
    text: item.text,
  }));
}

export async function getTags(
  contactId: string,
  _signal?: AbortSignal,
): Promise<string[]> {
  return inMemoryTags.get(contactId) || [];
}

export async function getTagsBulk(
  ids: string[],
  _signal?: AbortSignal,
): Promise<Record<string, string[]>> {
  const result: Record<string, string[]> = {};
  ids.forEach((id) => {
    const tags = inMemoryTags.get(id);
    if (tags && tags.length) {
      result[id] = [...tags];
    }
  });
  return result;
}

export async function addTag(
  contactId: string,
  tag: string,
  _signal?: AbortSignal,
): Promise<string[]> {
  const trimmed = tag.trim();
  if (!trimmed) {
    return inMemoryTags.get(contactId) || [];
  }
  const current = new Set(inMemoryTags.get(contactId) || []);
  current.add(trimmed);
  const next = Array.from(current);
  inMemoryTags.set(contactId, next);
  return next;
}

export async function removeTag(
  contactId: string,
  tag: string,
  _signal?: AbortSignal,
): Promise<string[]> {
  const current = new Set(inMemoryTags.get(contactId) || []);
  current.delete(tag.trim());
  const next = Array.from(current);
  inMemoryTags.set(contactId, next);
  return next;
}

export async function saveNotes(
  contactId: string,
  notes: string,
  signal?: AbortSignal,
) {
  ensureRealApi();
  const { data } = await api.patch<{ id: string; notes: string; updatedAt: string }>(
    `/contacts/${contactId}/notes`,
    { notes },
    { signal },
  );
  return data;
}
