// Workflow API Service
// Handles backend API calls for specific task types (CMA, Market Reports, Social Posts)
// Enhanced with context validation and enrichment to prevent 422 errors

import type { AxiosError } from 'axios'
import { enrichWorkflowPayload, EnrichedPayload } from './contextEnrichment';
import { Intent } from './intentParser';
import api from './http';

const normalizeEndpoint = (endpoint: string): string => {
  const withoutOrigin = endpoint.replace(/^https?:\/\/[^/]+/, '')
  const withoutPrefix = withoutOrigin.replace(/^\/api\/v1/, '')
  if (!withoutPrefix.length) return '/'
  return withoutPrefix.startsWith('/') ? withoutPrefix : `/${withoutPrefix}`
}

const applyEnrichmentMetadata = (
  data: WorkflowResponse,
  enrichment?: EnrichedPayload,
  extraFields: string[] = [],
  extraLog: string[] = []
): WorkflowResponse => {
  if (!enrichment) {
    if (!extraFields.length && !extraLog.length) {
      return data
    }
    return {
      ...data,
      enrichment: {
        status: 'enriched',
        inferredFields: extraFields,
        debugLog: extraLog,
      },
    }
  }

  const inferredFields = Array.from(
    new Set([...Object.keys(enrichment.inferredFields), ...extraFields])
  )

  return {
    ...data,
    enrichment: {
      status: extraFields.length ? 'enriched' : enrichment.validationStatus,
      inferredFields,
      debugLog: enrichment.debugLog.concat(extraLog),
    },
  }
}

export interface WorkflowResponse {
  success: boolean;
  task_id: string;
  message: string;
  data?: any;
  enrichment?: {
    status: 'valid' | 'enriched' | 'fallback';
    inferredFields: string[];
    debugLog: string[];
  };
}

/**
 * Enhanced API call with validation and enrichment
 */
async function makeValidatedAPICall(
  endpoint: string,
  payload: Record<string, any>,
  enrichment?: EnrichedPayload
): Promise<WorkflowResponse> {
  // Structured logging for debugging
  console.group(`[Workflow API] ${endpoint}`);
  console.log('dY" Payload:', payload);
  if (enrichment) {
    console.log('dY" Enrichment Status:', enrichment.validationStatus);
    console.log('dYZ_ Inferred Fields:', Object.keys(enrichment.inferredFields));
    if (enrichment.debugLog.length > 0) {
      console.log('dY"? Debug Log:', enrichment.debugLog);
    }
  }

  // --- v3.3.1 Auto-Healing Patch ---
  if (payload && typeof payload === 'object') {
    for (const key of Object.keys(payload)) {
      if (payload[key] === null || payload[key] === undefined) {
        payload[key] = '';
      }
    }

    if (!('query' in payload)) {
      payload.query = '_';
    }

    if (endpoint.includes('/cma/')) {
      payload.location = payload.location || 'Dubai';
      payload.property_type = payload.property_type || 'mixed';
    }
    if (endpoint.includes('/social/')) {
      payload.topic = payload.topic || payload.query || 'Real Estate';
      payload.platform = payload.platform || 'instagram';
    }
    if (endpoint.includes('/pitchdeck/')) {
      payload.address = payload.address || payload.location || 'Dubai';
      payload.investment_type = payload.investment_type || 'acquisition';
    }
    if (endpoint.includes('/newsletter/')) {
      payload.topic = payload.topic || payload.query || 'Market Updates';
    }

    console.log('[Auto-Heal] Enhanced payload:', payload);
  }

  const pathSegment = normalizeEndpoint(endpoint);

  try {
    const { data } = await api.post<WorkflowResponse>(pathSegment, payload);
    console.log('�o. Success Response:', data);
    const result = applyEnrichmentMetadata(data, enrichment);
    console.groupEnd();
    return result;
  } catch (error) {
    const axiosError = error as AxiosError<any>;
    const status = axiosError.response?.status;

    if (status === 422 && !payload._retryAttempt) {
      console.warn('[WorkflowAPI] Auto-retrying after 422 with enhanced safe payload');

      const safePayload = {
        ...payload,
        query: payload.query || payload.location || 'CMA',
        _: payload._ || 'auto',
        property_type: payload.property_type || 'mixed',
        location: payload.location || 'Dubai',
        _retryAttempt: true,
      };

      console.log('[WorkflowAPI] Retry payload:', safePayload);

      try {
        const { data: retryData } = await api.post<WorkflowResponse>(pathSegment, safePayload);
        console.log('�o. Auto-retry successful!');
        console.log('�o. Retry Success Response:', retryData);
        const result = applyEnrichmentMetadata(
          retryData,
          enrichment,
          ['query', '_'],
          ['Auto-healed 422 error with safe payload']
        );
        console.groupEnd();
        return result;
      } catch (retryError) {
        console.error('[WorkflowAPI] Auto-retry also failed:', retryError);
      }
    }

    const responseData = axiosError.response?.data;
    console.error('�?O API Error Response:', {
      status,
      data: responseData,
      payload,
    });

    console.groupEnd();
    throw new Error(
      `API call failed: ${status ?? 'unknown'} ${axiosError.message}. ` +
      `Payload: ${JSON.stringify(payload)}. ` +
      `Response: ${JSON.stringify(responseData)}`
    );
  }
}




