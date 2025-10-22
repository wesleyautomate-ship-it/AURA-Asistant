// AI client, prefers real API when enabled, falls back to stub
import { api } from './http';

const delay = (ms: number) => new Promise<void>(res => setTimeout(res, ms));

export type FollowUpTone = 'Friendly' | 'Professional' | 'Persuasive' | 'Casual';
export type FollowUpGoal = 'Re-engage' | 'Schedule Call' | 'Share Brochure' | 'Nurture';

export async function generateFollowUp(contactId: string, opts?: { tone?: FollowUpTone; goal?: FollowUpGoal }) {
  if (api.enabled) {
    const { data } = await api.post<{ draft: string }>(`/ai/followup`, { contactId, ...opts });
    return data.draft;
  }
  await delay(350);
  const tone = opts?.tone || 'Friendly';
  const goal = opts?.goal || 'Re-engage';
  return `Hi there,\n\nJust following up on our last conversation. ${goal === 'Schedule Call' ? 'Would you be available for a quick call this week?' : goal === 'Share Brochure' ? 'I attached a brochure with tailored options you might like.' : goal === 'Nurture' ? 'I thought you might enjoy some fresh listings that match your preferences.' : 'Let me know if you had any questions I can help with.'}\n\nBest regards,\nYour Agent\n\nTone: ${tone}`;
}

export async function summarizeNotes(contactId: string) {
  if (api.enabled) {
    const { data } = await api.post<{ summary: string }>(`/ai/summarize`, { contactId });
    return data.summary;
  }
  await delay(280);
  return 'Summary: Interested in waterfront, 2–3BR around 6M AED; prefers Marina/Palm, responsive to brochures; follow up this week.';
}

export interface Recommendation {
  id: string;
  title: string;
  area: string;
  price: string;
  route: '/ai-workflow/brochure' | '/ai-workflow/cma' | '/ai-workflow/social';
}

export async function recommendProperties(contactId: string): Promise<Recommendation[]> {
  if (api.enabled) {
    const { data } = await api.get<{ items: Recommendation[] }>(
      `/ai/recommend?contactId=${encodeURIComponent(contactId)}`
    );
    return data.items;
  }
  await delay(320);
  return [
    { id: 'rec-1', title: 'Marina 2BR with Sea View', area: 'Dubai Marina', price: 'AED 6.2M', route: '/ai-workflow/brochure' },
    { id: 'rec-2', title: 'Palm Jumeirah 3BR', area: 'Palm Jumeirah', price: 'AED 6.8M', route: '/ai-workflow/cma' },
  ];
}

export async function nextBestAction(contactId: string): Promise<{ title: string; detail: string }> {
  if (api.enabled) {
    const { data } = await api.get<{ title: string; detail: string }>(
      `/ai/next-best-action?contactId=${encodeURIComponent(contactId)}`
    );
    return data;
  }
  await delay(260);
  return { title: 'Schedule a follow-up call', detail: 'They opened your brochure twice yesterday. Propose a 10–15 min call.' };
}
