/**
 * Enrichment Service
 * ===================
 * 
 * Automatically enriches incomplete payloads
 * Uses agent context, user history, and smart defaults
 * Calls backend enrichment endpoints when available
 * 
 * Version: 3.3
 * Phase: Track 3.3 - Auto-Enrichment
 */

import { ContentType, ValidationResult } from '../types/contentSchemas';
import { useCommandStore } from '../store/commandStore';

import api from './http';

export interface EnrichmentRequest {
  contentType: ContentType;
  payload: Record<string, any>;
  missingFields: string[];
  validationResult: ValidationResult;
  requestId: string;
}

export interface EnrichmentResult {
  enriched_payload: Record<string, any>;
  filled_fields: string[];
  confidence: number;
  sources: Record<string, string>;
}

/**
 * Enrich payload with missing fields
 */
export const enrichPayload = async (
  request: EnrichmentRequest
): Promise<EnrichmentResult> => {
  console.group(`[Enrichment] ${request.requestId}`);
  console.log('Content Type:', request.contentType);
  console.log('Missing Fields:', request.missingFields);
  console.time('Enrichment');

  try {
    // Try backend enrichment first
    const backendResult = await enrichWithBackend(request);
    
    if (backendResult) {
      console.log('✅ Backend enrichment successful');
      console.timeEnd('Enrichment');
      console.groupEnd();
      return backendResult;
    }
    
    // Fall back to local enrichment
    console.log('⚠️ Backend unavailable, using local enrichment');
    const localResult = enrichWithLocalContext(request);
    
    console.log('✅ Local enrichment complete:', {
      filled_fields: localResult.filled_fields.length,
      confidence: localResult.confidence,
    });
    
    console.timeEnd('Enrichment');
    console.groupEnd();
    
    return localResult;
    
  } catch (error) {
    console.error('❌ Enrichment error:', error);
    console.timeEnd('Enrichment');
    console.groupEnd();
    
    // Return minimal enrichment
    return {
      enriched_payload: request.payload,
      filled_fields: [],
      confidence: 0.3,
      sources: {},
    };
  }
};

/**
 * Enrich using backend service
 */
const enrichWithBackend = async (
  request: EnrichmentRequest
): Promise<EnrichmentResult | null> => {
  try {
    const endpoint = `/enrich/${request.contentType.toLowerCase()}`;

    const { data } = await api.post<EnrichmentResult>(endpoint, {
      payload: request.payload,
      missing_fields: request.missingFields,
      context: getEnrichmentContext(),
    });

    return data;
    
  } catch (error) {
    console.warn('Backend enrichment failed:', error);
    return null;
  }
};

/**
 * Enrich using local context and defaults
 */
const enrichWithLocalContext = (
  request: EnrichmentRequest
): EnrichmentResult => {
  const { contentType, payload, missingFields } = request;
  const enriched = { ...payload };
  const filled: string[] = [];
  const sources: Record<string, string> = {};
  
  // Get user context
  const store = useCommandStore.getState();
  const recentRequests = store.requests.slice(-10);
  const userPreferences = getUserPreferences();
  
  // Enrich based on content type
  missingFields.forEach(field => {
    const enrichmentAttempt = enrichField(
      field,
      contentType,
      enriched,
      recentRequests,
      userPreferences
    );
    
    if (enrichmentAttempt.value !== undefined) {
      enriched[field] = enrichmentAttempt.value;
      filled.push(field);
      sources[field] = enrichmentAttempt.source;
      console.log(`✓ Filled ${field} = ${enriched[field]} (from ${enrichmentAttempt.source})`);
    }
  });
  
  // Calculate confidence based on filled ratio and source quality
  const confidence = calculateEnrichmentConfidence(filled, sources, missingFields);
  
  return {
    enriched_payload: enriched,
    filled_fields: filled,
    confidence,
    sources,
  };
};

/**
 * Enrich a single field
 */
const enrichField = (
  field: string,
  contentType: ContentType,
  currentPayload: Record<string, any>,
  recentRequests: any[],
  preferences: Record<string, any>
): { value: any; source: string } => {
  // Try user preferences first
  if (preferences[field] !== undefined) {
    return { value: preferences[field], source: 'user_preferences' };
  }
  
  // Try recent requests
  const recentValue = extractFromRecentRequests(field, contentType, recentRequests);
  if (recentValue !== undefined) {
    return { value: recentValue, source: 'recent_requests' };
  }
  
  // Try contextual inference
  const inferredValue = inferFromContext(field, contentType, currentPayload);
  if (inferredValue !== undefined) {
    return { value: inferredValue, source: 'contextual_inference' };
  }
  
  // Fall back to smart defaults
  const defaultValue = getSmartDefault(field, contentType);
  if (defaultValue !== undefined) {
    return { value: defaultValue, source: 'smart_defaults' };
  }
  
  return { value: undefined, source: 'none' };
};

/**
 * Extract field value from recent requests
 */
const extractFromRecentRequests = (
  field: string,
  contentType: ContentType,
  recentRequests: any[]
): any => {
  // Look for recent requests of same content type
  const sameTypeRequests = recentRequests.filter(
    req => req.contentType === contentType
  );
  
  // Find most recent with this field populated
  for (const req of sameTypeRequests.reverse()) {
    if (req.content?.metadata?.[field]) {
      return req.content.metadata[field];
    }
  }
  
  return undefined;
};

/**
 * Infer field value from current context
 */
