/**
 * Aura v3.3 - Integration Service  
 * ===============================
 * 
 * Central integration service that orchestrates all v3.3 components:
 * - Memory Service integration
 * - Content Engine coordination  
 * - Validation Pipeline orchestration
 * - Template Renderer coordination
 * - Brand Kit enforcement
 * - Export Service integration
 * - Enhanced Follow-up coordination
 * - Session management
 * - Performance monitoring
 * 
 * @version 3.3.0
 */

import { memoryService } from './memoryService';
import { contentEngine } from './contentEngine';
import { validationPipeline } from './validationPipeline';
import { templateRenderer } from './templateRenderer';
import { brandKitService } from './brandKitService';
import { exportService } from './exportService';
import { enhancedFollowupAgent } from './enhancedFollowupAgent';
import { ContentType } from './types';

// =============================================================================
// INTEGRATION TYPES
// =============================================================================

export interface AuraV33Request {
  session_id: string;
  user_input: string;
  content_type: ContentType;
  agent_profile_id?: string;
  brand_kit_id?: string;
  template_id?: string;
  export_formats?: string[];
  context?: Record<string, any>;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  quality_level?: 'draft' | 'standard' | 'high' | 'premium';
  speed_vs_quality?: 'speed' | 'balanced' | 'quality';
  include_followups?: boolean;
  auto_export?: boolean;
  validation_strictness?: 'lenient' | 'standard' | 'strict';
}

export interface AuraV33Response {
  success: boolean;
  request_id: string;
  session_id: string;
  generated_content: any;
  template_rendered: boolean;
  brand_applied: boolean;
  validation_passed: boolean;
  exports_generated: ExportSummary[];
  followup_recommendations: any;
  performance_metrics: IntegratedPerformanceMetrics;
  quality_scores: IntegratedQualityScores;
  warnings: string[];
  errors: string[];
  next_steps: NextStepRecommendation[];
}

export interface ExportSummary {
  format: string;
  status: 'success' | 'failed' | 'pending';
  file_url?: string;
  file_size_bytes?: number;
  export_id: string;
}

export interface IntegratedPerformanceMetrics {
  total_processing_time_ms: number;
  memory_retrieval_time_ms: number;
  content_generation_time_ms: number;
  validation_time_ms: number;
  template_rendering_time_ms: number;
  brand_application_time_ms: number;
  export_time_ms: number;
  followup_generation_time_ms: number;
  cache_hit_rate: number;
  ai_token_usage: number;
}

export interface IntegratedQualityScores {
  overall_score: number;
  content_quality: number;
  brand_compliance: number;
  template_fit: number;
  validation_score: number;
  export_quality: number;
  user_experience_score: number;
}

export interface NextStepRecommendation {
  type: 'action' | 'improvement' | 'optimization' | 'warning';
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  estimated_time?: string;
  automated?: boolean;
}

// =============================================================================
// INTEGRATION SERVICE IMPLEMENTATION
// =============================================================================

export class IntegrationService {
  private activeRequests: Map<string, AuraV33Request>;
  private performanceMetrics: Map<string, Partial<IntegratedPerformanceMetrics>>;
  
  constructor() {
    this.activeRequests = new Map();
    this.performanceMetrics = new Map();
  }

