/**
 * Validation Service
 * ==================
 * 
 * Pre-validates payloads before API calls
 * Calls backend validator endpoints
 * Provides structured validation results
 * 
 * Version: 3.2
 * Phase: Track 3.2 - Pre-Validation
 */

import { ContentType, ValidationResult } from '../types/contentSchemas';
import { NormalizedIntent } from './intentNormalizer';
import api from './http';
import templateOrchestrator from './templateOrchestrator';
import type { AxiosError } from 'axios';

export interface ValidationRequest {
  contentType: ContentType;
  payload: Record<string, any>;
  requestId: string;
}

/**
 * Validate payload with backend validator
 */
export const validatePayload = async (
  request: ValidationRequest
): Promise<ValidationResult> => {
  console.group(`[Validation] ${request.requestId}`);
  console.log('Content Type:', request.contentType);
  console.log('Payload:', request.payload);
  console.time('Validation');

  try {
    const endpoint = `/validate/${request.contentType.toLowerCase()}`;

    const { data: result } = await api.post<ValidationResult>(endpoint, request.payload);
    
    console.log('✅ Validation Result:', {
      valid: result.valid,
      missing_fields: result.missing_fields,
      confidence: result.confidence,
      tips_count: result.tips.length,
    });
    
    console.timeEnd('Validation');
    console.groupEnd();

    return result;
    
  } catch (error) {
    console.error('❌ Validation error:', error);
    console.timeEnd('Validation');
    console.groupEnd();

    // Return pessimistic validation result on error
    // This allows enrichment to still attempt to fix issues
    return {
      valid: false,
      missing_fields: Object.keys(request.payload).filter(k => !request.payload[k]),
      normalized_payload: request.payload,
      tips: ['Validation service unavailable - will attempt enrichment'],
      confidence: 0.5,
    };
  }
};

/**
 * Build API payload from normalized intent
 */
export const buildPayload = (normalized: NormalizedIntent): Record<string, any> => {
  const { contentType, entities } = normalized;
  
  console.group('[Validation] Building Payload');
  console.log('Content Type:', contentType);
  console.log('Entities:', entities);
  
  let payload: Record<string, any> = {};
  
  switch (contentType) {
    case ContentType.CMA_REPORT:
      payload = {
        property_type: entities.propertyType || 'apartment',  // Required: apartment|villa|townhouse|penthouse|office|retail
        location: entities.address || entities.region,        // Required: location string
        bedrooms: entities.bedrooms || null,                  // Optional: number of bedrooms
        bathrooms: entities.bathrooms || null,                // Optional: number of bathrooms  
        area_sqft: entities.area_sqft || 1000,                // Required: area in square feet
        amenities: entities.amenities || [],                  // Optional: array of amenities
        building_age: entities.building_age || null,          // Optional: age of building
      };
      break;
    
    case ContentType.PITCH_DECK:
      payload = {
        address: entities.address || entities.region,
        property_type: entities.propertyType || 'luxury',
        investment_type: entities.investmentType || 'acquisition',
        target_audience: entities.targetAudience || 'investors',
        slide_count: entities.slideCount || 8,
      };
      break;
    
    case ContentType.MARKET_REPORT:
      payload = {
        region: entities.region || entities.address,
        property_type: entities.propertyType || 'mixed',
        time_period: entities.timePeriod || 'quarterly',
        metrics: entities.metricsRequired || ['price_trends', 'volume', 'inventory'],
      };
      break;
    
    case ContentType.NEWSLETTER:
      payload = {
        topic: entities.topic,
        tone: entities.tone || 'professional',
        target_audience: entities.targetAudience || 'clients',
      };
      break;
    
    case ContentType.SOCIAL_POST:
      payload = {
        topic: entities.topic,
        platform: entities.platform || 'instagram',
        tone: entities.tone || 'engaging',
        hashtags: entities.hashtags || [],
      };
      break;
    
    default:
      payload = entities;
  }
  
  console.log('Built Payload:', payload);
  console.groupEnd();
  
  return payload;
};

/**
 * Validate required fields are present
 */