const inferFromContext = (
  field: string,
  contentType: ContentType,
  currentPayload: Record<string, any>
): any => {
  // Address/region inference
  if (field === 'region' && currentPayload.address) {
    // Extract city/region from address
    const parts = currentPayload.address.split(',').map((s: string) => s.trim());
    return parts[parts.length - 2] || parts[0];
  }
  
  if (field === 'address' && currentPayload.region) {
    // Can't reliably infer address from region
    return undefined;
  }
  
  // Property type inference
  if (field === 'property_type' && currentPayload.address) {
    // Check if address contains keywords
    const addr = currentPayload.address.toLowerCase();
    if (addr.includes('condo')) return 'condo';
    if (addr.includes('townhouse')) return 'townhouse';
    if (addr.includes('apt') || addr.includes('unit')) return 'condo';
  }
  
  // Target audience inference
  if (field === 'target_audience') {
    if (contentType === ContentType.PITCH_DECK) return 'investors';
    if (contentType === ContentType.NEWSLETTER) return 'clients';
  }
  
  return undefined;
};

/**
 * Get smart defaults for field
 */
const getSmartDefault = (field: string, contentType: ContentType): any => {
  const defaults: Record<string, Record<string, any>> = {
    [ContentType.CMA_REPORT]: {
      property_type: 'single_family',
      comparable_count: 5,
      date_range: '6_months',
    },
    [ContentType.PITCH_DECK]: {
      property_type: 'luxury',
      investment_type: 'acquisition',
      target_audience: 'investors',
      slide_count: 10,
    },
    [ContentType.MARKET_REPORT]: {
      property_type: 'mixed',
      time_period: 'quarterly',
      metrics: ['price_trends', 'volume', 'inventory'],
    },
    [ContentType.NEWSLETTER]: {
      tone: 'professional',
      target_audience: 'clients',
    },
    [ContentType.SOCIAL_POST]: {
      platform: 'instagram',
      tone: 'engaging',
      hashtags: [],
    },
  };
  
  return defaults[contentType]?.[field];
};

/**
 * Get user preferences from store
 */
const getUserPreferences = (): Record<string, any> => {
  const store = useCommandStore.getState();
  
  // Extract preferences from user profile or settings
  return {
    default_property_type: localStorage.getItem('default_property_type'),
    default_region: localStorage.getItem('default_region'),
    preferred_comparable_count: localStorage.getItem('preferred_comparable_count'),
    // Add more preferences as needed
  };
};

/**
 * Get enrichment context for backend
 */
const getEnrichmentContext = (): Record<string, any> => {
  const store = useCommandStore.getState();
  const recentRequests = store.requests.slice(-5);
  
  return {
    recent_content_types: recentRequests.map(r => r.contentType),
    recent_regions: recentRequests
      .map(r => r.content?.metadata?.region || r.content?.metadata?.address)
      .filter(Boolean),
    user_preferences: getUserPreferences(),
    timestamp: new Date().toISOString(),
  };
};

/**
 * Calculate enrichment confidence score
 */
const calculateEnrichmentConfidence = (
  filledFields: string[],
  sources: Record<string, string>,
  missingFields: string[]
): number => {
  if (missingFields.length === 0) return 1.0;
  if (filledFields.length === 0) return 0.0;
  
  const fillRatio = filledFields.length / missingFields.length;
  
  // Weight by source quality
  const sourceWeights: Record<string, number> = {
    user_preferences: 1.0,
    recent_requests: 0.8,
    contextual_inference: 0.6,
    smart_defaults: 0.4,
    none: 0.0,
  };
  
  const avgSourceQuality = filledFields.reduce((sum, field) => {
    return sum + (sourceWeights[sources[field]] || 0);
  }, 0) / filledFields.length;
  
  // Blend fill ratio and source quality
  return (fillRatio * 0.6) + (avgSourceQuality * 0.4);
};

/**
 * Format enrichment result for logging
 */
export const formatEnrichmentLog = (result: EnrichmentResult): string[] => {
  const log: string[] = [];
  
  log.push(`Enrichment: ${result.filled_fields.length} fields filled`);
  log.push(`Confidence: ${(result.confidence * 100).toFixed(1)}%`);
  
  if (result.filled_fields.length > 0) {
    log.push('Filled Fields:');
    result.filled_fields.forEach(field => {
      const value = result.enriched_payload[field];
      const source = result.sources[field];
      log.push(`  - ${field}: ${JSON.stringify(value)} (${source})`);
    });
  }
  
  return log;
};

/**
 * Check if payload is ready for generation
 */
export const isPayloadReady = (
  payload: Record<string, any>,
  contentType: ContentType,
  confidence: number
): { ready: boolean; reason?: string } => {
  // Check minimum confidence threshold
  if (confidence < 0.5) {
    return {
      ready: false,
      reason: 'Confidence too low - missing critical fields',
    };
  }
  
  // Check required fields are present
  const required = getRequiredFieldsForContentType(contentType);
  const missing = required.filter(field => !payload[field]);
  
  if (missing.length > 0) {
    return {
      ready: false,
      reason: `Required fields missing: ${missing.join(', ')}`,
    };
  }
  
  return { ready: true };
};

/**
 * Get required fields for content type
 */
const getRequiredFieldsForContentType = (contentType: ContentType): string[] => {
  const requirements: Record<ContentType, string[]> = {
    [ContentType.CMA_REPORT]: ['address'],
    [ContentType.PITCH_DECK]: ['address'],
    [ContentType.MARKET_REPORT]: ['region'],
    [ContentType.NEWSLETTER]: ['topic'],
    [ContentType.SOCIAL_POST]: ['topic'],
  };
  
  return requirements[contentType] || [];
};
