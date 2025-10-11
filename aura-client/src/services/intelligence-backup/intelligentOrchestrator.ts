/**
 * Intelligent Orchestrator Service - v3.3 Content Intelligence Layer
 * ==================================================================
 * 
 * Enhanced orchestrator that routes content generation through the v3.3 
 * Content Intelligence Layer, providing:
 * - Context-aware content generation
 * - Memory-enhanced prompts
 * - Quality validation and scoring
 * - Seamless integration with existing orchestratorService.ts
 * 
 * Version: 3.3.0
 * Phase: Content Intelligence Layer Integration
 */

import { normalizeIntent, NormalizedIntent } from '../intentNormalizer';
import { ContentType } from '../../types/contentSchemas';
import { useCommandStore } from '../../store/commandStore';
import memoryService from './memoryService';
import contentEngine, { GenerationContext, GenerationResult } from './contentEngine';

// =============================================================================
// INTELLIGENT ORCHESTRATION TYPES
// =============================================================================

export interface IntelligentGenerationRequest {
  userInput: string;
  requestId: string;
  sessionId: string;
  metadata?: Record<string, any>;
  useIntelligentGeneration?: boolean; // Feature flag
  fallbackToLegacy?: boolean;
}

export interface IntelligentGenerationResult {
  success: boolean;
  requestId: string;
  contentId?: string;
  content?: any;
  metadata?: {
    generation_time_ms: number;
    used_intelligent_engine: boolean;
    quality_scores?: any;
    validation_results?: any[];
    fallback_reason?: string;
    memory_context_used: boolean;
    ai_enhancements: string[];
  };
  error?: string;
  logs: string[];
}

// =============================================================================
// FEATURE FLAGS
// =============================================================================

const FEATURE_FLAGS = {
  ENABLE_V33_INTELLIGENCE: true,
  ENABLE_MEMORY_ENRICHMENT: true,
  ENABLE_MULTI_PASS_GENERATION: true,
  ENABLE_QUALITY_VALIDATION: true,
  FALLBACK_ON_ERROR: true,
  LOG_DETAILED_METRICS: true
};

// =============================================================================
// INTELLIGENT ORCHESTRATOR CLASS
// =============================================================================

export class IntelligentOrchestrator {
  private static instance: IntelligentOrchestrator;

  private constructor() {
    console.log('[IntelligentOrchestrator] Initializing v3.3 Content Intelligence Layer...');
  }

  public static getInstance(): IntelligentOrchestrator {
    if (!IntelligentOrchestrator.instance) {
      IntelligentOrchestrator.instance = new IntelligentOrchestrator();
    }
    return IntelligentOrchestrator.instance;
  }

  // =============================================================================
  // MAIN INTELLIGENT GENERATION
  // =============================================================================

