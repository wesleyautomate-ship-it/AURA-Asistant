/**
 * Brochure Generation Progress Steps
 * ==================================
 * 
 * Defines progress stages for property brochure generation
 * Matches backend BrochureProgressStage enum
 */

import { ProgressStep } from '../components/ui/ProgressTracker';

export const BROCHURE_PROGRESS_STEPS: ProgressStep[] = [
  {
    id: 'init',
    label: 'Initialize',
    description: 'Preparing brochure generation...',
    percentage: 5,
  },
  {
    id: 'property_lookup',
    label: 'Property Lookup',
    description: 'Finding property details...',
    percentage: 15,
  },
  {
    id: 'building_prompt',
    label: 'Building Context',
    description: 'Gathering property information...',
    percentage: 25,
  },
  {
    id: 'generating',
    label: 'AI Generation',
    description: 'Creating brochure content...',
    percentage: 60,
  },
  {
    id: 'formatting',
    label: 'Formatting',
    description: 'Structuring final output...',
    percentage: 90,
  },
  {
    id: 'completed',
    label: 'Complete',
    description: 'Brochure ready!',
    percentage: 100,
  },
];

/**
 * Progress stage to percentage mapping
 */
export const BROCHURE_STAGE_PROGRESS: Record<string, number> = {
  'init': 5,
  'property_lookup': 15,
  'building_prompt': 25,
  'generating': 60,
  'formatting': 90,
  'completed': 100,
  'error': 100,
};

/**
 * Get progress percentage from stage
 */
export function getBrochureProgressFromStage(stage: string): number {
  return BROCHURE_STAGE_PROGRESS[stage] || 0;
}

/**
 * Check if this is a brochure generation task
 */
export function isBrochureGenerationTask(contentType?: string): boolean {
  return contentType === 'PROPERTY_BROCHURE';
}

/**
 * Property disambiguation interface for multiple matches
 */
export interface PropertyMatch {
  id: string;
  title: string;
  address?: string;
  price?: string;
  property_type?: string;
}

/**
 * Disambiguation event data structure
 */
export interface DisambiguationData {
  matches: PropertyMatch[];
  query: string;
  message: string;
}