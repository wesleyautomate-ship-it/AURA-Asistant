// Basic contract test that imports a few types from generated api.d.ts
// and checks assignability against sample payloads.

// These are type-level checks; at runtime this file can be empty exports.
import type { paths } from '../../types/api.d.ts';

// Contact list sample should match the inferred response type
type ContactsListResp = paths['/contacts']['get']['responses']['200']['content']['application/json'];
const sampleContacts: ContactsListResp = [
  { id: '1', name: 'Alex Johnson', temperature: 'Active', lastActivityAt: '2025-01-01T10:00:00Z' },
];

// Contact detail sample
type ContactDetailResp = paths['/contacts/{contact_id}']['get']['responses']['200']['content']['application/json'];
const sampleDetail: ContactDetailResp = {
  id: '1',
  name: 'Alex Johnson',
  temperature: 'Active',
  email: 'alex.j@example.com',
  phone: '+971 50 123 4567',
  lastActivityAt: '2025-01-01T10:00:00Z',
  notes: '...',
  intentScore: 62,
  signals: ['Opened brochure'],
};

// Activity list sample
type ActivityListResp = paths['/contacts/{contact_id}/activity']['get']['responses']['200']['content']['application/json'];
const sampleActs: ActivityListResp = [
  { id: '1-t1', type: 'call', at: '2025-01-01T09:30:00Z', text: 'Discussed waterfront options' },
];

export {};