export const validateRequiredFields = (
  payload: Record<string, any>,
  contentType: ContentType
): { valid: boolean; missing: string[] } => {
  const required = getRequiredFields(contentType);
  const missing = required.filter(field => !payload[field]);
  
  return {
    valid: missing.length === 0,
    missing,
  };
};

/**
 * Get required fields for content type
 */
const getRequiredFields = (contentType: ContentType): string[] => {
  const requirements: Record<ContentType, string[]> = {
    [ContentType.CMA_REPORT]: ['property_type', 'location', 'area_sqft'],  // Updated to match QuickValuationRequest
    [ContentType.PITCH_DECK]: ['address'],
    [ContentType.MARKET_REPORT]: ['region'],
    [ContentType.NEWSLETTER]: ['topic'],
    [ContentType.SOCIAL_POST]: ['topic'],
  };
  
  return requirements[contentType] || [];
};

/**
 * Apply validation tips to payload
 */
export const applyValidationTips = (
  payload: Record<string, any>,
  tips: string[]
): Record<string, any> => {
  const enhanced = { ...payload };
  
  console.group('[Validation] Applying Tips');
  
  tips.forEach(tip => {
    // Parse tips like "Consider setting comparable_count to 5"
    const match = tip.match(/setting (\w+) to (.+)$/);
    if (match) {
      const [, field, value] = match;
      if (!enhanced[field]) {
        enhanced[field] = parseValue(value);
        console.log(`✓ Applied tip: ${field} = ${enhanced[field]}`);
      }
    }
  });
  
  console.groupEnd();
  
  return enhanced;
};

/**
 * Parse string value to appropriate type
 */
const parseValue = (value: string): any => {
  const trimmed = value.trim();
  
  // Number
  if (/^\d+$/.test(trimmed)) {
    return parseInt(trimmed, 10);
  }
  
  // Boolean
  if (trimmed === 'true') return true;
  if (trimmed === 'false') return false;
  
  // Array (simple comma-separated)
  if (trimmed.includes(',')) {
    return trimmed.split(',').map(s => s.trim());
  }
  
  // String (remove quotes if present)
  return trimmed.replace(/^["']|["']$/g, '');
};

/**
 * Format validation result for logging
 */
export const formatValidationLog = (result: ValidationResult): string[] => {
  const log: string[] = [];
  
  log.push(`Validation: ${result.valid ? '✅ VALID' : '❌ INVALID'}`);
  log.push(`Confidence: ${(result.confidence * 100).toFixed(1)}%`);
  
  if (result.missing_fields.length > 0) {
    log.push(`Missing Fields (${result.missing_fields.length}):`);
    result.missing_fields.forEach(field => {
      log.push(`  - ${field}`);
    });
  }
  
  if (result.tips.length > 0) {
    log.push(`Tips (${result.tips.length}):`);
    result.tips.forEach(tip => {
      log.push(`  - ${tip}`);
    });
  }
  
  return log;
};

/**
 * 🔧 Unified validation and generation - replaces two-step pipeline
 * 
 * This function combines validation and generation into a single call,
 * using the correct FastAPI endpoints and providing proper error handling.
 */
export const validateAndGenerate = async (
  contentType: ContentType,
  payload: Record<string, any>,
  requestId: string
): Promise<{ valid: boolean; data?: any; errors?: any[] }> => {
  const templateConfig = templateOrchestrator.getTemplateConfig(contentType as any);
  const endpoint = templateConfig.endpoint;
  console.log(`[Validation] Unified call to ${endpoint}`);
  const normalizedEndpoint = endpoint.startsWith('/api/v1') ? endpoint.replace('/api/v1', '') : endpoint;

  try {
    const { data } = await api.post(normalizedEndpoint, {
      ...payload,
      request_id: requestId,
    });
    console.log('[Validation] ✅ Success');
    return { valid: true, data };
  } catch (err) {
    const error = err as AxiosError<any>;
    if (error.response?.status === 422) {
      const detail = error.response.data?.detail;
      console.warn('[Validation] ⚠️ Schema validation failed (422):', detail);
      return {
        valid: false,
        errors: Array.isArray(detail) ? detail : [detail],
      };
    }

    console.error('[Validation] ❌ Error:', error.message);
    throw error;
  }


};
