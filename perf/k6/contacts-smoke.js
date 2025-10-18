import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '1m',
  thresholds: {
    http_req_duration: ['p(95)<300'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE = __ENV.BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.API_TOKEN || 'dev';

export default function () {
  const headers = { Authorization: `Bearer ${TOKEN}` };

  const list = http.get(`${BASE}/contacts?limit=20&offset=0`, { headers });
  check(list, {
    'list status 200': (r) => r.status === 200,
    'list returns array': (r) => Array.isArray(r.json()),
  });

  const items = list.json();
  if (items.length > 0) {
    const id = items[0].id;
    const detail = http.get(`${BASE}/contacts/${id}`, { headers });
    check(detail, {
      'detail status 200': (r) => r.status === 200,
      'detail has name': (r) => !!r.json().name,
    });

    const activity = http.get(`${BASE}/contacts/${id}/activity`, { headers });
    check(activity, {
      'activity status 200': (r) => r.status === 200,
    });
  }

  sleep(1);
}