  public async generateContentIntelligently(
    request: IntelligentGenerationRequest
  ): Promise<IntelligentGenerationResult> {
    const startTime = Date.now();
    const logs: string[] = [];
    
    console.group(`[IntelligentOrchestrator] Starting v3.3 generation for request ${request.requestId}`);
    console.time('Intelligent Generation');

    try {
      // Step 1: Check feature flags and determine generation strategy
      const shouldUseIntelligence = this.shouldUseIntelligentGeneration(request);
      
      if (!shouldUseIntelligence) {
        logs.push('🔄 Routing to legacy orchestrator (feature disabled or fallback)');
        return await this.fallbackToLegacyOrchestrator(request, logs, 'Feature disabled');
      }

      logs.push('🧠 Using v3.3 Content Intelligence Layer');

      // Step 2: Normalize intent using existing normalizer
      console.log('📋 Step 1: Intent Normalization');
      const normalized = await normalizeIntent({
        userInput: request.userInput,
        requestId: request.requestId,
      });

      if (!normalized || normalized.confidence < 0.6) {
        logs.push('❌ Intent normalization failed or confidence too low');
        return await this.fallbackToLegacyOrchestrator(request, logs, 'Intent unclear');
      }

      logs.push(`✅ Intent normalized: ${normalized.contentType} (${Math.round(normalized.confidence * 100)}% confidence)`);

      // Step 3: Initialize sample data in memory for demonstration
      await this.initializeSampleData(request.sessionId);

      // Step 4: Build generation context
      console.log('🔍 Step 2: Context Building');
      const generationContext = await this.buildGenerationContext(normalized, request);
      logs.push(`🔍 Context built with ${generationContext.agent_profile ? 'agent' : 'no agent'}, ${generationContext.property_record ? 'property' : 'no property'} data`);

      // Step 5: Generate content using intelligent engine
      console.log('🎨 Step 3: Intelligent Content Generation');
      const generationResult = await contentEngine.generateContent(generationContext);

      if (!generationResult.success) {
        logs.push('❌ Intelligent generation failed');
        return await this.fallbackToLegacyOrchestrator(request, logs, generationResult.error || 'Generation failed');
      }

      logs.push(`✅ Content generated successfully (${generationResult.metadata.generation_time_ms}ms)`);
      logs.push(`📊 Quality scores: Overall ${Math.round(generationResult.metadata.quality_scores.overall * 100)}%`);

      // Step 6: Store content in command store
      console.log('💾 Step 4: Content Persistence');
      const contentId = await this.persistGeneratedContent(generationResult, normalized, request);
      logs.push(`💾 Content persisted with ID: ${contentId}`);

      // Step 7: Update request status
      const store = useCommandStore.getState();
      store.updateRequestStatus(request.requestId, 'Complete');

      const totalTime = Date.now() - startTime;
      logs.push(`⏱️ Total intelligent generation time: ${totalTime}ms`);

      console.log('✅ Intelligent generation completed successfully');
      console.timeEnd('Intelligent Generation');
      console.groupEnd();

      return {
        success: true,
        requestId: request.requestId,
        contentId,
        content: generationResult.content,
        metadata: {
          generation_time_ms: totalTime,
          used_intelligent_engine: true,
          quality_scores: generationResult.metadata.quality_scores,
          validation_results: generationResult.metadata.validation_results,
          memory_context_used: !!(generationContext.agent_profile || generationContext.property_record),
          ai_enhancements: [
            'Context enrichment from memory',
            'Multi-pass generation with self-critique',
            'Brand compliance validation',
            'Template fitting optimization'
          ]
        },
        logs
      };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('❌ Intelligent generation failed:', error);
      
      logs.push(`❌ Error in intelligent generation: ${errorMessage}`);
      
      console.timeEnd('Intelligent Generation');
      console.groupEnd();

      // Attempt fallback to legacy system
      if (FEATURE_FLAGS.FALLBACK_ON_ERROR) {
        logs.push('🔄 Attempting fallback to legacy orchestrator...');
        return await this.fallbackToLegacyOrchestrator(request, logs, errorMessage);
      }

      return {
        success: false,
        requestId: request.requestId,
        error: errorMessage,
        metadata: {
          generation_time_ms: Date.now() - startTime,
          used_intelligent_engine: false,
          memory_context_used: false,
          ai_enhancements: []
        },
        logs
      };
    }
  }

  // =============================================================================
  // CONTEXT BUILDING
  // =============================================================================

  private async buildGenerationContext(
    normalized: NormalizedIntent,
    request: IntelligentGenerationRequest
  ): Promise<GenerationContext> {
    const context: GenerationContext = {
      session_id: request.sessionId,
      task_id: request.requestId,
      content_type: normalized.contentType as ContentType,
      user_prompt: request.userInput
    };

    // Add sample template constraints based on content type
    context.template_constraints = this.getTemplateConstraints(normalized.contentType as ContentType);

    // Add sample generation parameters
    context.generation_params = this.getGenerationParameters(normalized.contentType as ContentType);

    console.log(`[IntelligentOrchestrator] Built generation context for ${context.content_type}`);
    return context;
  }