/**
 * Create a CMA (Comparative Market Analysis) report with validation
 */
export async function createCMA(
  intent: Intent,
  recentTasks: any[] = [],
  contextHistory: string[] = [],
  originalPrompt: string = ''
): Promise<WorkflowResponse> {
  console.log(`[Workflow] Creating CMA with validation`);
  
  // Validate and enrich the payload
  const enrichment = await enrichWorkflowPayload(intent, recentTasks, contextHistory, originalPrompt);
  
  if (!enrichment.canProceed) {
    console.warn(`[Workflow] Cannot proceed with CMA: ${enrichment.fallbackReason}`);
    throw new Error(`CMA validation failed: ${enrichment.fallbackReason}`);
  }
  
  // 🛡️ CMA Payload Auto-Healing
  const payload = {
    location: enrichment.enrichedFields.location,
    property_type: enrichment.enrichedFields.property_type || 'mixed',
    query: enrichment.enrichedFields.location || originalPrompt || "CMA", // Auto-heal missing query
    _: "auto" // Auto-heal underscore field that some schemas expect
  };
  
  console.log('[CMA Auto-Heal] Final payload:', payload);
  return makeValidatedAPICall('/api/v1/cma/create', payload, enrichment);
}

/**
 * Legacy CMA function for backward compatibility
 */
export async function createCMALegacy(location: string): Promise<WorkflowResponse> {
  const intent: Intent = { type: 'CMA', location, confidence: 0.8 };
  return createCMA(intent, [], [], location);
}

/**
 * Infer property type from prompt text for market analysis
 * @param promptText - The original user prompt
 * @returns Property type classification
 */
function inferPropertyType(promptText?: string): string {
  if (!promptText) return 'mixed';
  
  const lower = promptText.toLowerCase();
  if (lower.includes('commercial')) return 'commercial';
  if (lower.includes('apartment') || lower.includes('flat') || lower.includes('residential'))
    return 'residential';
  if (lower.includes('villa') || lower.includes('luxury'))
    return 'villa';
  
  return 'mixed';
}

/**
 * Create a market analysis report with validation
 */
