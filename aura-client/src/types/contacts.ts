export type LeadTemperature = 'New' | 'Active' | 'Warm' | 'Cold' | 'Dormant';

export interface Contact {
  id: string;
  initials?: string;
  name: string;
  phone?: string;
  email?: string;
  tags?: string[];
  lastActivityAt?: string; // ISO
  temperature: LeadTemperature;
  avatarUrl?: string;
}

export interface ContactDetail extends Contact {
  notes: string; // agent notes (markdown/plain)
  preferences?: string[]; // e.g. 'sea-view','3BR','Palm Jumeirah'
  budget?: { min?: number; max?: number; currency?: string };
  intentScore?: number; // 0..100
  timeline: Array<{
    id: string;
    ts: string; // ISO
    type: 'call' | 'email' | 'whatsapp' | 'meeting' | 'site-visit' | 'doc' | 'ai';
    text: string;
    meta?: Record<string, any>;
  }>;
}

