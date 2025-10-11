/**
 * Aura Template Orchestrator v3.1
 * 
 * Central decision engine that connects "intent" → "template" → "generation logic"
 * Maps user commands to appropriate content generation workflows and visual templates
 * 
 * Features:
 * ✅ Intent-to-template mapping with metadata enrichment
 * ✅ Support for CMA, PITCH_DECK, and SOCIAL_POST content types
 * ✅ Structured output with consistent visual hierarchy
 * ✅ Integration with existing contextEnrichment service
 * ✅ File-based output support (PDF, slides, markdown)
 */

import { Intent } from './intentParser';
import { enrichWorkflowPayload } from './contextEnrichment';
import { useCommandStore } from '../store/commandStore';

// Content generation types
export type ContentType = 'CMA_REPORT' | 'PITCH_DECK' | 'SOCIAL_POST' | 'MARKET_REPORT';
export type LegacyContentType = 'CMA' | 'PITCH_DECK' | 'SOCIAL_POST' | 'MARKET_REPORT';

// Template configuration for each content type
export interface TemplateConfig {
  type: ContentType;
  endpoint: string;
  outputFormats: ('pdf' | 'html' | 'json' | 'markdown')[];
  visualTemplate: string;
  requiredFields: string[];
  optionalFields: string[];
  brandingProfile: {
    tone: 'professional' | 'conversational' | 'analytical';
    hierarchy: string[];
    colorScheme: string;
  };
}

// Generated content structure
export interface GeneratedContent {
  id: string;
  type: ContentType;
  title: string;
  createdAt: number;
  metadata: {
    location?: string;
    audience?: string;
    propertyType?: string;
    generationContext: 'voice' | 'text';
    originalPrompt: string;
  };
  content: {
    structured: Record<string, any>; // JSON representation
    formatted?: string; // HTML/Markdown for preview
    exportUrl?: string; // PDF/file download URL
  };
  status: 'generating' | 'ready' | 'error';
  error?: string;
}

// Template orchestration result
export interface TemplateOrchestrationResult {
  success: boolean;
  contentId?: string;
  content?: GeneratedContent;
  error?: string;
  fallbackToStream?: boolean;
  userMessage?: string;
}

// Template configurations
const TEMPLATE_CONFIGS: Record<ContentType, TemplateConfig> = {
  CMA_REPORT: {
    type: 'CMA_REPORT',
    endpoint: '/api/v1/cma/generate',
    outputFormats: ['pdf', 'html', 'json'],
    visualTemplate: 'newsletter_style', // Clean, professional layout
    requiredFields: ['location'],
    optionalFields: ['property_type', 'date_range', 'comparable_count'],
    brandingProfile: {
      tone: 'professional',
      hierarchy: ['executive_summary', 'market_overview', 'comparables', 'insights', 'recommendations'],
      colorScheme: 'neutral_professional'
    }
  },
  PITCH_DECK: {
    type: 'PITCH_DECK',
    endpoint: '/api/v1/decks/generate',
    outputFormats: ['pdf', 'json', 'html'],
    visualTemplate: 'investor_deck_style', // Slide-based layout
    requiredFields: ['location', 'property_type'],
    optionalFields: ['investment_amount', 'target_audience', 'timeline'],
    brandingProfile: {
      tone: 'professional',
      hierarchy: ['overview', 'market_opportunity', 'financial_highlights', 'value_proposition', 'next_steps'],
      colorScheme: 'brand_primary'
    }
  },
  SOCIAL_POST: {
    type: 'SOCIAL_POST',
    endpoint: '/api/v1/social/generate',
    outputFormats: ['json', 'html', 'markdown'],
    visualTemplate: 'social_media_style', // Engaging, visual layout
    requiredFields: ['topic', 'platform'],
    optionalFields: ['audience', 'hashtags', 'call_to_action'],
    brandingProfile: {
      tone: 'conversational',
      hierarchy: ['hook', 'content', 'call_to_action'],
      colorScheme: 'brand_vibrant'
    }
  },
  MARKET_REPORT: {
    type: 'MARKET_REPORT',
    endpoint: '/api/v1/market/generate',
    outputFormats: ['pdf', 'html', 'json'],
    visualTemplate: 'analytical_report_style', // Data-focused layout
    requiredFields: ['location'],
    optionalFields: ['time_period', 'property_types', 'metrics'],
    brandingProfile: {
      tone: 'analytical',
      hierarchy: ['executive_summary', 'market_trends', 'data_analysis', 'forecasts', 'conclusions'],
      colorScheme: 'data_visualization'
    }
  }
};