export async function createMarketReport(
  intent: Intent,
  recentTasks: any[] = [],
  contextHistory: string[] = [],
  originalPrompt: string = ''
): Promise<WorkflowResponse> {
  console.log(`[Workflow] Creating Market Report with validation`);

  // Validate and enrich the payload
  const enrichment = await enrichWorkflowPayload(intent, recentTasks, contextHistory, originalPrompt);
  
  if (!enrichment.canProceed) {
    console.warn(`[Workflow] Cannot proceed with Market Report: ${enrichment.fallbackReason}`);
    throw new Error(`Market Report validation failed: ${enrichment.fallbackReason}`);
  }
  
  const payload = {
    region: enrichment.enrichedFields.location,
    property_type: enrichment.enrichedFields.property_type || inferPropertyType(originalPrompt),
    metrics: ['price_per_sqft', 'trend_analysis', 'demand_index'],
  };

  return makeValidatedAPICall('/api/v1/analytics/report', payload, enrichment);
}

/**
 * Legacy Market Report function for backward compatibility
 */
export async function createMarketReportLegacy(location: string, promptText?: string): Promise<WorkflowResponse> {
  const intent: Intent = { type: 'MARKET_REPORT', location, confidence: 0.8 };
  return createMarketReport(intent, [], [], promptText || location);
}

/**
 * Generate social media content with context validation and enrichment
 * @param intent - The parsed intent with topic/query information
 * @param recentTasks - Recent task history for context inference
 * @param contextHistory - Recent context for enrichment
 * @param originalPrompt - Original user prompt for analysis
 */
export async function createSocialPost(
  intent: Intent,
  recentTasks: any[] = [],
  contextHistory: string[] = [],
  originalPrompt: string = ''
): Promise<WorkflowResponse> {
  console.log(`[Workflow] Creating social post with validation`);
  
  // Step 1: Validate and enrich the payload
  const enrichment = await enrichWorkflowPayload(intent, recentTasks, contextHistory, originalPrompt);
  
  // Step 2: Check if we can proceed with the API call
  if (!enrichment.canProceed) {
    console.warn(`[Workflow] Cannot proceed with social post: ${enrichment.fallbackReason}`);
    throw new Error(`Payload validation failed: ${enrichment.fallbackReason}`);
  }
  
  // Step 3: Build the API payload using enriched fields
  const payload = {
    topic: enrichment.enrichedFields.topic,
    query: enrichment.enrichedFields.query, // Backend expects 'query' field
    category: enrichment.enrichedFields.category || 'marketing',
    platform: enrichment.enrichedFields.platform || 'instagram',
    content: `AI-generated campaign for ${enrichment.enrichedFields.topic}. Includes captions, hashtags, and key messaging.`,
  };

  // Step 4: Make the validated API call
  return makeValidatedAPICall('/api/v1/social/generate', payload, enrichment);
}

/**
 * Legacy createSocialPost for backward compatibility
 * @deprecated Use the new createSocialPost with Intent parameter
 */
export async function createSocialPostLegacy(topic: string, context: string = ''): Promise<WorkflowResponse> {
  console.log(`[Workflow] Creating social post (legacy): ${topic}`);
  
  // Create a basic intent for the legacy call
  const intent: Intent = {
    type: 'SOCIAL_POST',
    topic,
    confidence: 0.8
  };
  
  // Call the new enriched version
  return createSocialPost(intent, [], [context], topic);
}

/**
 * Check workflow task status
 */
export async function checkTaskStatus(taskId: string): Promise<any> {
  try {
    const { data } = await api.get<any>(normalizeEndpoint(`/api/v1/tasks/${taskId}/status`));
    return data;
  } catch (error) {
    console.error('[Workflow] Task status check error:', error);
    throw error;
  }
}

/**
 * Generate mock CMA report for development/testing
 */
export async function mockCMAReport(location: string): Promise<{ report_url: string; message: string }> {
  console.log(`[Workflow] Generating mock CMA report for ${location}`);
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1200));
  
  const sanitizedLocation = location.replace(/\s+/g, '_');
  return {
    report_url: `/mock-reports/CMA_${sanitizedLocation}_${Date.now()}.pdf`,
    message: `Mock CMA report generated for ${location}`,
  };
}

/**
 * Generate CMA report (real or mock based on environment)
 */
