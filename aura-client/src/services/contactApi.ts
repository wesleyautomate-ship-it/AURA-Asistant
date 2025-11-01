import api from './http'
import type { ContactDetail } from '../types/contacts'

const REQUIRE_REAL_API = 'Contacts API requires VITE_USE_REAL_API=true and a reachable backend.'

const ensureRealApi = () => {
  if (!(api as any).enabled) {
    throw new Error(REQUIRE_REAL_API)
  }
}

export interface FollowUpPayload {
  when: string
  channel: 'call' | 'email' | 'meeting' | 'whatsapp'
  note?: string
}

export interface SchedulePayload {
  when: string
  title: string
  durationMin?: number
}

export type NextBestAction = {
  label: string
  actionKey: string
  payload?: unknown
}

export async function getContact(contactId: string, signal?: AbortSignal): Promise<ContactDetail> {
  ensureRealApi()
  const { data } = await api.get<ContactDetail>(`/contacts/${contactId}`, { signal })
  return data
}

export async function patchNotes(contactId: string, text: string, signal?: AbortSignal): Promise<{ savedAt: string }> {
  ensureRealApi()
  const { data } = await api.patch<{ savedAt: string }>(`/contacts/${contactId}/notes`, { text }, { signal })
  return data
}

export async function createFollowUp(contactId: string, payload: FollowUpPayload, signal?: AbortSignal): Promise<void> {
  ensureRealApi()
  await api.post(`/contacts/${contactId}/followups`, payload, { signal })
}

export async function scheduleEvent(contactId: string, payload: SchedulePayload, signal?: AbortSignal): Promise<void> {
  ensureRealApi()
  await api.post(`/contacts/${contactId}/schedule`, payload, { signal })
}

export async function summarizeNotes(contactId: string, signal?: AbortSignal): Promise<{ summary: string }> {
  ensureRealApi()
  const { data } = await api.post<{ summary: string }>(`/contacts/${contactId}/summarize-notes`, undefined, { signal })
  return data
}

export async function fetchNextBestAction(contactId: string, signal?: AbortSignal): Promise<NextBestAction> {
  ensureRealApi()
  const { data } = await api.get<NextBestAction>(`/contacts/${contactId}/next-best-action`, { signal })
  return data
}

export async function aiDraftNotes(
  contactId: string,
  payload: { prompt?: string; context?: string },
  signal?: AbortSignal,
): Promise<{ draft: string }> {
  ensureRealApi()
  const { data } = await api.post<{ draft: string }>(`/contacts/${contactId}/notes/ai-draft`, payload, { signal })
  return data
}
