/**
 * Intent Normalizer Service
 * ==========================
 * 
 * Normalizes free-form text/voice intents to canonical content types
 * Extracts entities and prepares payloads for validation
 * Provides structured diagnostic logging
 * 
 * Version: 3.2
 * Phase: Track 3.1 - Intent Normalization
 */

import { ContentType as SchemaContentType } from '../types/contentSchemas';
import { Intent, detectIntent } from './intentParser';

// Request ID for tracking
let requestCounter = 0;
export const generateRequestId = (): string => {
  return `req_${Date.now()}_${(++requestCounter).toString().padStart(4, '0')}`;
};

export interface NormalizedIntent {
  contentType: SchemaContentType;
  entities: Record<string, any>;
  confidence: number;
  rawIntent: string;
  requestId: string;
  inferredFrom: string[];
  missingFields: string[];
  canAutoFill: boolean;
}

export interface NormalizationRequest {
  userInput: string;
  requestId: string;
}

/**
 * Map legacy intent types to schema content types
 */
export const mapIntentToContentType = (intent: Intent): SchemaContentType | null => {
  console.group(`[Orchestrator] Intent Type Mapping`);
  console.log('Intent type:', intent.type);
  console.log('Intent confidence:', intent.confidence);
  
  let contentType: SchemaContentType | null = null;
  
  switch (intent.type) {
    case 'CMA':
    case 'CMA_REPORT':
      contentType = SchemaContentType.CMA_REPORT;
      break;
    
    case 'PITCH_DECK':
      contentType = SchemaContentType.PITCH_DECK;
      break;
    
    case 'MARKET_REPORT':
      contentType = SchemaContentType.MARKET_REPORT;
      break;
    
    case 'NEWSLETTER':
      contentType = SchemaContentType.NEWSLETTER;
      break;
    
    case 'SOCIAL_POST':
      contentType = SchemaContentType.SOCIAL_POST;
      break;
    
    default:
      console.warn('Unknown or unmapped intent type:', intent.type);
      contentType = null;
  }
  
  console.log('Mapped to content type:', contentType);
  console.groupEnd();
  
  return contentType;
};

/**
 * Extract entities from intent and prompt
 */
export const extractEntities = (
  intent: Intent,
  prompt: string,
  contentType: SchemaContentType
): Record<string, any> => {
  console.group('[Orchestrator] Entity Extraction');
  console.log('Content type:', contentType);
  console.log('Prompt:', prompt);
  
  const entities: Record<string, any> = {};
  const lowerPrompt = prompt.toLowerCase();
  
  // Common entity extraction
  if (intent.location) {
    entities.address = intent.location;
    entities.region = intent.location;
    console.log('✓ Extracted address/region:', intent.location);
  }
  
  if (intent.topic) {
    entities.topic = intent.topic;
    console.log('✓ Extracted topic:', intent.topic);
  }
  
  // Content type specific extraction
  switch (contentType) {
    case SchemaContentType.CMA_REPORT:
      entities.propertyType = extractPropertyType(lowerPrompt);
      entities.comparableCount = extractNumber(lowerPrompt, 'comp', 5);
      entities.dateRange = extractDateRange(lowerPrompt);
      console.log('CMA entities:', entities);
      break;
    
    case SchemaContentType.PITCH_DECK:
      entities.investmentType = extractInvestmentType(lowerPrompt);
      entities.targetAudience = extractTargetAudience(lowerPrompt);
      entities.slideCount = extractNumber(lowerPrompt, 'slide', 8);
      console.log('Pitch Deck entities:', entities);
      break;
    
    case SchemaContentType.MARKET_REPORT:
      entities.propertyType = extractPropertyType(lowerPrompt);
      entities.timePeriod = extractTimePeriod(lowerPrompt);
      entities.metricsRequired = extractMetrics(lowerPrompt);
      console.log('Market Report entities:', entities);
      break;
    
    case SchemaContentType.NEWSLETTER:
      entities.tone = extractTone(lowerPrompt);
      entities.targetAudience = extractAudience(lowerPrompt);
      console.log('Newsletter entities:', entities);
      break;
    
    case SchemaContentType.SOCIAL_POST:
      entities.platform = extractPlatform(lowerPrompt);
      entities.tone = extractSocialTone(lowerPrompt);
      entities.hashtags = extractHashtags(prompt);
      console.log('Social Post entities:', entities);
      break;
  }
  
  console.log('Final extracted entities:', entities);
  console.groupEnd();
  
  return entities;
};

