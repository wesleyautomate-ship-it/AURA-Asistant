import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 2,
  duration: '1m',
  thresholds: {
    http_req_duration: ['p(95)<800'],
    http_req_failed: ['rate<0.05'],
  },
};

const BASE = __ENV.BASE_URL || 'http://localhost:8000';
const TOKEN = __ENV.API_TOKEN || 'dev';

export default function () {
  const headers = {
    Authorization: `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  };

  const payload = {
    property_id: 1,
    analysis_type: 'listing',
    include_market_trends: true,
    include_price_history: true,
    include_neighborhood_analysis: true,
    comp_radius_km: 2.0,
    comp_time_months: 6,
  };

  const create = http.post(`${BASE}/api/v1/cma/reports`, JSON.stringify(payload), { headers });
  check(create, { 'create status acceptable': (r) => r.status === 200 || r.status === 202 });

  if (create.status === 200 && create.json()?.task_id) {
    const taskId = create.json().task_id;
    const statusRes = http.get(`${BASE}/api/v1/cma/reports/${taskId}/status`, { headers });
    check(statusRes, { 'status responds': (r) => r.status === 200 || r.status === 202 || r.status === 404 });
  }

  sleep(3);
}
