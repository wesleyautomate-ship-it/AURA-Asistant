/**
 * Content Save Service
 * =====================
 * 
 * Transforms backend responses to frontend schemas
 * Saves content to store with proper metadata
 * Manages content versioning and updates
 * 
 * Version: 3.4
 * Phase: Track 3.4 - Content Transformation & Persistence
 */

import { 
  ContentType, 
  BaseContent,
  CMAReportContent,
  PitchDeckContent,
  MarketReportContent,
  NewsletterContent,
  SocialPostContent,
  ContentStatus,
  SchemaVersion,
} from '../types/contentSchemas';
import { useCommandStore } from '../store/commandStore';

export interface BackendContentResponse {
  content_type: string;
  data: any;
  metadata?: Record<string, any>;
  generation_info?: {
    model_used?: string;
    tokens?: number;
    duration_ms?: number;
  };
}

export interface SaveContentRequest {
  requestId: string;
  backendResponse: BackendContentResponse;
  originalPayload: Record<string, any>;
  enrichmentSources?: Record<string, string>;
}

export interface SaveContentResult {
  success: boolean;
  contentId: string;
  error?: string;
}

/**
 * Transform and save generated content
 */
export const saveGeneratedContent = async (
  request: SaveContentRequest
): Promise<SaveContentResult> => {
  console.group(`[Content Save] ${request.requestId}`);
  console.log('Content Type:', request.backendResponse.content_type);
  console.time('Content Save');

  try {
    // Transform backend response to frontend schema
    const content = transformBackendResponse(
      request.backendResponse,
      request.originalPayload,
      request.enrichmentSources
    );

    // Validate transformed content
    const validation = validateContent(content);
    if (!validation.valid) {
      throw new Error(`Content validation failed: ${validation.errors.join(', ')}`);
    }

    // Save to store
    const store = useCommandStore.getState();
    store.saveContent(request.requestId, content);

    console.log('✅ Content saved successfully');
    console.log('Content ID:', content.id);
    console.log('Schema Version:', content.schemaVersion);
    
    console.timeEnd('Content Save');
    console.groupEnd();

    return {
      success: true,
      contentId: content.id,
    };

  } catch (error) {
    console.error('❌ Content save error:', error);
    console.timeEnd('Content Save');
    console.groupEnd();

    return {
      success: false,
      contentId: '',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

/**
 * Transform backend response to frontend schema
 */
const transformBackendResponse = (
  response: BackendContentResponse,
  originalPayload: Record<string, any>,
  enrichmentSources?: Record<string, string>
): BaseContent => {
  const contentType = normalizeContentType(response.content_type);
  const baseContent: BaseContent = {
    id: generateContentId(),
    type: contentType,
    status: ContentStatus.COMPLETED,
    version: 1,
    schemaVersion: SchemaVersion.V1,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    metadata: {
      ...response.metadata,
      ...originalPayload,
      enrichment_sources: enrichmentSources,
      generation_info: response.generation_info,
    },
    sections: [],
  };

  // Transform based on content type
  switch (contentType) {
    case ContentType.CMA_REPORT:
      return transformCMAReport(baseContent, response.data);
    
    case ContentType.PITCH_DECK:
      return transformPitchDeck(baseContent, response.data);
    
    case ContentType.MARKET_REPORT:
      return transformMarketReport(baseContent, response.data);
    
    case ContentType.NEWSLETTER:
      return transformNewsletter(baseContent, response.data);
    
    case ContentType.SOCIAL_POST:
      return transformSocialPost(baseContent, response.data);
    
    default:
      throw new Error(`Unsupported content type: ${contentType}`);
  }
};

/**
 * Transform CMA Report
 */
const transformCMAReport = (
  base: BaseContent,
  data: any
): CMAReportContent => {
  return {
    ...base,
    type: ContentType.CMA_REPORT,
    sections: data.sections || [],
    summary: data.summary || '',
    comparables: data.comparables || [],
    valuationRange: data.valuation_range || {
      low: 0,
      mid: 0,
      high: 0,
      confidence: 0,
    },
    marketMetrics: data.market_metrics || {},
  };
};

/**
 * Transform Pitch Deck
 */
const transformPitchDeck = (
  base: BaseContent,
  data: any
): PitchDeckContent => {
  return {
    ...base,
    type: ContentType.PITCH_DECK,
    sections: data.slides || data.sections || [],
    slides: data.slides || [],
    theme: data.theme || 'professional',
    targetAudience: data.target_audience || 'investors',
  };
};

/**
 * Transform Market Report
 */
const transformMarketReport = (
  base: BaseContent,
  data: any
): MarketReportContent => {
  return {
    ...base,
    type: ContentType.MARKET_REPORT,
    sections: data.sections || [],
    region: data.region || base.metadata.region,
    timePeriod: data.time_period || base.metadata.time_period,
    metrics: data.metrics || {},
    trends: data.trends || [],
    insights: data.insights || [],
  };
};

/**
 * Transform Newsletter
 */
const transformNewsletter = (
  base: BaseContent,
  data: any
): NewsletterContent => {
  return {
    ...base,
    type: ContentType.NEWSLETTER,
    sections: data.sections || [],
    subject: data.subject || data.title || '',
    preheader: data.preheader || '',
    content: data.content || data.body || '',
    cta: data.cta || null,
  };
};

/**
 * Transform Social Post
 */
const transformSocialPost = (
  base: BaseContent,
  data: any
): SocialPostContent => {
  return {
    ...base,
    type: ContentType.SOCIAL_POST,
    sections: data.sections || [],
    platform: data.platform || base.metadata.platform || 'instagram',
    content: data.content || data.text || '',
    hashtags: data.hashtags || [],
    media: data.media || [],
  };
};

/**
 * Normalize content type string
 */
const normalizeContentType = (type: string): ContentType => {
  const normalized = type.toLowerCase().replace(/[-_]/g, '_');
  
  const typeMap: Record<string, ContentType> = {
    'cma_report': ContentType.CMA_REPORT,
    'cma': ContentType.CMA_REPORT,
    'pitch_deck': ContentType.PITCH_DECK,
    'deck': ContentType.PITCH_DECK,
    'market_report': ContentType.MARKET_REPORT,
    'market': ContentType.MARKET_REPORT,
    'newsletter': ContentType.NEWSLETTER,
    'social_post': ContentType.SOCIAL_POST,
    'social': ContentType.SOCIAL_POST,
  };
  
  return typeMap[normalized] || ContentType.CMA_REPORT;
};

/**
 * Generate unique content ID
 */
const generateContentId = (): string => {
  return `content_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Validate transformed content
 */
const validateContent = (
  content: BaseContent
): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  // Validate required base fields
  if (!content.id) errors.push('Missing content ID');
  if (!content.type) errors.push('Missing content type');
  if (!content.status) errors.push('Missing content status');
  if (!content.version) errors.push('Missing content version');
  if (!content.schemaVersion) errors.push('Missing schema version');
  if (!content.createdAt) errors.push('Missing creation timestamp');
  if (!content.updatedAt) errors.push('Missing update timestamp');
  
  // Validate content-type specific fields
  switch (content.type) {
    case ContentType.CMA_REPORT:
      validateCMAReport(content as CMAReportContent, errors);
      break;
    
    case ContentType.PITCH_DECK:
      validatePitchDeck(content as PitchDeckContent, errors);
      break;
    
    case ContentType.MARKET_REPORT:
      validateMarketReport(content as MarketReportContent, errors);
      break;
    
    case ContentType.NEWSLETTER:
      validateNewsletter(content as NewsletterContent, errors);
      break;
    
    case ContentType.SOCIAL_POST:
      validateSocialPost(content as SocialPostContent, errors);
      break;
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
};

/**
 * Validate CMA Report content
 */
const validateCMAReport = (content: CMAReportContent, errors: string[]): void => {
  if (!content.comparables || content.comparables.length === 0) {
    errors.push('CMA Report missing comparables');
  }
  if (!content.valuationRange) {
    errors.push('CMA Report missing valuation range');
  }
};

/**
 * Validate Pitch Deck content
 */
const validatePitchDeck = (content: PitchDeckContent, errors: string[]): void => {
  if (!content.slides || content.slides.length === 0) {
    errors.push('Pitch Deck missing slides');
  }
  if (!content.targetAudience) {
    errors.push('Pitch Deck missing target audience');
  }
};

/**
 * Validate Market Report content
 */
const validateMarketReport = (content: MarketReportContent, errors: string[]): void => {
  if (!content.region) {
    errors.push('Market Report missing region');
  }
  if (!content.metrics || Object.keys(content.metrics).length === 0) {
    errors.push('Market Report missing metrics');
  }
};

/**
 * Validate Newsletter content
 */
const validateNewsletter = (content: NewsletterContent, errors: string[]): void => {
  if (!content.subject || content.subject.trim().length === 0) {
    errors.push('Newsletter missing subject');
  }
  if (!content.content || content.content.trim().length === 0) {
    errors.push('Newsletter missing content');
  }
};

/**
 * Validate Social Post content
 */
const validateSocialPost = (content: SocialPostContent, errors: string[]): void => {
  if (!content.platform) {
    errors.push('Social Post missing platform');
  }
  if (!content.content || content.content.trim().length === 0) {
    errors.push('Social Post missing content');
  }
};

/**
 * Update existing content
 */
export const updateContent = async (
  contentId: string,
  updates: Partial<BaseContent>
): Promise<SaveContentResult> => {
  console.group(`[Content Update] ${contentId}`);
  console.time('Content Update');

  try {
    const store = useCommandStore.getState();
    const request = store.requests.find(r => r.content?.id === contentId);
    
    if (!request) {
      throw new Error('Content not found');
    }

    const updatedContent = {
      ...request.content,
      ...updates,
      version: (request.content?.version || 0) + 1,
      updatedAt: new Date().toISOString(),
    } as BaseContent;

    // Validate updated content
    const validation = validateContent(updatedContent);
    if (!validation.valid) {
      throw new Error(`Content validation failed: ${validation.errors.join(', ')}`);
    }

    // Update in store
    store.updateContent(request.id, updatedContent);

    console.log('✅ Content updated successfully');
    console.log('New version:', updatedContent.version);
    
    console.timeEnd('Content Update');
    console.groupEnd();

    return {
      success: true,
      contentId: updatedContent.id,
    };

  } catch (error) {
    console.error('❌ Content update error:', error);
    console.timeEnd('Content Update');
    console.groupEnd();

    return {
      success: false,
      contentId,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

/**
 * Delete content
 */
export const deleteContent = async (
  requestId: string
): Promise<{ success: boolean; error?: string }> => {
  console.group(`[Content Delete] ${requestId}`);

  try {
    const store = useCommandStore.getState();
    store.removeContent(requestId);

    console.log('✅ Content deleted successfully');
    console.groupEnd();

    return { success: true };

  } catch (error) {
    console.error('❌ Content delete error:', error);
    console.groupEnd();

    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

/**
 * Format save result for logging
 */
export const formatSaveLog = (result: SaveContentResult): string[] => {
  const log: string[] = [];
  
  if (result.success) {
    log.push('✅ Content saved successfully');
    log.push(`Content ID: ${result.contentId}`);
  } else {
    log.push('❌ Content save failed');
    if (result.error) {
      log.push(`Error: ${result.error}`);
    }
  }
  
  return log;
};
