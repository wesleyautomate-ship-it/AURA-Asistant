/**
 * Integration Hub v3.3
 * =====================
 * 
 * Central bridge between the v3.3 Intelligence Layer and existing
 * v3.2 orchestrator infrastructure. Provides backward compatibility
 * while enabling intelligent features.
 * 
 * Integrates with: orchestratorService.ts, contentIntelligence.ts, memoryService.ts
 */

import { GenerationRequest, GenerationResult } from '../orchestratorService';
import { contentIntelligence, IntelligentRequest } from './contentIntelligence';
import { memoryService } from './memoryService';
import { useCommandStore } from '../../store/commandStore';

export interface IntelligentGenerationRequest extends GenerationRequest {
  enable_intelligence?: boolean;
  memory_enhanced?: boolean;
  quality_threshold?: number;
  brand_kit_id?: string;
}

export interface IntelligentGenerationResult extends GenerationResult {
  intelligence_used?: boolean;
  quality_scores?: {
    overall_score: number;
    content_quality: number;
    brand_compliance: number;
    validation_score: number;
  };
  recommendations?: string[];
  memory_context_used?: boolean;
}

class IntegrationHub {
  private static instance: IntegrationHub;
  
  public static getInstance(): IntegrationHub {
    if (!IntegrationHub.instance) {
      IntegrationHub.instance = new IntegrationHub();
    }
    return IntegrationHub.instance;
  }

  /**
   * Process request with optional intelligence enhancement
   */
  async processIntelligentRequest(request: IntelligentGenerationRequest): Promise<IntelligentGenerationResult> {
    const logs: string[] = [];
    const startTime = Date.now();
    
    console.group(`🔗 [Integration Hub] Processing Request`);
    console.log('Intelligence Enabled:', request.enable_intelligence !== false);
    console.log('Memory Enhanced:', request.memory_enhanced !== false);
    console.log('Request ID:', request.requestId);
    
    try {
      // Determine if we should use intelligence features
      const useIntelligence = this.shouldUseIntelligence(request);
      
      if (useIntelligence) {
        logs.push('🧠 Using v3.3 Intelligence Layer');
        return await this.processWithIntelligence(request, logs);
      } else {
        logs.push('🔄 Using v3.2 Stable Orchestrator');
        return await this.processWithStandardOrchestrator(request, logs);
      }
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      logs.push(`❌ Integration Hub failed: ${errorMessage}`);
      
      console.error('❌ Integration Hub failed:', error);
      console.groupEnd();
      
      return {
        success: false,
        requestId: request.requestId,
        error: errorMessage,
        logs,
        intelligence_used: false
      };
    }
  }

  /**
   * Process with full v3.3 intelligence features
   */
  private async processWithIntelligence(
    request: IntelligentGenerationRequest, 
    logs: string[]
  ): Promise<IntelligentGenerationResult> {
    
    // Step 1: Prepare intelligent request
    const intelligentRequest: IntelligentRequest = {
      user_input: request.userInput,
      session_id: request.requestId,
      quality_requirements: {
        min_score: request.quality_threshold || 0.8,
        brand_consistency: true,
        compliance_checks: ['readability', 'brand', 'compliance']
      }
    };

    // Step 2: Build memory context if enabled
    if (request.memory_enhanced !== false) {
      logs.push('🔍 Building enhanced memory context');
      intelligentRequest.memory_context = await memoryService.buildContext(
        request.userInput, 
        request.requestId
      );
    }

    // Step 3: Process with content intelligence
    logs.push('⚡ Processing with content intelligence');
    const intelligentResult = await contentIntelligence.generateIntelligentContent(intelligentRequest);

    // Step 4: Convert to standard result format
    const totalTime = Date.now() - Date.now();
    logs.push(...intelligentResult.processing_log);
    logs.push(`⏱️ Intelligence processing: ${totalTime}ms`);

    console.log('✅ Intelligence processing completed');
    console.groupEnd();

    return {
      success: intelligentResult.success,
      requestId: request.requestId,
      contentId: intelligentResult.generated_content?.id || `intel_${request.requestId}`,
      error: intelligentResult.error,
      logs,
      intelligence_used: true,
      quality_scores: intelligentResult.quality_scores,
      recommendations: intelligentResult.recommendations,
      memory_context_used: !!intelligentResult.memory_context
    };
  }