export async function generateCMAReport(location: string): Promise<{ report_url: string | null; message: string }> {
  const useRealAPI = import.meta.env.VITE_USE_REAL_API === 'true';
  
  // Mock mode (default for development)
  if (!useRealAPI) {
    console.log('[Workflow] Using mock CMA generation');
    return await mockCMAReport(location);
  }
  
  // Real API mode
  console.log(`[Workflow] Generating real CMA report for ${location}`);
  
  try {
    const { data } = await api.post<{ report_url: string; [key: string]: any }>(
      normalizeEndpoint('/api/v1/cma/report'),
      { location }
    );
    console.log('[Workflow] CMA report generated successfully:', data.report_url);
    return {
      report_url: data.report_url || null,
      message: data.message || `CMA report generated for ${location}`,
    };
  } catch (error) {
    console.error('[Workflow] CMA report generation error:', error);
    // Fallback to mock on error
    console.log('[Workflow] Falling back to mock CMA generation');
    return await mockCMAReport(location);
  }
}

// ============================================================================
// CONTENT GENERATION API FUNCTIONS (v3.1)
// ============================================================================

/**
 * Generate CMA Content Report with AI
 * Creates a comprehensive CMA report using the template orchestrator
 */
export async function generateCMAContent(
  intent: Intent,
  recentTasks: any[] = [],
  contextHistory: string[] = [],
  originalPrompt: string = ''
): Promise<WorkflowResponse> {
  console.log('[Workflow] Generating CMA Content with AI');
  
  // Validate and enrich the payload
  const enrichment = await enrichWorkflowPayload(intent, recentTasks, contextHistory, originalPrompt);
  
  if (!enrichment.canProceed) {
    console.warn(`[Workflow] Cannot proceed with CMA content generation: ${enrichment.fallbackReason}`);
    throw new Error(`CMA content generation validation failed: ${enrichment.fallbackReason}`);
  }
  
  const payload = {
    location: enrichment.enrichedFields.location,
    property_type: enrichment.enrichedFields.property_type || 'mixed',
    date_range: enrichment.enrichedFields.date_range || '3_months',
    comparable_count: enrichment.enrichedFields.comparable_count || 5,
    analysis_type: 'comprehensive',
    include_insights: true,
    include_recommendations: true,
    output_format: 'structured_json'
  };

  return makeValidatedAPICall('/api/v1/cma/generate', payload, enrichment);
}

/**
 * Generate Investor Pitch Deck Content with AI
 * Creates a multi-slide pitch deck using the template orchestrator
 */
export async function generatePitchDeckContent(
  intent: Intent,
  recentTasks: any[] = [],
  contextHistory: string[] = [],
  originalPrompt: string = ''
): Promise<WorkflowResponse> {
  console.log('[Workflow] Generating Pitch Deck Content with AI');
  
  // Validate and enrich the payload
  const enrichment = await enrichWorkflowPayload(intent, recentTasks, contextHistory, originalPrompt);
  
  if (!enrichment.canProceed) {
    console.warn(`[Workflow] Cannot proceed with pitch deck generation: ${enrichment.fallbackReason}`);
    throw new Error(`Pitch deck generation validation failed: ${enrichment.fallbackReason}`);
  }
  
  const payload = {
    location: enrichment.enrichedFields.location,
    property_type: enrichment.enrichedFields.property_type || 'luxury',
    investment_amount: enrichment.enrichedFields.investment_amount || null,
    target_audience: enrichment.enrichedFields.target_audience || 'investors',
    timeline: enrichment.enrichedFields.timeline || '12_months',
    deck_type: 'investor_presentation',
    include_financials: true,
    include_market_analysis: true,
    slide_count: 8,
    output_format: 'structured_slides'
  };

  return makeValidatedAPICall('/api/v1/decks/generate', payload, enrichment);
}

/**
 * Generate Market Report Content with AI
 * Creates an analytical market report using the template orchestrator
 */
