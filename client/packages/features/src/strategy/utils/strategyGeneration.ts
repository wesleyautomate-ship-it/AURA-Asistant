// Strategy utilities for Agent Beta-4
// Teal theme primary: #0891b2

import type { Property } from '@propertypro/store';
import { usePropertyStore } from '@propertypro/store';
import type { Client } from '@propertypro/store';
import { useClientStore } from '@propertypro/store';

export interface USP {
  key: string;
  value: string;
}

export interface ListingStrategyDoc {
  title: string;
  summary: string;
  usps: USP[];
  pricing: {
    suggestedListPrice: number | null;
    pricingRationale: string;
    alternatives: { label: string; price: number | null; notes: string }[];
  };
  channels: string[];
}

export interface AudienceSegment {
  name: string;
  demographics: string[];
  interests: string[];
  score: number; // 0-100
}

export interface TimelineItem {
  id: string;
  week: number;
  title: string;
  description: string;
}

export interface NegotiationPlay {
  name: string;
  trigger: string;
  counter: string;
  risk: 'low' | 'medium' | 'high';
}

export function extractUSPs(property: Partial<Property>): USP[] {
  const usps: USP[] = [];
  if (property.beds) usps.push({ key: 'Bedrooms', value: String(property.beds) });
  if (property.baths) usps.push({ key: 'Bathrooms', value: String(property.baths) });
  if (property.sqft) usps.push({ key: 'SqFt', value: `${property.sqft.toLocaleString()} sq ft` });
  if (property.city || property.address)
    usps.push({ key: 'Location', value: `${property.address ?? ''} ${property.city ?? ''}`.trim() });
  if (property.status) usps.push({ key: 'Status', value: property.status });
  // Placeholder for Beta-1 analytics-derived USPs
  if (typeof property.price === 'number')
    usps.push({ key: 'Price Band', value: `$${property.price.toLocaleString()}` });
  return usps;
}

export function generateListingStrategy(property: Partial<Property>): ListingStrategyDoc {
  const usps = extractUSPs(property);
  const suggested = typeof property.price === 'number' ? property.price : null;
  return {
    title: `Listing Strategy${property.address ? ` - ${property.address}` : ''}`,
    summary:
      'Comprehensive strategy covering positioning, pricing, target audience, and channel mix. Auto-generated using property analytics (Beta-1) and CRM insights (Beta-2).',
    usps,
    pricing: {
      suggestedListPrice: suggested,
      pricingRationale:
        'Suggested price is aligned with current comps and condition. Consider micro-market demand and seasonality.',
      alternatives: [
        { label: 'Aggressive', price: suggested ? Math.round(suggested * 1.03) : null, notes: 'Maximize upside in seller’s market' },
        { label: 'Market', price: suggested, notes: 'Balance demand and time-on-market' },
        { label: 'Velocity', price: suggested ? Math.round(suggested * 0.97) : null, notes: 'Drive multiple offers quickly' },
      ],
    },
    channels: ['Portal listing', 'Email to buyers list', 'Instagram + Reels', 'Agent network', 'Open house'],
  };
}

export function analyzeTargetAudience(property: Partial<Property>, clients: Client[]): AudienceSegment[] {
  // Simple heuristic demo. In production, use clustering against client interest history.
  const base: AudienceSegment[] = [
    {
      name: 'Young Professionals',
      demographics: ['25-35', 'Dual income'],
      interests: ['Urban living', 'Proximity to work'],
      score: 78,
    },
    {
      name: 'Investors',
      demographics: ['Global', 'Cash buyers'],
      interests: ['Yield', 'Capital appreciation'],
      score: 72,
    },
  ];

  const highScorers = clients.filter((c) => (c.leadScore ?? 0) >= 70);
  if (highScorers.length > 0) {
    base.push({
      name: 'High-score CRM Leads',
      demographics: ['From CRM (Beta-2)'],
      interests: ['Previously engaged with similar listings'],
      score: 82,
    });
  }

  if ((property.beds ?? 0) >= 3) {
    base.push({
      name: 'Families',
      demographics: ['30-45', 'School proximity'],
      interests: ['Space', 'Neighborhood amenities'],
      score: 68,
    });
  }
  return base.sort((a, b) => b.score - a.score);
}

export function buildMarketingTimeline(property: Partial<Property>): TimelineItem[] {
  return [
    { id: 'w1-1', week: 1, title: 'Prep & Assets', description: 'Staging, photography, floorplan, and copywriting' },
    { id: 'w2-1', week: 2, title: 'Launch', description: 'Portals live, email to CRM (Beta-2), initial social push (Beta-3)' },
    { id: 'w3-1', week: 3, title: 'Awareness Boost', description: 'Reels + stories, influencer collab, postcard drop (Beta-3)' },
    { id: 'w4-1', week: 4, title: 'Open House', description: 'Host OH, collect leads, follow-ups via templates (Beta-3)' },
  ];
}

export function prepareNegotiationPlan(property: Partial<Property>): NegotiationPlay[] {
  return [
    { name: 'Counter +1.5%', trigger: 'Initial low offer <97% ask', counter: 'Counter at 101.5% with value reminders', risk: 'low' },
    { name: 'Concessions Swap', trigger: 'Buyer requests repairs credit', counter: 'Offer small credit in exchange for price integrity', risk: 'medium' },
    { name: 'Deadline Strategy', trigger: 'Stalled negotiation', counter: 'Set response deadline and signal alternate interest', risk: 'low' },
  ];
}

export function useStrategySources() {
  // Hook for components to access property and client stores safely
  const propertyStore = usePropertyStore();
  const clientStore = useClientStore();
  const properties = (propertyStore as any)?.items as Property[] | undefined;
  const clients = (clientStore as any)?.clients as Client[] | undefined;
  return { properties: properties ?? [], clients: clients ?? [] };
}
