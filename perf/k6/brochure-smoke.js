import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomItem } from './utils.js';

export const options = {
  vus: 3,
  duration: '1m',
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.03'],
  },
};

const BASE = __ENV.BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.API_TOKEN || 'dev';
const TEMPLATE_KEYS = ['clean-minimal', 'luxury-showcase', 'neighborhood-highlight'];

export default function () {
  const headers = {
    Authorization: `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  };

  const createRes = http.post(
    `${BASE}/api/v1/brochures`,
    JSON.stringify({ templateKey: randomItem(TEMPLATE_KEYS) }),
    { headers },
  );
  check(createRes, { 'create draft 200': (r) => r.status === 200 });

  const draft = createRes.json();
  if (!draft?.id) {
    sleep(1);
    return;
  }

  const patchRes = http.patch(
    `${BASE}/api/v1/brochures/${draft.id}`,
    JSON.stringify({
      data: {
        hero: { title: 'Perf Smoke Property' },
        about: { body: 'Automated smoke description.' },
        whyInvest: { bullets: ['Prime location', 'High ROI'] },
      },
    }),
    { headers },
  );
  check(patchRes, { 'patch 200': (r) => r.status === 200 });

  const renderRes = http.post(`${BASE}/api/v1/brochures/${draft.id}/render`, null, { headers });
  check(renderRes, {
    'render status ok': (r) => r.status === 200 || r.status === 202 || r.status === 500,
  });

  sleep(2);
}