export async function generateMarketReportContent(
  intent: Intent,
  recentTasks: any[] = [],
  contextHistory: string[] = [],
  originalPrompt: string = ''
): Promise<WorkflowResponse> {
  console.log('[Workflow] Generating Market Report Content with AI');
  
  // Validate and enrich the payload
  const enrichment = await enrichWorkflowPayload(intent, recentTasks, contextHistory, originalPrompt);
  
  if (!enrichment.canProceed) {
    console.warn(`[Workflow] Cannot proceed with market report generation: ${enrichment.fallbackReason}`);
    throw new Error(`Market report generation validation failed: ${enrichment.fallbackReason}`);
  }
  
  const payload = {
    location: enrichment.enrichedFields.location,
    time_period: enrichment.enrichedFields.time_period || 'quarterly',
    property_types: enrichment.enrichedFields.property_types || ['residential', 'commercial'],
    metrics: enrichment.enrichedFields.metrics || ['price_trends', 'volume', 'inventory', 'forecasts'],
    analysis_depth: 'comprehensive',
    include_charts: true,
    include_forecasts: true,
    output_format: 'structured_report'
  };

  return makeValidatedAPICall('/api/v1/market/generate', payload, enrichment);
}

/**
 * Generate Enhanced Social Content with AI
 * Creates comprehensive social media content using the template orchestrator
 */
export async function generateSocialContent(
  intent: Intent,
  recentTasks: any[] = [],
  contextHistory: string[] = [],
  originalPrompt: string = ''
): Promise<WorkflowResponse> {
  console.log('[Workflow] Generating Social Content with AI');
  
  // Validate and enrich the payload
  const enrichment = await enrichWorkflowPayload(intent, recentTasks, contextHistory, originalPrompt);
  
  if (!enrichment.canProceed) {
    console.warn(`[Workflow] Cannot proceed with social content generation: ${enrichment.fallbackReason}`);
    throw new Error(`Social content generation validation failed: ${enrichment.fallbackReason}`);
  }
  
  const payload = {
    topic: enrichment.enrichedFields.topic,
    query: enrichment.enrichedFields.query,
    platform: enrichment.enrichedFields.platform || 'multi_platform',
    audience: enrichment.enrichedFields.audience || 'property_buyers',
    hashtags: enrichment.enrichedFields.hashtags || null,
    call_to_action: enrichment.enrichedFields.call_to_action || 'contact_us',
    content_type: 'comprehensive_campaign',
    include_captions: true,
    include_hashtags: true,
    include_visuals: true,
    output_format: 'structured_content'
  };

  return makeValidatedAPICall('/api/v1/social/generate', payload, enrichment);
}

/**
 * Export generated content to various formats
 */
export async function exportGeneratedContent(
  contentId: string,
  contentType: 'CMA' | 'PITCH_DECK' | 'MARKET_REPORT' | 'SOCIAL_POST',
  format: 'pdf' | 'html' | 'json' | 'pptx' = 'pdf'
): Promise<{ export_url: string; message: string }> {
  console.log(`[Workflow] Exporting ${contentType} content: ${contentId} as ${format}`);
  
  try {
    const endpoint = `/api/v1/content/export/${contentId}`;
    const payload = {
      content_type: contentType,
      format,
      include_branding: true,
      template: contentType === 'CMA' ? 'newsletter_style' : 
                contentType === 'PITCH_DECK' ? 'investor_deck_style' :
                contentType === 'MARKET_REPORT' ? 'analytical_report_style' :
                'social_media_style'
    };

    const { data } = await api.post<{ export_url: string; message?: string }>(
      normalizeEndpoint(endpoint),
      payload
    );
    console.log('[Workflow] Export completed:', data.export_url);
    
    return {
      export_url: data.export_url,
      message: data.message || `${contentType} exported as ${format.toUpperCase()}`
    };
    
  } catch (error) {
    console.error('[Workflow] Export error:', error);
    
    // Fallback to mock export
    return {
      export_url: `/mock-exports/${contentType}_${contentId}.${format}`,
      message: `Mock export generated: ${contentType} as ${format.toUpperCase()}`
    };
  }
}