/**
 * Normalize intent to structured format
 */
export const normalizeIntent = async (
  request: NormalizationRequest
): Promise<NormalizedIntent> => {
  const { userInput, requestId } = request;
  
  console.group(`[Orchestrator] ${requestId} - Intent Normalization`);
  console.log('User Input:', userInput);
  console.time('Normalization');
  
  // Parse intent from user input
  const intent = detectIntent(userInput);
  
  console.log('Parsed intent:', intent);
  
  const contentType = mapIntentToContentType(intent);
  
  if (!contentType) {
    console.warn('Cannot normalize - no content type match');
    console.timeEnd('Normalization');
    console.groupEnd();
    throw new Error('Unable to determine content type from input');
  }
  
  const entities = extractEntities(intent, userInput, contentType);
  const requiredFields = getRequiredFields(contentType);
  const missingFields = requiredFields.filter(field => !entities[field] && !canAutoFill(field, contentType));
  const allFieldsCanAutoFill = missingFields.length === 0 || missingFields.every(f => canAutoFill(f, contentType));
  
  const inferredFrom: string[] = [];
  if (intent.location) inferredFrom.push('intent.location');
  if (intent.topic) inferredFrom.push('intent.topic');
  if (Object.keys(entities).length > inferredFrom.length) {
    inferredFrom.push('prompt_analysis');
  }
  
  const normalized: NormalizedIntent = {
    contentType,
    entities,
    confidence: intent.confidence,
    rawIntent: userInput,
    requestId,
    inferredFrom,
    missingFields,
    canAutoFill: allFieldsCanAutoFill,
  };
  
  console.log('Normalized intent:', normalized);
  console.log(`Missing fields (${missingFields.length}):`, missingFields);
  console.log('Can auto-fill:', allFieldsCanAutoFill);
  console.timeEnd('Normalization');
  console.groupEnd();
  
  return normalized;
};

/**
 * Get required fields for content type
 */
const getRequiredFields = (contentType: SchemaContentType): string[] => {
  switch (contentType) {
    case SchemaContentType.CMA_REPORT:
      return ['address', 'propertyType'];
    case SchemaContentType.PITCH_DECK:
      return ['address', 'investmentType'];
    case SchemaContentType.MARKET_REPORT:
      return ['region', 'timePeriod'];
    case SchemaContentType.NEWSLETTER:
      return ['topic', 'targetAudience'];
    case SchemaContentType.SOCIAL_POST:
      return ['topic', 'platform'];
    default:
      return [];
  }
};

/**
 * Check if field can be auto-filled with defaults
 */
const canAutoFill = (field: string, contentType: SchemaContentType): boolean => {
  const autoFillableFields: Record<string, string[]> = {
    [SchemaContentType.CMA_REPORT]: ['propertyType', 'comparableCount', 'dateRange'],
    [SchemaContentType.PITCH_DECK]: ['slideCount', 'targetAudience'],
    [SchemaContentType.MARKET_REPORT]: ['propertyType', 'metricsRequired'],
    [SchemaContentType.NEWSLETTER]: ['tone'],
    [SchemaContentType.SOCIAL_POST]: ['platform', 'tone'],
  };
  
  return autoFillableFields[contentType]?.includes(field) || false;
};

// ============================================================================
// ENTITY EXTRACTION HELPERS
// ============================================================================

const extractPropertyType = (text: string): string => {
  if (text.includes('commercial')) return 'commercial';
  if (text.includes('residential')) return 'residential';
  if (text.includes('apartment') || text.includes('condo')) return 'residential';
  if (text.includes('villa') || text.includes('luxury')) return 'residential';
  if (text.includes('land') || text.includes('plot')) return 'land';
  return 'mixed';
};

const extractInvestmentType = (text: string): string => {
  if (text.includes('acquisition') || text.includes('buy')) return 'acquisition';
  if (text.includes('development') || text.includes('develop')) return 'development';
  if (text.includes('renovation') || text.includes('renovate')) return 'renovation';
  if (text.includes('flip')) return 'flip';
  return 'acquisition';
};

