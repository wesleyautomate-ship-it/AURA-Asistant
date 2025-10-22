import { api } from './http';

export type FollowUpChannel = 'call' | 'email' | 'whatsapp' | 'meeting';

export interface FollowUpItem {
  id: string;
  contactId: string;
  channel: FollowUpChannel;
  dueAt: string;
  status: string;
  notes?: string;
  createdAt: string;
}

const REQUIRE_REAL_API =
  'Follow-ups API requires VITE_USE_REAL_API=true and a reachable backend.';

function ensureRealApi(): void {
  if (!api.enabled) {
    throw new Error(REQUIRE_REAL_API);
  }
}

export async function listFollowUps(
  contactId: string,
  signal?: AbortSignal,
): Promise<FollowUpItem[]> {
  ensureRealApi();
  const { data } = await api.get<FollowUpItem[]>(
    `/followups?contactId=${encodeURIComponent(contactId)}`,
    { signal },
  );
  return data;
}

export async function createFollowUp(
  input: { contactId: string; channel: FollowUpChannel; dueAt: string; notes?: string },
  signal?: AbortSignal,
): Promise<FollowUpItem> {
  ensureRealApi();
  const { data } = await api.post<FollowUpItem>(
    '/followups',
    {
      contactId: input.contactId,
      channel: input.channel,
      dueAt: input.dueAt,
      notes: input.notes,
    },
    { signal },
  );
  return data;
}

export async function nextFollowUp(
  contactId: string,
  signal?: AbortSignal,
): Promise<FollowUpItem | null> {
  const items = await listFollowUps(contactId, signal);
  const now = Date.now();
  const upcoming = items
    .map((item) => ({ item, ts: Date.parse(item.dueAt) }))
    .filter(({ ts }) => Number.isFinite(ts) && ts >= now)
    .sort((a, b) => a.ts - b.ts);
  return upcoming.length ? upcoming[0].item : null;
}

