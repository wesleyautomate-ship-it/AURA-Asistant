// Package orchestration utilities for Agent Beta-4 (B4-B)
// Coordinates Beta-1 (properties/analytics), Beta-2 (CRM/transactions), Beta-3 (marketing/social), and B4-A (strategy)

import type { Property } from '../store/propertyStore';
import type { Client } from '../store/clientStore';
import { computeComps, summarizeComps } from './analyticsUtils';
import { generateListingStrategy, analyzeTargetAudience } from '@propertypro/features';

export type PackageId = 'new_listing' | 'lead_nurture' | 'custom';

export interface PackageStep {
  id: string;
  title: string;
  description: string;
  requires?: ('beta1' | 'beta2' | 'beta3' | 'b4a' | 'alpha2')[];
}

export interface PackageDefinition {
  id: PackageId;
  name: string;
  summary: string;
  color: string; // for UI badges
  steps: PackageStep[];
}

export const PACKAGE_TEMPLATES: PackageDefinition[] = [
  {
    id: 'new_listing',
    name: 'New Listing Package',
    summary: 'CMA + Strategy + Marketing automation',
    color: '#0891b2',
    steps: [
      { id: 'cma', title: 'CMA Analysis', description: 'Generate comps and pricing metrics', requires: ['beta1'] },
      { id: 'strategy', title: 'Listing Strategy', description: 'Create positioning and pricing options', requires: ['b4a'] },
      { id: 'campaign', title: 'Marketing Campaign', description: 'Generate campaign content and assets', requires: ['beta3'] },
      { id: 'social_schedule', title: 'Social Scheduling', description: 'Schedule social posts across platforms', requires: ['beta3'] },
    ],
  },
  {
    id: 'lead_nurture',
    name: 'Lead Nurturing Package',
    summary: 'CRM + Email + Social campaigns',
    color: '#7c3aed',
    steps: [
      { id: 'score', title: 'Lead Scoring', description: 'Analyze lead score and intent', requires: ['beta2'] },
      { id: 'email_seq', title: 'Email Sequence', description: 'Personalized email series', requires: ['beta3'] },
      { id: 'social_target', title: 'Social Targeting', description: 'Audience targeting on social', requires: ['beta3'] },
      { id: 'followups', title: 'Follow-up Scheduling', description: 'Tasks and reminders', requires: ['beta2'] },
    ],
  },
];

export interface CMASummary {
  count: number;
  averagePrice: number;
  medianPrice: number;
  averagePricePerSqft: number;
  medianPricePerSqft: number;
}

export interface NewListingOutputs {
  cma: CMASummary;
  strategy: ReturnType<typeof generateListingStrategy>;
  segments: ReturnType<typeof analyzeTargetAudience>;
}

export function runNewListingAnalysis(subject: Property, candidates: Property[], clients: Client[]): NewListingOutputs {
  const comps = computeComps(subject, candidates);
  const cma = summarizeComps(comps);
  const strategy = generateListingStrategy(subject);
  const segments = analyzeTargetAudience(subject, clients);
  return { cma, strategy, segments };
}

export interface LeadNurtureOutputs {
  segment: string;
  nextActions: string[];
}

export function runLeadNurtureAnalysis(lead: Client): LeadNurtureOutputs {
  const score = lead.leadScore ?? 0;
  let segment = 'Nurture';
  if (score >= 80) segment = 'Hot';
  else if (score >= 60) segment = 'Warm';
  const nextActions = segment === 'Hot'
    ? ['Send personalized offer', 'Schedule call in 24h', 'Prepare social custom audience']
    : segment === 'Warm'
      ? ['Start 3-email sequence', 'Retarget on social', 'Schedule follow-up in 3 days']
      : ['Add to monthly newsletter', 'Monitor engagement', 'Quarterly check-in'];
  return { segment, nextActions };
}

