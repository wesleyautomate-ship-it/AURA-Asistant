import { BrochureDraft, BrochureTemplateKey } from '../types/brochure';

type Listener = () => void;

const STORAGE_KEY = 'aura.brochureDrafts.v1';

let drafts: Record<string, BrochureDraft> = {};
const listeners = new Set<Listener>();

function notify() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
  } catch {}
  listeners.forEach((l) => {
    try { l(); } catch {}
  });
}

function load() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    drafts = saved ? JSON.parse(saved) : {};
  } catch {
    drafts = {};
  }
}

load();

function makeId() {
  try {
    // browser crypto
    return crypto.randomUUID();
  } catch {
    // fallback
    return 'draft_' + Math.random().toString(36).slice(2, 10);
  }
}

export function subscribe(listener: Listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export async function createDraft(template: BrochureTemplateKey): Promise<BrochureDraft> {
  const now = new Date().toISOString();
  const id = makeId();
  const draft: BrochureDraft = {
    id,
    template,
    createdAt: now,
    updatedAt: now,
    status: 'draft',
  };
  drafts[id] = draft;
  notify();
  return draft;
}

export async function getDraft(id: string): Promise<BrochureDraft> {
  const d = drafts[id];
  if (!d) throw new Error('Draft not found');
  return d;
}

export async function updateDraft(id: string, patch: Partial<BrochureDraft>): Promise<BrochureDraft> {
  const existing = drafts[id];
  if (!existing) throw new Error('Draft not found');
  const updated: BrochureDraft = {
    ...existing,
    ...patch,
    updatedAt: new Date().toISOString(),
  };
  drafts[id] = updated;
  notify();
  return updated;
}

export async function listDrafts(): Promise<BrochureDraft[]> {
  const arr = Object.values(drafts);
  return arr.sort((a, b) => (b.updatedAt || '').localeCompare(a.updatedAt || ''));
}