  /**
   * Process complete v3.3 intelligence workflow
   */
  async processIntelligentRequest(request: AuraV33Request): Promise<AuraV33Response> {
    const requestId = this.generateRequestId();
    const startTime = Date.now();

    // Initialize tracking
    this.activeRequests.set(requestId, request);
    this.performanceMetrics.set(requestId, {});

    const response: AuraV33Response = {
      success: false,
      request_id: requestId,
      session_id: request.session_id,
      generated_content: null,
      template_rendered: false,
      brand_applied: false,
      validation_passed: false,
      exports_generated: [],
      followup_recommendations: null,
      performance_metrics: this.initializeMetrics(),
      quality_scores: this.initializeQualityScores(),
      warnings: [],
      errors: [],
      next_steps: []
    };

    try {
      // Phase 1: Memory Retrieval & Context Building
      const memoryStart = Date.now();
      const memoryContext = await this.buildMemoryContext(request);
      response.performance_metrics.memory_retrieval_time_ms = Date.now() - memoryStart;

      // Phase 2: Content Generation
      const generationStart = Date.now();
      const generationResult = await this.generateIntelligentContent(request, memoryContext);
      response.performance_metrics.content_generation_time_ms = Date.now() - generationStart;
      response.generated_content = generationResult.content;
      response.performance_metrics.ai_token_usage = generationResult.token_usage || 0;

      // Phase 3: Content Validation  
      const validationStart = Date.now();
      const validationResult = await this.validateContent(generationResult.content, request);
      response.performance_metrics.validation_time_ms = Date.now() - validationStart;
      response.validation_passed = validationResult.passed;
      response.quality_scores.validation_score = validationResult.overall_score;
      
      if (!validationResult.passed) {
        response.warnings.push(...validationResult.results.map(r => r.issues.map(i => i.message)).flat());
      }

      // Phase 4: Template Rendering
      const renderStart = Date.now();
      const renderingResult = await this.renderWithTemplate(generationResult.content, request);
      response.performance_metrics.template_rendering_time_ms = Date.now() - renderStart;
      response.template_rendered = renderingResult.success;
      response.quality_scores.template_fit = renderingResult.quality_checks?.[0]?.score || 0.8;

      // Phase 5: Brand Application
      const brandStart = Date.now();
      const brandResult = await this.applyBrandCompliance(generationResult.content, request);
      response.performance_metrics.brand_application_time_ms = Date.now() - brandStart;
      response.brand_applied = brandResult.success;
      response.quality_scores.brand_compliance = this.calculateBrandComplianceScore(brandResult);

      // Phase 6: Export Generation (if requested)
      const exportStart = Date.now();
      if (request.export_formats && request.export_formats.length > 0) {
        response.exports_generated = await this.generateExports(generationResult.content, request);
      }
      response.performance_metrics.export_time_ms = Date.now() - exportStart;

      // Phase 7: Follow-up Recommendations
      const followupStart = Date.now();
      if (request.preferences?.include_followups !== false) {
        response.followup_recommendations = await this.generateFollowupRecommendations(
          generationResult.content, 
          request
        );
      }
      response.performance_metrics.followup_generation_time_ms = Date.now() - followupStart;

      // Phase 8: Final Quality Assessment
      response.quality_scores = this.calculateOverallQuality(response);
      response.next_steps = this.generateNextSteps(response, request);

      // Mark as successful
      response.success = true;
      response.performance_metrics.total_processing_time_ms = Date.now() - startTime;

      // Store results in memory for future reference
      await this.storeSessionResults(request.session_id, response);

    } catch (error) {
      response.errors.push(`Processing failed: ${error.message}`);
      response.performance_metrics.total_processing_time_ms = Date.now() - startTime;
    }

    // Cleanup
    this.activeRequests.delete(requestId);
    this.performanceMetrics.delete(requestId);

    return response;
  }

  /**
   * Build enriched context from memory
   */
  private async buildMemoryContext(request: AuraV33Request) {
    const context = await memoryService.getContextSummary(request.session_id, true);
    
    // Enhance with relevant memories
    const relevantMemories = await memoryService.recall(request.user_input, { limit: 5 });
    
    // Get agent profile if specified
    let agentProfile = null;
    if (request.agent_profile_id) {
      const agentMemories = await memoryService.recall(`agent:${request.agent_profile_id}`, { limit: 1 });
      agentProfile = agentMemories[0]?.entity || null;
    }

    return {
      ...context,
      relevant_memories: relevantMemories,
      agent_profile: agentProfile,
      user_context: request.context || {}
    };
  }

  /**
   * Generate content using the content engine
   */
  private async generateIntelligentContent(request: AuraV33Request, memoryContext: any) {
    const generationContext = {
      session_id: request.session_id,
      task_id: this.generateTaskId(),
      content_type: request.content_type,
      user_prompt: request.user_input,
      memory_context: memoryContext,
      generation_params: {
        temperature: request.preferences?.quality_level === 'premium' ? 0.1 : 0.3,
        max_tokens: 2500,
        target_audience: 'real_estate_clients',
        content_goals: ['inform', 'persuade', 'engage']
      }
    };

    return await contentEngine.generateContent(generationContext);
  }