/**
 * Template Orchestrator Service
 */
export class TemplateOrchestrator {
  private generationQueue: Map<string, GeneratedContent> = new Map();

  /**
   * Orchestrate content generation from intent to deliverable
   */
  async orchestrateContentGeneration(
    intent: Intent,
    recentTasks: any[] = [],
    contextHistory: string[] = [],
    originalPrompt: string = ''
  ): Promise<TemplateOrchestrationResult> {
    console.group('[TemplateOrchestrator] Starting content generation');
    console.log('Intent:', intent);
    console.log('Original prompt:', originalPrompt);

    try {
      // Step 1: Map intent to content type
      const contentType = this.mapIntentToContentType(intent);
      if (!contentType) {
        console.log('❌ No content type mapping found for intent');
        console.groupEnd();
        return {
          success: false,
          error: 'Unable to determine content type from intent',
          fallbackToStream: true,
          userMessage: "I'll help you with that through a conversation instead."
        };
      }

      console.log(`📋 Mapped to content type: ${contentType}`);

      // Step 2: Get template configuration
      const templateConfig = TEMPLATE_CONFIGS[contentType];
      
      // Step 3: Enrich context using existing enrichment service
      const enrichedPayload = await enrichWorkflowPayload(
        intent, // Use original intent for enrichment
        recentTasks,
        contextHistory,
        originalPrompt
      );

      if (!enrichedPayload.canProceed) {
        console.log('❌ Context enrichment failed:', enrichedPayload.fallbackReason);
        console.groupEnd();
        return {
          success: false,
          error: enrichedPayload.fallbackReason,
          fallbackToStream: true,
          userMessage: `I need more information to generate your ${contentType.toLowerCase().replace('_', ' ')}. Let me help you through a conversation.`
        };
      }

      // Step 4: Create content generation request
      const contentId = this.generateContentId(contentType);
      const generatedContent: GeneratedContent = {
        id: contentId,
        type: contentType,
        title: this.generateContentTitle(contentType, enrichedPayload.enrichedFields),
        createdAt: Date.now(),
        metadata: {
          location: enrichedPayload.enrichedFields.location,
          audience: enrichedPayload.enrichedFields.audience,
          propertyType: enrichedPayload.enrichedFields.property_type,
          generationContext: originalPrompt.length > 0 ? 'text' : 'voice',
          originalPrompt
        },
        content: {
          structured: enrichedPayload.enrichedFields,
          formatted: undefined, // Will be populated by backend
          exportUrl: undefined // Will be populated by backend
        },
        status: 'generating'
      };

      // Step 5: Store in generation queue
      this.generationQueue.set(contentId, generatedContent);

      // Step 6: Trigger backend generation (simulate API call for now)
      const generationResult = await this.callGenerationAPI(
        templateConfig,
        enrichedPayload.enrichedFields,
        contentId
      );

      if (generationResult.success) {
        // Update content with results
        generatedContent.status = 'ready';
        generatedContent.content = {
          ...generatedContent.content,
          ...generationResult.content
        };
        this.generationQueue.set(contentId, generatedContent);

        console.log('✅ Content generation completed successfully');
        console.groupEnd();
        
        return {
          success: true,
          contentId,
          content: generatedContent
        };
      } else {
        // Handle generation failure
        generatedContent.status = 'error';
        generatedContent.error = generationResult.error;
        this.generationQueue.set(contentId, generatedContent);

        console.log('❌ Content generation failed:', generationResult.error);
        console.groupEnd();

        return {
          success: false,
          error: generationResult.error,
          fallbackToStream: true,
          userMessage: `I encountered an issue generating your ${contentType.toLowerCase().replace('_', ' ')}. Let me help you through a conversation instead.`
        };
      }

    } catch (error) {
      console.error('💥 Template orchestration error:', error);
      console.groupEnd();

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        fallbackToStream: true,
        userMessage: "I encountered an issue generating your content. Let me help you through a conversation instead."
      };
    }
  }

  /**
   * Get generated content by ID
   */
  getGeneratedContent(contentId: string): GeneratedContent | undefined {
    return this.generationQueue.get(contentId);
  }

  /**
   * List all generated content
   */
  listGeneratedContent(): GeneratedContent[] {
    return Array.from(this.generationQueue.values()).sort((a, b) => b.createdAt - a.createdAt);
  }

  /**
   * Get template configuration for content type
   */
  getTemplateConfig(contentType: ContentType): TemplateConfig {
    return TEMPLATE_CONFIGS[contentType];
  }

  /**
   * Save generated content to commandStore
   * This method should be called from components that have access to the store
   */
  saveToCommandStore(
    taskId: string, 
    content: GeneratedContent,
    saveGeneratedContent: (content: any) => string
  ): void {
    try {
      // Transform the templateOrchestrator format to commandStore format
      const storeContent = {
        taskId,
        type: content.type,
        title: content.title,
        data: content.content.structured,
        updatedAt: new Date().toISOString()
      };
      
      const savedId = saveGeneratedContent(storeContent);
      console.log(`[TemplateOrchestrator] Saved content to store with ID: ${savedId}`);
    } catch (error) {
      console.error('[TemplateOrchestrator] Failed to save to store:', error);
    }
  }

  // Private helper methods

  private mapIntentToContentType(intent: Intent): ContentType | null {
    // Map intent types to content types
    switch (intent.type) {
      case 'CMA':
        return 'CMA_REPORT';
      case 'MARKET_REPORT':
        return 'MARKET_REPORT';
      case 'SOCIAL_POST':
        return 'SOCIAL_POST';
      default:
        // Check for pitch deck keywords in topic or additional context
        if (intent.topic && (
          intent.topic.toLowerCase().includes('pitch') ||
          intent.topic.toLowerCase().includes('deck') ||
          intent.topic.toLowerCase().includes('investor') ||
          intent.topic.toLowerCase().includes('presentation')
        )) {
          return 'PITCH_DECK';
        }
        return null;
    }
  }

  private generateContentId(contentType: ContentType): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    return `${contentType.toLowerCase()}_${timestamp}_${random}`;
  }

  private generateContentTitle(contentType: ContentType, fields: Record<string, any>): string {
    const location = fields.location || 'Property';
    const timestamp = new Date().toLocaleDateString();

    switch (contentType) {
      case 'CMA_REPORT':
        return `CMA Report - ${location} (${timestamp})`;
      case 'PITCH_DECK':
        return `Investor Pitch Deck - ${location} (${timestamp})`;
      case 'SOCIAL_POST':
        return `Social Media Content - ${fields.topic || location} (${timestamp})`;
      case 'MARKET_REPORT':
        return `Market Analysis - ${location} (${timestamp})`;
      default:
        return `Generated Content - ${location} (${timestamp})`;
    }
  }

  private async callGenerationAPI(
    config: TemplateConfig,
    payload: Record<string, any>,
    contentId: string
  ): Promise<{ success: boolean; content?: any; error?: string }> {
    console.log(`[TemplateOrchestrator] Calling generation API: ${config.endpoint}`);
    
    // Simulate API call for now - in production this would call the actual backend
    try {
      // Mock successful response based on content type
      const mockContent = this.generateMockContent(config.type, payload);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      return {
        success: true,
        content: mockContent
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'API call failed'
      };
    }
  }

  private generateMockContent(contentType: ContentType, payload: Record<string, any>): any {
    const location = payload.location || 'Dubai Marina';
    
    switch (contentType) {
      case 'CMA_REPORT':
        return {
          structured: {
            property: {
              address: location,
              sqft: 2000,
              bedrooms: 3,
              bathrooms: 3,
              yearBuilt: 2020,
              lotSize: '2000 sqft',
              type: 'Apartment'
            },
            marketAnalysis: {
              avgPrice: 2500000,
              medianPrice: 2400000,
              pricePerSqft: 1250,
              marketTrend: 'up' as const,
              daysOnMarket: 28,
              inventory: 156
            },
            comparables: [
              {
                address: `${location} Tower A`,
                price: 2500000,
                sqft: 2000,
                bedrooms: 3,
                bathrooms: 3,
                soldDate: new Date().toISOString(),
                distance: 0.2,
                pricePerSqft: 1250
              },
              {
                address: `${location} Tower B`,
                price: 2800000,
                sqft: 2200,
                bedrooms: 3,
                bathrooms: 3,
                soldDate: new Date().toISOString(),
                distance: 0.3,
                pricePerSqft: 1273
              },
              {
                address: `${location} Tower C`,
                price: 2300000,
                sqft: 1900,
                bedrooms: 2,
                bathrooms: 2,
                soldDate: new Date().toISOString(),
                distance: 0.1,
                pricePerSqft: 1211
              }
            ],
            valuation: {
              estimatedValue: 2500000,
              confidenceRange: { min: 2300000, max: 2700000 },
              methodology: ['Comparative Market Analysis', 'Price Per Square Foot Analysis']
            },
            insights: [
              'Market showing strong upward momentum with 12% YoY growth',
              'High demand in luxury segment driving premium pricing',
              'Limited supply pipeline supporting current valuations',
              'Strong rental yields of 7.5% expected in this location'
            ],
            disclaimers: [
              'Market analysis based on recent comparable sales',
              'Property valuations are estimates and may vary',
              'Market conditions subject to change'
            ],
            generatedAt: new Date().toISOString(),
            reportId: `cma_${Date.now()}`
          },
          formatted: `<div class="cma-report">
            <h1>CMA Report - ${location}</h1>
            <div class="executive-summary">
              <h2>Executive Summary</h2>
              <p>Comprehensive market analysis showing strong investment potential...</p>
            </div>
          </div>`,
          exportUrl: `/api/v1/cma/export/${contentType.toLowerCase()}`
        };

      case 'PITCH_DECK':
        return {
          structured: {
            id: `deck_${Date.now()}`,
            title: `${location} Investment Opportunity`,
            property: {
              address: location,
              type: 'residential' as const,
              sqft: 2000,
              lotSize: '2000 sqft',
              yearBuilt: 2020
            },
            slides: [
              {
                id: 'slide_1',
                type: 'title' as const,
                title: 'Investment Opportunity',
                content: {
                  text: `${location} Premium Development`,
                  bullets: [
                    'Prime location with sea views',
                    'High-end finishes and amenities',
                    'Strong rental demand'
                  ]
                }
              },
              {
                id: 'slide_2',
                type: 'market-analysis' as const,
                title: 'Market Opportunity',
                content: {
                  text: 'Growing Demand in Premium Segment',
                  bullets: [
                    '15% YoY price appreciation',
                    '85% occupancy rates',
                    'Limited new supply pipeline'
                  ],
                  charts: [
                    {
                      type: 'bar' as const,
                      title: 'Market Growth',
                      data: [{ year: 2023, growth: 15 }, { year: 2024, growth: 12 }]
                    }
                  ]
                }
              },
              {
                id: 'slide_3',
                type: 'financial-projections' as const,
                title: 'Financial Highlights',
                content: {
                  text: 'Strong Investment Returns',
                  bullets: [
                    '7.5% rental yield',
                    'AED 2.5M investment',
                    '12% IRR projected'
                  ],
                  data: {
                    investment: 2500000,
                    yield: 7.5,
                    irr: 12
                  }
                }
              }
            ],
            theme: {
              primaryColor: '#1e40af',
              accentColor: '#3b82f6',
              fontFamily: 'Inter'
            },
            generatedAt: new Date().toISOString()
          },
          formatted: `<div class="pitch-deck">
            <div class="slide">
              <h1>Investment Opportunity</h1>
              <h2>${location} Premium Development</h2>
            </div>
          </div>`,
          exportUrl: `/api/v1/decks/export/${contentType.toLowerCase()}`
        };

      default:
        return {
          structured: { content: `Generated content for ${location}` },
          formatted: `<div>Generated content for ${location}</div>`,
          exportUrl: `/api/v1/content/export/${contentType.toLowerCase()}`
        };
    }
  }
}

// Export singleton instance
export default new TemplateOrchestrator();