  /**
   * Process with standard v3.2 orchestrator (fallback/compatibility)
   */
  private async processWithStandardOrchestrator(
    request: IntelligentGenerationRequest, 
    logs: string[]
  ): Promise<IntelligentGenerationResult> {
    
    // Import and use existing orchestratorService
    const { generateContent } = await import('../orchestratorService');
    
    logs.push('🔄 Using standard orchestration pipeline');
    const result = await generateContent({
      userInput: request.userInput,
      requestId: request.requestId,
      metadata: request.metadata
    });

    // Enhance standard result with basic intelligence features
    logs.push(...result.logs);

    console.log(`${result.success ? '✅' : '❌'} Standard orchestration completed`);
    console.groupEnd();

    return {
      ...result,
      intelligence_used: false,
      quality_scores: this.generateBasicQualityScores(result),
      recommendations: this.generateBasicRecommendations(result),
      memory_context_used: false
    };
  }

  /**
   * Determine if intelligence features should be used
   */
  private shouldUseIntelligence(request: IntelligentGenerationRequest): boolean {
    // Check feature flags
    if (request.enable_intelligence === false) {
      return false;
    }

    // Check if intelligence features are available
    if (!contentIntelligence || !memoryService) {
      console.warn('Intelligence services not available, falling back to standard');
      return false;
    }

    // Check environment flag
    const intelligenceEnabled = import.meta.env.VITE_INTELLIGENCE_ENABLED !== 'false';
    if (!intelligenceEnabled) {
      console.log('Intelligence disabled via environment variable');
      return false;
    }

    // Use intelligence by default
    return true;
  }

  /**
   * Generate basic quality scores for standard orchestration
   */
  private generateBasicQualityScores(result: GenerationResult) {
    return {
      overall_score: result.success ? 0.8 : 0.4,
      content_quality: result.success ? 0.75 : 0.4,
      brand_compliance: 0.8, // Assume reasonable brand compliance
      validation_score: result.success ? 0.85 : 0.3
    };
  }

  /**
   * Generate basic recommendations for standard orchestration
   */
  private generateBasicRecommendations(result: GenerationResult): string[] {
    const recommendations: string[] = [];

    if (!result.success) {
      recommendations.push('Consider enabling intelligence features for better results');
      recommendations.push('Review input parameters and try again');
    } else {
      recommendations.push('Consider upgrading to v3.3 Intelligence for enhanced quality');
      recommendations.push('Enable memory context for personalized content');
    }

    return recommendations;
  }

  /**
   * Initialize sample memory data for demonstration
   */
  async initializeSampleData(): Promise<void> {
    console.log('🌱 Initializing sample memory data');
    
    // Sample agent profile
    await memoryService.upsertAgent({
      id: 'sample_agent',
      name: 'Sarah Johnson',
      specialties: ['Luxury Properties', 'Commercial Real Estate'],
      voice_preferences: {
        tone: 'professional',
        style: 'informative and engaging'
      },
      brand_preferences: {
        colors: ['#1a365d', '#2d3748', '#4a5568'],
        fonts: ['Inter', 'Georgia'],
        logo_url: '/assets/logo-sample.png'
      }
    });

    // Sample property records
    await memoryService.upsertProperty({
      id: 'prop_downtown',
      address: 'Downtown Dubai Business District',
      property_type: 'commercial',
      market_data: {
        current_price: 2500000,
        estimated_value: 2650000,
        market_trends: ['Rising demand', 'Premium location', 'Growing investment interest']
      }
    });

    await memoryService.upsertProperty({
      id: 'prop_marina',
      address: 'Dubai Marina Luxury Towers',
      property_type: 'apartment',
      market_data: {
        current_price: 1800000,
        estimated_value: 1900000,
        market_trends: ['Waterfront premium', 'High rental yield', 'Tourist destination']
      }
    });

    console.log('✅ Sample memory data initialized');
  }

  /**
   * Get system health status
   */
  getSystemHealth() {
    return {
      intelligence_available: !!contentIntelligence,
      memory_available: !!memoryService,
      standard_orchestrator_available: true,
      feature_flags: {
        intelligence_enabled: import.meta.env.VITE_INTELLIGENCE_ENABLED !== 'false',
        memory_enhanced: import.meta.env.VITE_MEMORY_ENHANCED !== 'false',
        backend_enabled: import.meta.env.VITE_BACKEND_ENABLED !== 'false'
      }
    };
  }
}

// Export singleton instance
export const integrationHub = IntegrationHub.getInstance();

// Export the main processing function for easy importing
export const processIntelligentRequest = integrationHub.processIntelligentRequest.bind(integrationHub);