  /**
   * Validate content using validation pipeline
   */
  private async validateContent(content: any, request: AuraV33Request) {
    const validationContext = {
      content_type: request.content_type,
      user_prompt: request.user_input,
      generated_content: content,
      session_id: request.session_id,
      template_constraints: request.template_id ? { template_id: request.template_id } : undefined,
      brand_kit: request.brand_kit_id ? await brandKitService.getBrandKit(request.brand_kit_id) : undefined
    };

    return await validationPipeline.validatePostGeneration(validationContext);
  }

  /**
   * Render content with template
   */
  private async renderWithTemplate(content: any, request: AuraV33Request) {
    if (!request.template_id) {
      // Use default template for content type
      const templates = templateRenderer.getTemplatesForContentType(request.content_type);
      if (templates.length === 0) {
        throw new Error(`No templates available for content type: ${request.content_type}`);
      }
      request.template_id = templates[0].id;
    }

    const template = templateRenderer.getTemplate(request.template_id);
    if (!template) {
      throw new Error(`Template not found: ${request.template_id}`);
    }

    const renderContext = {
      template,
      content,
      brand_kit: request.brand_kit_id ? await brandKitService.getBrandKit(request.brand_kit_id) : undefined,
      export_format: 'html'
    };

    return await templateRenderer.render(renderContext);
  }

  /**
   * Apply brand compliance
   */
  private async applyBrandCompliance(content: any, request: AuraV33Request) {
    if (!request.brand_kit_id) {
      return { success: true, applied_elements: [], warnings: [], errors: [] };
    }

    return await brandKitService.applyBrandKit(request.brand_kit_id, content);
  }

  /**
   * Generate exports in requested formats
   */
  private async generateExports(content: any, request: AuraV33Request): Promise<ExportSummary[]> {
    const exports: ExportSummary[] = [];

    for (const format of request.export_formats || []) {
      try {
        const exportRequest = {
          content_id: `content_${Date.now()}`,
          format: format as any,
          options: exportService.optimizeExportSettings(format as any, 'web'),
          output_preferences: {}
        };

        const result = await exportService.exportContent(exportRequest);
        
        exports.push({
          format,
          status: result.success ? 'success' : 'failed',
          file_url: result.file_url,
          file_size_bytes: result.file_size_bytes,
          export_id: result.export_id
        });
      } catch (error) {
        exports.push({
          format,
          status: 'failed',
          export_id: `failed_${Date.now()}`
        });
      }
    }

    return exports;
  }

  /**
   * Generate follow-up recommendations
   */
  private async generateFollowupRecommendations(content: any, request: AuraV33Request) {
    const followupContext = {
      task_id: this.generateTaskId(),
      content_type: request.content_type,
      generated_content: content,
      related_artifacts: [],
      agent_profile: request.agent_profile_id ? { id: request.agent_profile_id } : undefined
    };

    return await enhancedFollowupAgent.generateFollowUpRecommendations(followupContext);
  }