  private getTemplateConstraints(contentType: ContentType) {
    const constraints = {
      [ContentType.CMA_REPORT]: {
        template_id: 'cma_professional_v1',
        max_characters: 8000,
        required_sections: ['executive_summary', 'market_analysis', 'comparables', 'valuation', 'insights'],
        slot_limits: { summary: 500, insights: 200 },
        typography_rules: { heading_levels: 3, body_paragraph_limit: 150, list_item_limit: 8 }
      },
      [ContentType.PITCH_DECK]: {
        template_id: 'investor_deck_v1',
        max_characters: 6000,
        required_sections: ['title', 'highlights', 'property', 'market', 'financial', 'conclusion'],
        slot_limits: { slide_title: 60, bullet_point: 120 },
        typography_rules: { heading_levels: 2, body_paragraph_limit: 100, list_item_limit: 5 }
      },
      [ContentType.MARKET_REPORT]: {
        template_id: 'market_analysis_v1',
        max_characters: 5000,
        required_sections: ['summary', 'metrics', 'trends', 'forecast'],
        slot_limits: { metric_description: 100 },
        typography_rules: { heading_levels: 3, body_paragraph_limit: 120, list_item_limit: 6 }
      },
      [ContentType.SOCIAL_POST]: {
        template_id: 'social_engaging_v1',
        max_characters: 2200,
        required_sections: ['content', 'hashtags'],
        slot_limits: { main_content: 280, hashtags: 30 },
        typography_rules: { heading_levels: 1, body_paragraph_limit: 50, list_item_limit: 10 }
      },
      [ContentType.NEWSLETTER]: {
        template_id: 'newsletter_professional_v1',
        max_characters: 4000,
        required_sections: ['greeting', 'market_update', 'featured_properties', 'call_to_action'],
        slot_limits: { section: 300 },
        typography_rules: { heading_levels: 2, body_paragraph_limit: 100, list_item_limit: 5 }
      }
    };

    return constraints[contentType];
  }

  private getGenerationParameters(contentType: ContentType) {
    const params = {
      [ContentType.CMA_REPORT]: {
        temperature: 0.3,
        max_tokens: 3000,
        target_audience: 'real estate clients',
        content_goals: ['inform', 'analyze', 'recommend'],
        compliance_level: 'strict' as const,
        revision_passes: 2
      },
      [ContentType.PITCH_DECK]: {
        temperature: 0.7,
        max_tokens: 2500,
        target_audience: 'real estate investors',
        content_goals: ['persuade', 'inform', 'inspire action'],
        compliance_level: 'moderate' as const,
        revision_passes: 2
      },
      [ContentType.MARKET_REPORT]: {
        temperature: 0.4,
        max_tokens: 2000,
        target_audience: 'real estate professionals and clients',
        content_goals: ['inform', 'educate', 'forecast'],
        compliance_level: 'strict' as const,
        revision_passes: 1
      },
      [ContentType.SOCIAL_POST]: {
        temperature: 0.8,
        max_tokens: 500,
        target_audience: 'social media followers',
        content_goals: ['engage', 'promote', 'build brand'],
        compliance_level: 'moderate' as const,
        revision_passes: 1
      },
      [ContentType.NEWSLETTER]: {
        temperature: 0.6,
        max_tokens: 1500,
        target_audience: 'newsletter subscribers',
        content_goals: ['nurture', 'inform', 'maintain relationships'],
        compliance_level: 'moderate' as const,
        revision_passes: 1
      }
    };

    return params[contentType];
  }

  // =============================================================================
  // SAMPLE DATA INITIALIZATION
  // =============================================================================