const extractTargetAudience = (text: string): string => {
  if (text.includes('investor')) return 'investors';
  if (text.includes('partner')) return 'partners';
  if (text.includes('buyer')) return 'buyers';
  if (text.includes('client')) return 'clients';
  return 'investors';
};

const extractTimePeriod = (text: string): string => {
  if (text.includes('quarter') || text.includes('q1') || text.includes('q2')) return 'quarterly';
  if (text.includes('month')) return 'monthly';
  if (text.includes('year') || text.includes('annual')) return 'yearly';
  return 'quarterly';
};

const extractMetrics = (text: string): string[] => {
  const metrics: string[] = [];
  if (text.includes('price')) metrics.push('price_trends');
  if (text.includes('volume') || text.includes('transaction')) metrics.push('volume');
  if (text.includes('inventory')) metrics.push('inventory');
  if (text.includes('forecast') || text.includes('prediction')) metrics.push('forecasts');
  return metrics.length > 0 ? metrics : ['price_trends', 'volume', 'inventory'];
};

const extractTone = (text: string): 'professional' | 'casual' | 'friendly' | 'authoritative' => {
  if (text.includes('professional') || text.includes('formal')) return 'professional';
  if (text.includes('casual') || text.includes('relaxed')) return 'casual';
  if (text.includes('friendly') || text.includes('warm')) return 'friendly';
  if (text.includes('authoritative') || text.includes('expert')) return 'authoritative';
  return 'professional';
};

const extractAudience = (text: string): string => {
  if (text.includes('client')) return 'clients';
  if (text.includes('prospect')) return 'prospects';
  if (text.includes('investor')) return 'investors';
  if (text.includes('buyer')) return 'buyers';
  return 'clients';
};

const extractPlatform = (text: string): 'instagram' | 'facebook' | 'linkedin' | 'twitter' | 'tiktok' => {
  if (text.includes('instagram') || text.includes('insta') || text.includes('ig')) return 'instagram';
  if (text.includes('facebook') || text.includes('fb')) return 'facebook';
  if (text.includes('linkedin')) return 'linkedin';
  if (text.includes('twitter') || text.includes('x')) return 'twitter';
  if (text.includes('tiktok') || text.includes('tik tok')) return 'tiktok';
  return 'instagram';
};

const extractSocialTone = (text: string): 'engaging' | 'professional' | 'casual' | 'inspirational' | 'urgent' => {
  if (text.includes('engaging') || text.includes('fun')) return 'engaging';
  if (text.includes('professional')) return 'professional';
  if (text.includes('casual')) return 'casual';
  if (text.includes('inspirational') || text.includes('motivational')) return 'inspirational';
  if (text.includes('urgent') || text.includes('limited')) return 'urgent';
  return 'engaging';
};

const extractHashtags = (text: string): string[] => {
  const hashtagRegex = /#[\w]+/g;
  const matches = text.match(hashtagRegex);
  return matches ? matches.map(tag => tag.slice(1)) : [];
};

const extractDateRange = (text: string): string => {
  if (text.includes('3 month') || text.includes('90 day')) return '3_months';
  if (text.includes('6 month')) return '6_months';
  if (text.includes('year') || text.includes('12 month')) return '12_months';
  return '6_months';
};

const extractNumber = (text: string, context: string, defaultValue: number): number => {
  const regex = new RegExp(`(\\d+)\\s*${context}`, 'i');
  const match = text.match(regex);
  return match ? parseInt(match[1], 10) : defaultValue;
};

/**
 * Format diagnostic log for display
 */
export const formatDiagnosticLog = (normalized: NormalizedIntent): string[] => {
  const log: string[] = [];
  
  log.push(`[Request ID: ${normalized.requestId}]`);
  log.push(`Content Type: ${normalized.contentType}`);
  log.push(`Confidence: ${(normalized.confidence * 100).toFixed(1)}%`);
  log.push(`Inferred From: ${normalized.inferredFrom.join(', ')}`);
  
  if (normalized.missingFields.length > 0) {
    log.push(`Missing Fields: ${normalized.missingFields.join(', ')}`);
    log.push(`Can Auto-Fill: ${normalized.canAutoFill ? 'Yes' : 'No'}`);
  }
  
  log.push(`Extracted Entities: ${Object.keys(normalized.entities).length}`);
  Object.entries(normalized.entities).forEach(([key, value]) => {
    log.push(`  - ${key}: ${JSON.stringify(value)}`);
  });
  
  return log;
};
