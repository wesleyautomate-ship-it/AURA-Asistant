import { describe, it, expect } from 'vitest';
import { listTemplates, listDrafts } from '../features/brochure/api/brochure';

// These are smoke tests to validate function availability and basic shapes.
// In CI, replace skips with real integration when backend is running.

describe('Brochure API service', () => {
  it.skip('lists templates (mock mode ok)', async () => {
    const items = await listTemplates();
    expect(Array.isArray(items)).toBe(true);
  });

  it.skip('lists drafts (empty in mock mode)', async () => {
    const items = await listDrafts();
    expect(Array.isArray(items)).toBe(true);
  });
});

