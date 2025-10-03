#!/usr/bin/env node

const API_BASE = process.env.SEED_API_URL || process.env.VITE_API_URL || 'http://localhost:8000';
const AUTH_TOKEN = process.env.SEED_AUTH_TOKEN || process.env.API_BEARER_TOKEN || null;
const SAMPLE_TITLE = 'Dubai Marina Launch Suite';

const payload = {
  title: SAMPLE_TITLE,
  description:
    'Stylish two-bedroom residence with full marina skyline views, curated interiors, and smart home upgrades.',
  price: 3450000,
  location: 'Dubai Marina',
  property_type: 'apartment',
  bedrooms: 2,
  bathrooms: 2,
  area_sqft: 1280,
};

async function safeJson(response) {
  try {
    return await response.json();
  } catch (error) {
    return null;
  }
}

async function main() {
  if (typeof fetch !== 'function') {
    const { default: fetchPolyfill } = await import('node-fetch');
    globalThis.fetch = fetchPolyfill;
  }

  const headers = { 'Content-Type': 'application/json' };
  if (AUTH_TOKEN) {
    headers.Authorization = `Bearer ${AUTH_TOKEN}`;
  }

  try {
    const listResponse = await fetch(`${API_BASE.replace(/\/$/, '')}/api/v1/properties`, {
      headers,
    });

    if (!listResponse.ok) {
      console.warn(`Seed: property list request failed (${listResponse.status}).`);
      return;
    }

    const existing = await safeJson(listResponse);
    if (Array.isArray(existing)) {
      const alreadyPresent = existing.some((property) => {
        const title = (property?.title || '').toLowerCase();
        const location = (property?.location || '').toLowerCase();
        return title.includes(SAMPLE_TITLE.toLowerCase()) && location.includes('dubai');
      });
      if (alreadyPresent) {
        console.log('Seed: sample property already present.');
        return;
      }
    }

    const createResponse = await fetch(`${API_BASE.replace(/\/$/, '')}/api/v1/properties`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });

    if (!createResponse.ok) {
      console.warn(`Seed: property creation failed (${createResponse.status}).`);
      return;
    }

    console.log('Seed: sample property created.');
  } catch (error) {
    console.warn(`Seed: property seeding skipped (${(error && error.message) || error}).`);
  }
}

main();