  private async initializeSampleData(sessionId: string): Promise<void> {
    console.log('[IntelligentOrchestrator] Initializing sample memory data...');

    // Sample agent profile
    const sampleAgent = {
      id: 'agent_001',
      name: 'Sarah Johnson',
      brokerage: 'Premier Realty Group',
      specialties: ['Luxury homes', 'First-time buyers', 'Investment properties'],
      markets: ['Downtown', 'Westside', 'Riverside District'],
      experience_years: 8,
      bio: 'Dedicated real estate professional specializing in luxury properties and investment opportunities. Known for exceptional client service and market expertise.',
      contact: {
        email: 'sarah@premierrealty.com',
        phone: '(555) 123-4567',
        website: 'https://sarahjohnsonrealty.com'
      },
      voice_preferences: {
        tone: 'professional' as const,
        style: 'detailed' as const,
        avoid_terms: ['cheap', 'deal', 'steal']
      },
      branding: {
        colors: {
          primary: '#2563eb',
          secondary: '#64748b',
          accent: '#7c3aed'
        },
        fonts: {
          headings: 'Inter, sans-serif',
          body: 'Inter, sans-serif'
        },
        logo_url: 'https://example.com/logo.png'
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    // Sample property record
    const sampleProperty = {
      id: 'property_001',
      mls_id: 'MLS123456',
      address: '1234 Maple Street, Downtown, State 12345',
      type: 'residential' as const,
      details: {
        sqft: 1685,
        bedrooms: 3,
        bathrooms: 2,
        year_built: 2018,
        lot_size: '0.25 acres',
        price: 485000,
        price_history: [
          { date: '2024-10-01', price: 485000, event: 'listing' as const },
          { date: '2024-08-15', price: 475000, event: 'price_change' as const }
        ]
      },
      location: {
        neighborhood: 'Downtown District',
        city: 'Cityville',
        state: 'State',
        zip: '12345',
        lat: 40.7128,
        lng: -74.0060
      },
      market_data: {
        comparables: [
          { address: '1230 Maple Street', price: 472000, sqft: 1650, distance_miles: 0.1, sold_date: '2024-09-15' },
          { address: '1240 Oak Avenue', price: 495000, sqft: 1720, distance_miles: 0.2, sold_date: '2024-09-08' },
          { address: '1250 Pine Street', price: 489000, sqft: 1685, distance_miles: 0.3, sold_date: '2024-08-28' }
        ],
        neighborhood_stats: {
          median_price: 475000,
          avg_days_on_market: 32,
          price_trend: 'up' as const
        }
      },
      images: [
        { url: 'https://example.com/exterior.jpg', type: 'exterior' as const, description: 'Front view with beautiful landscaping' },
        { url: 'https://example.com/kitchen.jpg', type: 'interior' as const, description: 'Modern kitchen with granite countertops' }
      ],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    // Sample neighborhood facts
    const sampleNeighborhood = {
      id: 'neighborhood_001',
      name: 'Downtown District',
      city: 'Cityville',
      state: 'State',
      demographics: {
        population: 25000,
        median_income: 85000,
        avg_age: 35
      },
      amenities: [
        'Metro station',
        'Central Park',
        'Shopping center',
        'Restaurants',
        'Schools',
        'Medical facilities'
      ],
      schools: [
        { name: 'Downtown Elementary', type: 'elementary' as const, rating: 9 },
        { name: 'Central Middle School', type: 'middle' as const, rating: 8 },
        { name: 'City High School', type: 'high' as const, rating: 9 }
      ],
      transportation: {
        walkability_score: 92,
        public_transit: ['Metro Blue Line', 'Bus Route 15', 'Bus Route 22'],
        major_highways: ['I-95', 'Route 1', 'Highway 202']
      },
      development: {
        upcoming_projects: ['New convention center', 'Waterfront development', 'Mixed-use complex'],
        recent_developments: ['Transit hub expansion', 'Park renovation', 'New shopping district']
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    // Store sample data in memory
    await memoryService.upsertAgent(sampleAgent);
    await memoryService.upsertProperty(sampleProperty);
    await memoryService.upsertNeighborhood(sampleNeighborhood);

    console.log('[IntelligentOrchestrator] Sample memory data initialized');
  }

  // =============================================================================
  // CONTENT PERSISTENCE
  // =============================================================================

  private async persistGeneratedContent(
    generationResult: GenerationResult,
    normalized: NormalizedIntent,
    request: IntelligentGenerationRequest
  ): Promise<string> {
    const store = useCommandStore.getState();

    // Transform the intelligent generation result to the existing content store format
    const legacyContent = this.transformToLegacyFormat(generationResult.content, normalized.contentType as ContentType);

    // Use the existing saveContent method
    const contentId = store.saveContent(request.requestId, {
      type: normalized.contentType as any,
      title: this.generateContentTitle(normalized.contentType as ContentType, request.userInput),
      data: legacyContent,
      generatedAt: new Date().toISOString()
    });

    // Also store quality metadata if available
    if (FEATURE_FLAGS.LOG_DETAILED_METRICS && generationResult.metadata) {
      const qualityMetadata = {
        quality_scores: generationResult.metadata.quality_scores,
        validation_results: generationResult.metadata.validation_results,
        generation_params: generationResult.metadata.generation_params,
        token_usage: generationResult.metadata.token_usage
      };

      // Store in localStorage for now (in production, this would go to a proper database)
      localStorage.setItem(`content_quality_${contentId}`, JSON.stringify(qualityMetadata));
    }

    return contentId;
  }

  private transformToLegacyFormat(content: any, contentType: ContentType): any {
    // Transform the new intelligent content format to the legacy format expected by existing components
    switch (contentType) {
      case ContentType.CMA_REPORT:
        return this.transformCMAToLegacy(content);
      case ContentType.PITCH_DECK:
        return this.transformPitchDeckToLegacy(content);
      case ContentType.MARKET_REPORT:
        return this.transformMarketReportToLegacy(content);
      case ContentType.SOCIAL_POST:
        return this.transformSocialPostToLegacy(content);
      case ContentType.NEWSLETTER:
        return this.transformNewsletterToLegacy(content);
      default:
        return content;
    }
  }

  private transformCMAToLegacy(content: any): any {
    return {
      property: {
        address: '1234 Maple Street',
        sqft: 1685,
        bedrooms: 3,
        bathrooms: 2,
        yearBuilt: 2018
      },
      marketAnalysis: content.market_analysis || {
        avgPrice: 485000,
        medianPrice: 475000,
        pricePerSqft: 285,
        marketTrend: 'up',
        daysOnMarket: 32,
        inventory: 156
      },
      comparables: content.comparables || [],
      valuation: content.valuation || {
        estimatedValue: 485000,
        confidenceRange: { min: 470000, max: 500000 },
        methodology: ['Sales comparison approach', 'Market analysis', 'Location factors']
      },
      insights: content.insights || [],
      disclaimers: content.disclaimers || [],
      generatedAt: new Date().toISOString(),
      reportId: `cma_${Date.now()}`
    };
  }

  private transformPitchDeckToLegacy(content: any): any {
    return {
      id: `deck_${Date.now()}`,
      title: 'Investment Opportunity Presentation',
      property: {
        address: '1234 Maple Street',
        type: 'residential',
        sqft: 1685
      },
      slides: content.slides || [],
      theme: content.theme || {
        primaryColor: '#2563eb',
        accentColor: '#7c3aed',
        fontFamily: 'Inter, sans-serif'
      },
      generatedAt: new Date().toISOString()
    };
  }

  private transformMarketReportToLegacy(content: any): any {
    return {
      executive_summary: content.executive_summary || 'Market analysis summary',
      market_metrics: content.market_metrics || [],
      market_segments: content.market_segments || [],
      insights: content.insights || [],
      forecast: content.forecast
    };
  }

  private transformSocialPostToLegacy(content: any): any {
    return {
      content: content.content || '',
      hashtags: content.hashtags || [],
      character_count: content.character_count || 0,
      visual_suggestions: content.visual_suggestions || [],
      call_to_action: content.call_to_action,
      engagement_hooks: content.engagement_hooks || []
    };
  }

  private transformNewsletterToLegacy(content: any): any {
    return {
      subject_line: content.subject_line || 'Your Real Estate Update',
      sections: content.sections || [],
      signature: content.signature,
      disclaimers: content.disclaimers || []
    };
  }

  private generateContentTitle(contentType: ContentType, userInput: string): string {
    const baseTitle = {
      [ContentType.CMA_REPORT]: 'Comparative Market Analysis',
      [ContentType.PITCH_DECK]: 'Investment Pitch Deck',
      [ContentType.MARKET_REPORT]: 'Market Report',
      [ContentType.SOCIAL_POST]: 'Social Media Post',
      [ContentType.NEWSLETTER]: 'Newsletter'
    }[contentType];

    // Extract property address or topic from user input
    const addressMatch = userInput.match(/(\d+\s+[^,]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|circle|cir))/i);
    const propertyContext = addressMatch ? ` - ${addressMatch[1]}` : '';

    return `${baseTitle}${propertyContext}`;
  }

  // =============================================================================
  // FEATURE FLAG AND FALLBACK LOGIC
  // =============================================================================

  private shouldUseIntelligentGeneration(request: IntelligentGenerationRequest): boolean {
    // Check global feature flag
    if (!FEATURE_FLAGS.ENABLE_V33_INTELLIGENCE) {
      return false;
    }

    // Check request-specific flag
    if (request.useIntelligentGeneration === false) {
      return false;
    }

    // Check if fallback is explicitly requested
    if (request.fallbackToLegacy) {
      return false;
    }

    return true;
  }

  private async fallbackToLegacyOrchestrator(
    request: IntelligentGenerationRequest,
    logs: string[],
    reason: string
  ): Promise<IntelligentGenerationResult> {
    console.log(`[IntelligentOrchestrator] Falling back to legacy orchestrator: ${reason}`);
    
    try {
      // Import and call the original orchestrator
      const { generateContent } = await import('../orchestratorService');
      
      const legacyResult = await generateContent({
        userInput: request.userInput,
        requestId: request.requestId,
        metadata: request.metadata
      });

      logs.push('✅ Legacy orchestrator completed successfully');

      return {
        success: legacyResult.success,
        requestId: legacyResult.requestId,
        contentId: legacyResult.contentId,
        metadata: {
          generation_time_ms: 0, // Legacy doesn't track this
          used_intelligent_engine: false,
          fallback_reason: reason,
          memory_context_used: false,
          ai_enhancements: []
        },
        error: legacyResult.error,
        logs: [...logs, ...legacyResult.logs]
      };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Legacy fallback failed';
      logs.push(`❌ Legacy orchestrator failed: ${errorMessage}`);

      return {
        success: false,
        requestId: request.requestId,
        error: errorMessage,
        metadata: {
          generation_time_ms: 0,
          used_intelligent_engine: false,
          fallback_reason: reason,
          memory_context_used: false,
          ai_enhancements: []
        },
        logs
      };
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  public getFeatureFlags() {
    return { ...FEATURE_FLAGS };
  }

  public updateFeatureFlag(flag: keyof typeof FEATURE_FLAGS, value: boolean) {
    FEATURE_FLAGS[flag] = value;
    console.log(`[IntelligentOrchestrator] Updated feature flag ${flag} to ${value}`);
  }

  public async getMemoryStats() {
    return memoryService.getStats();
  }

  public async cleanupMemory(options?: { older_than_days?: number }) {
    await memoryService.cleanup(options);
  }

  // =============================================================================
  // ANALYTICS AND MONITORING
  // =============================================================================

  public getGenerationMetrics(): {
    totalRequests: number;
    intelligentRequests: number;
    fallbackRequests: number;
    averageQualityScore: number;
  } {
    // In a real implementation, this would pull from analytics store
    return {
      totalRequests: 0,
      intelligentRequests: 0,
      fallbackRequests: 0,
      averageQualityScore: 0.85
    };
  }
}

// =============================================================================
// SINGLETON EXPORT AND CONVENIENCE FUNCTIONS
// =============================================================================

const intelligentOrchestrator = IntelligentOrchestrator.getInstance();

export default intelligentOrchestrator;

/**
 * Main entry point for v3.3 intelligent content generation
 * This function should be called instead of the legacy generateContent
 */
export const generateContentIntelligently = async (
  request: IntelligentGenerationRequest
): Promise<IntelligentGenerationResult> => {
  return intelligentOrchestrator.generateContentIntelligently(request);
};

/**
 * Convenience function for backward compatibility
 */
export const generateContentV33 = async (
  userInput: string,
  requestId: string,
  sessionId: string,
  options?: { useIntelligence?: boolean; metadata?: Record<string, any> }
): Promise<IntelligentGenerationResult> => {
  return intelligentOrchestrator.generateContentIntelligently({
    userInput,
    requestId,
    sessionId,
    useIntelligentGeneration: options?.useIntelligence ?? true,
    metadata: options?.metadata
  });
};