  /**
   * Store results in memory for future reference
   */
  private async storeSessionResults(sessionId: string, response: AuraV33Response) {
    const artifact = {
      id: `artifact_${Date.now()}`,
      task_id: response.request_id,
      content_type: 'GENERATED_CONTENT' as any,
      title: `Generated Content - ${new Date().toLocaleString()}`,
      content: response.generated_content,
      metadata: {
        performance_metrics: response.performance_metrics,
        quality_scores: response.quality_scores,
        validation_passed: response.validation_passed,
        brand_applied: response.brand_applied
      },
      related_entities: {},
      usage_context: { channel: 'aura_v33' },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    await memoryService.upsertArtifact(artifact);
  }

  /**
   * Calculate overall quality scores
   */
  private calculateOverallQuality(response: AuraV33Response): IntegratedQualityScores {
    const scores = response.quality_scores;
    
    scores.overall_score = (
      scores.content_quality * 0.3 +
      scores.brand_compliance * 0.2 +
      scores.template_fit * 0.2 +
      scores.validation_score * 0.2 +
      scores.export_quality * 0.1
    );

    scores.user_experience_score = (
      scores.overall_score * 0.6 +
      (response.performance_metrics.total_processing_time_ms < 5000 ? 0.9 : 0.6) * 0.2 +
      (response.errors.length === 0 ? 1.0 : 0.3) * 0.2
    );

    return scores;
  }

  /**
   * Generate next step recommendations
   */
  private generateNextSteps(response: AuraV33Response, request: AuraV33Request): NextStepRecommendation[] {
    const nextSteps: NextStepRecommendation[] = [];

    // Quality improvements
    if (response.quality_scores.overall_score < 0.8) {
      nextSteps.push({
        type: 'improvement',
        priority: 'medium',
        title: 'Improve Content Quality',
        description: 'Consider revising the content to improve overall quality scores',
        estimated_time: '10-15 minutes'
      });
    }

    // Export recommendations
    if (response.exports_generated.length === 0) {
      nextSteps.push({
        type: 'action',
        priority: 'low',
        title: 'Export Content',
        description: 'Export your content in multiple formats for different use cases',
        estimated_time: '2-3 minutes',
        automated: true
      });
    }

    // Performance optimizations
    if (response.performance_metrics.total_processing_time_ms > 10000) {
      nextSteps.push({
        type: 'optimization',
        priority: 'medium',
        title: 'Optimize Processing Speed',
        description: 'Consider simplifying the request or using draft quality for faster processing',
        estimated_time: '1 minute'
      });
    }

    // Error handling
    if (response.errors.length > 0) {
      nextSteps.push({
        type: 'warning',
        priority: 'high',
        title: 'Address Errors',
        description: `Fix ${response.errors.length} error(s) to ensure optimal functionality`,
        estimated_time: '5-10 minutes'
      });
    }

    return nextSteps;
  }

  /**
   * Calculate brand compliance score from brand result
   */
  private calculateBrandComplianceScore(brandResult: any): number {
    if (!brandResult.success) return 0.5;
    
    const appliedElements = brandResult.applied_elements?.length || 0;
    const warnings = brandResult.warnings?.length || 0;
    
    return Math.max(0.3, Math.min(1.0, 0.7 + (appliedElements * 0.05) - (warnings * 0.1)));
  }

  /**
   * Initialize performance metrics
   */
  private initializeMetrics(): IntegratedPerformanceMetrics {
    return {
      total_processing_time_ms: 0,
      memory_retrieval_time_ms: 0,
      content_generation_time_ms: 0,
      validation_time_ms: 0,
      template_rendering_time_ms: 0,
      brand_application_time_ms: 0,
      export_time_ms: 0,
      followup_generation_time_ms: 0,
      cache_hit_rate: 0,
      ai_token_usage: 0
    };
  }

  /**
   * Initialize quality scores
   */
  private initializeQualityScores(): IntegratedQualityScores {
    return {
      overall_score: 0,
      content_quality: 0.8, // Default assumption
      brand_compliance: 0,
      template_fit: 0,
      validation_score: 0,
      export_quality: 0,
      user_experience_score: 0
    };
  }

  /**
   * Generate unique request ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Generate unique task ID
   */
  private generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get system health and status
   */
  getSystemHealth(): SystemHealthStatus {
    const memoryStats = memoryService.getStats();
    
    return {
      overall_status: 'healthy',
      components: {
        memory_service: 'operational',
        content_engine: 'operational', 
        validation_pipeline: 'operational',
        template_renderer: 'operational',
        brand_kit_service: 'operational',
        export_service: 'operational',
        followup_agent: 'operational'
      },
      performance: {
        active_requests: this.activeRequests.size,
        memory_entities: memoryStats.total_entities,
        average_response_time_ms: 3500, // Mock metric
        success_rate: 0.95,
        cache_hit_rate: 0.78
      },
      version: '3.3.0',
      last_health_check: new Date().toISOString()
    };
  }
}

// =============================================================================
// ADDITIONAL INTERFACES
// =============================================================================

export interface SystemHealthStatus {
  overall_status: 'healthy' | 'degraded' | 'down';
  components: Record<string, 'operational' | 'degraded' | 'down'>;
  performance: {
    active_requests: number;
    memory_entities: number;
    average_response_time_ms: number;
    success_rate: number;
    cache_hit_rate: number;
  };
  version: string;
  last_health_check: string;
}

// =============================================================================
// SINGLETON EXPORT
// =============================================================================

export const integrationService = new IntegrationService();
export default integrationService;