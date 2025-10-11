/**
 * Content Engine - Content Intelligence Layer
 * ==========================================
 * 
 * The core AI-powered content generation engine for Aura v3.3:
 * - Dynamic prompt assembly with context injection
 * - Multi-pass generation with self-critique and revision
 * - Brand compliance and style enforcement
 * - Retrieval augmentation from memory service
 * 
 * Version: 3.3.0
 * Phase: Content Intelligence Layer
 */

import { ContentType } from '../../types/contentSchemas';
import memoryService, { AgentProfile, PropertyRecord, NeighborhoodFacts } from './memoryService';

// =============================================================================
// GENERATION TYPES AND INTERFACES
// =============================================================================

export interface GenerationContext {
  session_id: string;
  task_id: string;
  content_type: ContentType;
  user_prompt: string;
  agent_profile?: AgentProfile;
  property_record?: PropertyRecord;
  neighborhood_facts?: NeighborhoodFacts;
  brand_guidelines?: BrandGuidelines;
  template_constraints?: TemplateConstraints;
  generation_params?: GenerationParameters;
}

export interface BrandGuidelines {
  voice_tone: 'professional' | 'friendly' | 'authoritative' | 'casual';
  writing_style: 'concise' | 'detailed' | 'storytelling';
  avoid_terms: string[];
  required_disclaimers: string[];
  brand_colors: {
    primary: string;
    secondary: string;
    accent?: string;
  };
  typography: {
    headings: string;
    body: string;
  };
  logo_guidelines?: {
    min_size: string;
    placement_rules: string[];
  };
}

export interface TemplateConstraints {
  template_id: string;
  max_characters?: number;
  required_sections: string[];
  optional_sections?: string[];
  slot_limits: Record<string, number>;
  typography_rules: {
    heading_levels: number;
    body_paragraph_limit: number;
    list_item_limit: number;
  };
}

export interface GenerationParameters {
  temperature: number; // 0.0 - 2.0, creativity level
  max_tokens: number;
  seed?: number; // For deterministic results
  target_audience: string;
  content_goals: string[];
  compliance_level: 'strict' | 'moderate' | 'flexible';
  revision_passes: number;
}

export interface GenerationResult {
  content: any;
  metadata: {
    generation_time_ms: number;
    token_usage: {
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    };
    revision_count: number;
    quality_scores: {
      brand_compliance: number;
      readability: number;
      factual_accuracy: number;
      template_fit: number;
      overall: number;
    };
    validation_results: ValidationResult[];
    generation_params: GenerationParameters;
  };
  success: boolean;
  error?: string;
}

export interface ValidationResult {
  validator: string;
  passed: boolean;
  score: number;
  issues: string[];
  suggestions: string[];
}

// =============================================================================
// PROMPT TEMPLATES
// =============================================================================

const CONTENT_PROMPTS = {
  CMA_REPORT: {
    system: `You are an expert real estate analyst creating professional Comparative Market Analysis (CMA) reports. Your goal is to provide accurate, data-driven insights that help agents and clients make informed decisions.

Key principles:
- Use factual data and professional language
- Focus on market trends and property comparisons
- Include disclaimers about data accuracy
- Maintain objectivity in analysis`,

    user_template: `Create a comprehensive CMA report for the following property:

Property Details:
{property_details}

Comparable Properties:
{comparable_data}

Market Context:
{market_context}

Agent Profile:
{agent_context}

Brand Guidelines:
{brand_guidelines}

Template Constraints:
- Maximum characters: {max_characters}
- Required sections: {required_sections}
- Target audience: {target_audience}

Please generate a complete CMA report that includes:
1. Executive summary
2. Property overview
3. Market analysis with trends
4. Comparable property analysis
5. Valuation range with methodology
6. Key insights and recommendations
7. Professional disclaimers

Ensure the content aligns with the agent's voice and brand guidelines while maintaining professional standards.`
  },

  PITCH_DECK: {
    system: `You are a skilled real estate marketing specialist creating compelling investor pitch decks. Your expertise lies in translating property data into persuasive narratives that drive investment decisions.

Key principles:
- Lead with opportunity and ROI potential
- Use data to support investment thesis
- Create compelling visual narratives
- Address investor concerns proactively`,

    user_template: `Create an investor pitch deck for the following property opportunity:

Property Investment Opportunity:
{property_details}

Market Analysis:
{market_context}

Financial Projections:
{financial_data}

Agent Expertise:
{agent_context}

Brand Guidelines:
{brand_guidelines}

Presentation Requirements:
- Slide count: {slide_count}
- Target audience: {target_audience}
- Investment type: {investment_type}

Please generate a complete pitch deck with the following slides:
1. Title slide with opportunity overview
2. Investment highlights and key metrics
3. Property overview and specifications  
4. Market analysis and trends
5. Financial projections and ROI
6. Neighborhood and location advantages
7. Risk mitigation and exit strategies
8. Next steps and call to action

Each slide should have:
- Compelling title
- Key bullet points (max 5 per slide)
- Supporting data or metrics
- Visual content suggestions

Ensure the narrative builds momentum toward the investment decision while maintaining credibility.`
  },

  MARKET_REPORT: {
    system: `You are a real estate market research analyst creating insightful market reports. Your expertise is in interpreting market data and trends to provide actionable intelligence for agents and their clients.

Key principles:
- Present data in digestible, actionable insights
- Highlight trends and their implications
- Provide forward-looking analysis
- Support conclusions with specific metrics`,

    user_template: `Create a comprehensive market report for the following area:

Market Area:
{market_area}

Market Data:
{market_data}

Historical Trends:
{historical_trends}

Agent Market Knowledge:
{agent_context}

Brand Guidelines:
{brand_guidelines}

Report Parameters:
- Time period: {time_period}
- Property types: {property_types}
- Target audience: {target_audience}

Please generate a market report that includes:
1. Executive summary of market conditions
2. Key market metrics and trends
3. Price analysis by property type
4. Inventory and absorption rates
5. Buyer and seller behavior patterns
6. Neighborhood spotlight sections
7. Market forecast and outlook
8. Actionable insights for clients

Present data in clear, professional language with specific numbers and percentages where available.`
  },

  SOCIAL_POST: {
    system: `You are a social media marketing specialist for real estate professionals. Your expertise is creating engaging, platform-optimized content that builds trust and drives engagement while adhering to real estate compliance standards.

Key principles:
- Platform-specific optimization (character limits, hashtags)
- Visual-first content strategy
- Authentic, conversational tone
- Compliance with real estate advertising rules`,

    user_template: `Create an engaging social media post for the following:

Content Topic:
{content_topic}

Platform:
{platform}

Property/Market Context:
{property_context}

Agent Brand:
{agent_context}

Brand Guidelines:
{brand_guidelines}

Post Requirements:
- Character limit: {character_limit}
- Hashtag count: {hashtag_count}
- Tone: {tone}
- Call to action: {cta_type}

Please generate a social post that includes:
- Compelling hook/opening line
- Valuable content or insight
- Engaging middle content
- Clear call to action
- Relevant hashtags (formatted for {platform})
- Visual content suggestions

Ensure the post feels authentic to the agent's voice while being optimized for maximum engagement on {platform}.`
  },

  NEWSLETTER: {
    system: `You are an email marketing specialist for real estate professionals. Your expertise is creating valuable newsletter content that nurtures client relationships and positions agents as trusted market experts.

Key principles:
- Provide genuine value to subscribers
- Balance promotional and educational content
- Maintain consistent brand voice
- Include clear calls to action`,

    user_template: `Create a professional newsletter for the following:

Newsletter Theme:
{newsletter_theme}

Market Updates:
{market_updates}

Featured Properties:
{featured_properties}

Agent Insights:
{agent_context}

Brand Guidelines:
{brand_guidelines}

Newsletter Parameters:
- Target audience: {target_audience}
- Tone: {tone}
- Length: {target_length}
- Sections required: {required_sections}

Please generate a newsletter that includes:
1. Compelling subject line
2. Personal greeting from agent
3. Market update section
4. Featured property highlights
5. Neighborhood spotlight or tip
6. Community events or news
7. Call to action
8. Professional signature and disclaimers

Ensure the content provides value while maintaining the agent's professional brand and encouraging engagement.`
  }
};

// =============================================================================
// CONTENT ENGINE CLASS
// =============================================================================

export class ContentEngine {
  private static instance: ContentEngine;

  private constructor() {
    console.log('[ContentEngine] Initializing intelligent content generation engine...');
  }

  public static getInstance(): ContentEngine {
    if (!ContentEngine.instance) {
      ContentEngine.instance = new ContentEngine();
    }
    return ContentEngine.instance;
  }

  // =============================================================================
  // MAIN GENERATION METHODS
  // =============================================================================

  public async generateContent(context: GenerationContext): Promise<GenerationResult> {
    const startTime = Date.now();
    console.log(`[ContentEngine] Starting content generation for ${context.content_type} (Task: ${context.task_id})`);

    try {
      // Step 1: Enrich context with memory
      const enrichedContext = await this.enrichContextWithMemory(context);

      // Step 2: Build dynamic prompt
      const prompt = await this.buildDynamicPrompt(enrichedContext);

      // Step 3: Generate initial draft
      let content = await this.generateDraft(prompt, enrichedContext.generation_params || this.getDefaultParameters(context.content_type));

      // Step 4: Multi-pass revision
      if (enrichedContext.generation_params?.revision_passes && enrichedContext.generation_params.revision_passes > 1) {
        content = await this.performRevisionPasses(content, enrichedContext);
      }

      // Step 5: Validate and score
      const validationResults = await this.validateContent(content, enrichedContext);
      const qualityScores = this.calculateQualityScores(content, enrichedContext, validationResults);

      // Step 6: Store in memory for future reference
      await this.storeGeneratedArtifact(context, content, qualityScores, validationResults);

      const generationTime = Date.now() - startTime;

      return {
        content,
        metadata: {
          generation_time_ms: generationTime,
          token_usage: this.mockTokenUsage(prompt), // In real implementation, get from LLM provider
          revision_count: enrichedContext.generation_params?.revision_passes || 1,
          quality_scores: qualityScores,
          validation_results: validationResults,
          generation_params: enrichedContext.generation_params || this.getDefaultParameters(context.content_type)
        },
        success: true
      };

    } catch (error) {
      console.error('[ContentEngine] Generation failed:', error);
      
      return {
        content: null,
        metadata: {
          generation_time_ms: Date.now() - startTime,
          token_usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
          revision_count: 0,
          quality_scores: { brand_compliance: 0, readability: 0, factual_accuracy: 0, template_fit: 0, overall: 0 },
          validation_results: [],
          generation_params: this.getDefaultParameters(context.content_type)
        },
        success: false,
        error: error instanceof Error ? error.message : 'Unknown generation error'
      };
    }
  }

  public async reviseWithFeedback(
    originalContent: any,
    feedback: string,
    context: GenerationContext
  ): Promise<GenerationResult> {
    console.log(`[ContentEngine] Revising content based on feedback for ${context.content_type}`);

    const revisionPrompt = this.buildRevisionPrompt(originalContent, feedback, context);
    const revisedContent = await this.generateDraft(revisionPrompt, context.generation_params || this.getDefaultParameters(context.content_type));

    // Validate revised content
    const enrichedContext = await this.enrichContextWithMemory(context);
    const validationResults = await this.validateContent(revisedContent, enrichedContext);
    const qualityScores = this.calculateQualityScores(revisedContent, enrichedContext, validationResults);

    return {
      content: revisedContent,
      metadata: {
        generation_time_ms: 0, // Not tracking revision time separately
        token_usage: this.mockTokenUsage(revisionPrompt),
        revision_count: 1,
        quality_scores: qualityScores,
        validation_results: validationResults,
        generation_params: context.generation_params || this.getDefaultParameters(context.content_type)
      },
      success: true
    };
  }

  // =============================================================================
  // CONTEXT ENRICHMENT
  // =============================================================================

  private async enrichContextWithMemory(context: GenerationContext): Promise<GenerationContext> {
    console.log(`[ContentEngine] Enriching context with memory for task ${context.task_id}`);

    // Get task memory and context
    const contextSummary = await memoryService.getContextSummary(context.task_id);

    // Retrieve relevant entities from memory
    const relevantMemories = await memoryService.recall(context.user_prompt, {
      limit: 5,
      relevance_threshold: 0.7
    });

    // Build enriched context
    const enrichedContext: GenerationContext = {
      ...context,
      // Add memory-derived context
      agent_profile: relevantMemories.find(m => m.entity.name)?.entity as AgentProfile,
      property_record: relevantMemories.find(m => m.entity.address)?.entity as PropertyRecord,
      neighborhood_facts: relevantMemories.find(m => m.entity.amenities)?.entity as NeighborhoodFacts
    };

    // Add brand guidelines if agent profile found
    if (enrichedContext.agent_profile) {
      enrichedContext.brand_guidelines = this.extractBrandGuidelines(enrichedContext.agent_profile);
    }

    // Add task memory context
    await memoryService.addToTaskContext(context.task_id, 'user_prompt', {
      session_id: context.session_id,
      prompt: context.user_prompt,
      intent: context.content_type,
      entities: {
        content_type: context.content_type,
        property_address: enrichedContext.property_record?.address,
        agent_name: enrichedContext.agent_profile?.name
      }
    });

    console.log(`[ContentEngine] Context enriched with ${relevantMemories.length} relevant memories`);
    return enrichedContext;
  }

  private extractBrandGuidelines(agentProfile: AgentProfile): BrandGuidelines {
    return {
      voice_tone: agentProfile.voice_preferences.tone,
      writing_style: agentProfile.voice_preferences.style,
      avoid_terms: agentProfile.voice_preferences.avoid_terms || [],
      required_disclaimers: [
        'This information is deemed reliable but not guaranteed.',
        'All measurements and data should be independently verified.'
      ],
      brand_colors: agentProfile.branding.colors,
      typography: agentProfile.branding.fonts
    };
  }

  // =============================================================================
  // PROMPT ASSEMBLY
  // =============================================================================

  private async buildDynamicPrompt(context: GenerationContext): Promise<string> {
    const template = CONTENT_PROMPTS[context.content_type];
    if (!template) {
      throw new Error(`No prompt template found for content type: ${context.content_type}`);
    }

    // Build context-specific replacements
    const replacements = {
      property_details: this.formatPropertyDetails(context.property_record),
      market_context: this.formatMarketContext(context.neighborhood_facts),
      agent_context: this.formatAgentContext(context.agent_profile),
      brand_guidelines: this.formatBrandGuidelines(context.brand_guidelines),
      comparable_data: this.formatComparableData(context.property_record?.market_data?.comparables),
      financial_data: this.formatFinancialData(context.property_record),
      market_data: this.formatMarketData(context.neighborhood_facts),
      historical_trends: this.formatHistoricalTrends(context.property_record?.details?.price_history),
      market_area: this.formatMarketArea(context.neighborhood_facts),
      content_topic: context.user_prompt,
      property_context: this.formatPropertyContext(context.property_record),
      newsletter_theme: this.extractNewsletterTheme(context.user_prompt),
      market_updates: this.formatMarketUpdates(context.neighborhood_facts),
      featured_properties: this.formatFeaturedProperties([context.property_record].filter(Boolean)),
      
      // Template constraints
      max_characters: context.template_constraints?.max_characters || 5000,
      required_sections: context.template_constraints?.required_sections.join(', ') || 'All standard sections',
      target_audience: context.generation_params?.target_audience || 'General clients',
      slide_count: context.content_type === ContentType.PITCH_DECK ? '8-10' : 'N/A',
      investment_type: this.extractInvestmentType(context.user_prompt),
      time_period: this.extractTimePeriod(context.user_prompt),
      property_types: this.extractPropertyTypes(context.user_prompt),
      platform: this.extractSocialPlatform(context.user_prompt),
      character_limit: this.getSocialCharacterLimit(this.extractSocialPlatform(context.user_prompt)),
      hashtag_count: this.getSocialHashtagCount(this.extractSocialPlatform(context.user_prompt)),
      tone: context.brand_guidelines?.voice_tone || 'professional',
      cta_type: this.extractCallToAction(context.user_prompt),
      target_length: this.extractTargetLength(context.user_prompt)
    };

    // Replace placeholders in template
    let prompt = template.user_template;
    Object.entries(replacements).forEach(([key, value]) => {
      prompt = prompt.replace(new RegExp(`{${key}}`, 'g'), value.toString());
    });

    console.log(`[ContentEngine] Built dynamic prompt for ${context.content_type} (${prompt.length} chars)`);
    return prompt;
  }

  // =============================================================================
  // CONTENT GENERATION
  // =============================================================================

  private async generateDraft(prompt: string, params: GenerationParameters): Promise<any> {
    console.log(`[ContentEngine] Generating draft with temperature ${params.temperature}...`);

    // In a real implementation, this would call OpenAI, Anthropic, or another LLM
    // For now, return contextually appropriate mock content based on the prompt

    if (prompt.includes('CMA report')) {
      return this.generateMockCMAContent();
    } else if (prompt.includes('pitch deck')) {
      return this.generateMockPitchDeckContent();
    } else if (prompt.includes('market report')) {
      return this.generateMockMarketReportContent();
    } else if (prompt.includes('social')) {
      return this.generateMockSocialContent();
    } else if (prompt.includes('newsletter')) {
      return this.generateMockNewsletterContent();
    }

    return { content: 'Generated content would appear here based on the prompt and parameters.' };
  }

  private buildRevisionPrompt(originalContent: any, feedback: string, context: GenerationContext): string {
    return `Please revise the following ${context.content_type} content based on this feedback:

FEEDBACK: ${feedback}

ORIGINAL CONTENT:
${JSON.stringify(originalContent, null, 2)}

Please provide the revised content that addresses the feedback while maintaining the original structure and quality standards.`;
  }

  private async performRevisionPasses(content: any, context: GenerationContext): Promise<any> {
    console.log(`[ContentEngine] Performing ${context.generation_params?.revision_passes} revision passes...`);

    let revisedContent = content;
    const maxPasses = context.generation_params?.revision_passes || 1;

    for (let pass = 1; pass < maxPasses; pass++) {
      // Self-critique and revision
      const critiquePrompt = this.buildSelfCritiquePrompt(revisedContent, context);
      const critique = await this.generateDraft(critiquePrompt, {
        ...this.getDefaultParameters(context.content_type),
        temperature: 0.3 // Lower temperature for more focused critique
      });

      if (critique.suggestions && critique.suggestions.length > 0) {
        const revisionPrompt = this.buildRevisionPrompt(revisedContent, critique.suggestions.join('. '), context);
        revisedContent = await this.generateDraft(revisionPrompt, context.generation_params!);
      }
    }

    return revisedContent;
  }

  private buildSelfCritiquePrompt(content: any, context: GenerationContext): string {
    return `Please critique the following ${context.content_type} content for:
1. Brand compliance and voice consistency
2. Factual accuracy and completeness  
3. Template fit and formatting
4. Readability and engagement

CONTENT TO CRITIQUE:
${JSON.stringify(content, null, 2)}

Provide specific suggestions for improvement in JSON format:
{
  "brand_compliance": { "score": 0-10, "issues": [], "suggestions": [] },
  "factual_accuracy": { "score": 0-10, "issues": [], "suggestions": [] },
  "template_fit": { "score": 0-10, "issues": [], "suggestions": [] },
  "readability": { "score": 0-10, "issues": [], "suggestions": [] },
  "overall_suggestions": []
}`;
  }

  // =============================================================================
  // VALIDATION AND SCORING
  // =============================================================================

  private async validateContent(content: any, context: GenerationContext): Promise<ValidationResult[]> {
    const results: ValidationResult[] = [];

    // Brand compliance validation
    results.push(await this.validateBrandCompliance(content, context.brand_guidelines));

    // Template fit validation
    if (context.template_constraints) {
      results.push(await this.validateTemplateFit(content, context.template_constraints));
    }

    // Content type specific validation
    results.push(await this.validateContentTypeRequirements(content, context.content_type));

    // Fair housing and compliance
    results.push(await this.validateCompliance(content));

    return results;
  }

  private async validateBrandCompliance(content: any, brandGuidelines?: BrandGuidelines): Promise<ValidationResult> {
    // Mock validation - in real implementation would check voice, avoid terms, etc.
    const issues: string[] = [];
    const suggestions: string[] = [];

    if (!brandGuidelines) {
      issues.push('No brand guidelines available');
    } else {
      // Check for avoided terms
      const contentStr = JSON.stringify(content).toLowerCase();
      brandGuidelines.avoid_terms.forEach(term => {
        if (contentStr.includes(term.toLowerCase())) {
          issues.push(`Contains avoided term: "${term}"`);
          suggestions.push(`Replace or remove "${term}" per brand guidelines`);
        }
      });
    }

    return {
      validator: 'brand_compliance',
      passed: issues.length === 0,
      score: Math.max(0, 10 - issues.length * 2) / 10,
      issues,
      suggestions
    };
  }

  private async validateTemplateFit(content: any, constraints: TemplateConstraints): Promise<ValidationResult> {
    const issues: string[] = [];
    const suggestions: string[] = [];

    // Check character limits
    const contentStr = JSON.stringify(content);
    if (constraints.max_characters && contentStr.length > constraints.max_characters) {
      issues.push(`Content exceeds maximum characters: ${contentStr.length}/${constraints.max_characters}`);
      suggestions.push('Reduce content length to fit template constraints');
    }

    // Check required sections
    const hasRequiredSections = constraints.required_sections.every(section => 
      contentStr.toLowerCase().includes(section.toLowerCase())
    );

    if (!hasRequiredSections) {
      issues.push('Missing required sections');
      suggestions.push('Ensure all required sections are present');
    }

    return {
      validator: 'template_fit',
      passed: issues.length === 0,
      score: Math.max(0, 10 - issues.length * 3) / 10,
      issues,
      suggestions
    };
  }

  private async validateContentTypeRequirements(content: any, contentType: ContentType): Promise<ValidationResult> {
    const issues: string[] = [];
    const suggestions: string[] = [];

    switch (contentType) {
      case ContentType.CMA_REPORT:
        if (!content.executive_summary) {
          issues.push('Missing executive summary');
        }
        if (!content.comparables || content.comparables.length === 0) {
          issues.push('Missing comparable properties');
        }
        break;

      case ContentType.PITCH_DECK:
        if (!content.slides || content.slides.length < 5) {
          issues.push('Insufficient number of slides');
        }
        break;

      case ContentType.SOCIAL_POST:
        if (!content.content) {
          issues.push('Missing post content');
        }
        if (!content.hashtags || content.hashtags.length === 0) {
          issues.push('Missing hashtags');
        }
        break;
    }

    return {
      validator: 'content_requirements',
      passed: issues.length === 0,
      score: Math.max(0, 10 - issues.length * 2) / 10,
      issues,
      suggestions
    };
  }

  private async validateCompliance(content: any): Promise<ValidationResult> {
    const issues: string[] = [];
    const suggestions: string[] = [];
    const contentStr = JSON.stringify(content).toLowerCase();

    // Fair housing compliance
    const discriminatoryTerms = ['perfect for families', 'ideal for singles', 'great for young professionals'];
    discriminatoryTerms.forEach(term => {
      if (contentStr.includes(term)) {
        issues.push(`Potentially discriminatory language: "${term}"`);
        suggestions.push(`Remove or rephrase: "${term}"`);
      }
    });

    return {
      validator: 'compliance',
      passed: issues.length === 0,
      score: Math.max(0, 10 - issues.length * 4) / 10,
      issues,
      suggestions
    };
  }

  private calculateQualityScores(
    content: any,
    context: GenerationContext,
    validationResults: ValidationResult[]
  ): GenerationResult['metadata']['quality_scores'] {
    const scores = {
      brand_compliance: validationResults.find(r => r.validator === 'brand_compliance')?.score || 0,
      readability: 0.85, // Mock score
      factual_accuracy: 0.90, // Mock score  
      template_fit: validationResults.find(r => r.validator === 'template_fit')?.score || 0,
      overall: 0
    };

    scores.overall = (scores.brand_compliance + scores.readability + scores.factual_accuracy + scores.template_fit) / 4;

    return scores;
  }

  // =============================================================================
  // MEMORY INTEGRATION
  // =============================================================================

  private async storeGeneratedArtifact(
    context: GenerationContext,
    content: any,
    qualityScores: any,
    validationResults: ValidationResult[]
  ): Promise<void> {
    const artifact = {
      id: `artifact_${context.task_id}_${Date.now()}`,
      task_id: context.task_id,
      content_type: context.content_type,
      title: this.generateArtifactTitle(context),
      content,
      metadata: {
        template_used: context.template_constraints?.template_id || 'default',
        brand_compliance_score: qualityScores.brand_compliance,
        generation_params: context.generation_params || this.getDefaultParameters(context.content_type),
        validation_results: validationResults
      },
      related_entities: {
        agent_id: context.agent_profile?.id,
        property_id: context.property_record?.id,
        neighborhood_id: context.neighborhood_facts?.id
      },
      usage_context: {
        channel: this.inferChannel(context.content_type),
        target_audience: context.generation_params?.target_audience
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    await memoryService.upsertArtifact(artifact);

    // Add to task memory
    await memoryService.addToTaskContext(context.task_id, 'ai_response', {
      response: 'Content generated successfully',
      content_generated: context.content_type,
      confidence_score: qualityScores.overall
    });

    console.log(`[ContentEngine] Stored generated artifact: ${artifact.title}`);
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  private getDefaultParameters(contentType: ContentType): GenerationParameters {
    const defaults = {
      [ContentType.CMA_REPORT]: { temperature: 0.3, max_tokens: 3000, target_audience: 'clients', content_goals: ['inform', 'analyze'], compliance_level: 'strict' as const, revision_passes: 2 },
      [ContentType.PITCH_DECK]: { temperature: 0.7, max_tokens: 2500, target_audience: 'investors', content_goals: ['persuade', 'inform'], compliance_level: 'moderate' as const, revision_passes: 2 },
      [ContentType.MARKET_REPORT]: { temperature: 0.4, max_tokens: 2000, target_audience: 'clients', content_goals: ['inform', 'educate'], compliance_level: 'strict' as const, revision_passes: 1 },
      [ContentType.SOCIAL_POST]: { temperature: 0.8, max_tokens: 500, target_audience: 'general', content_goals: ['engage', 'promote'], compliance_level: 'moderate' as const, revision_passes: 1 },
      [ContentType.NEWSLETTER]: { temperature: 0.6, max_tokens: 1500, target_audience: 'subscribers', content_goals: ['nurture', 'inform'], compliance_level: 'moderate' as const, revision_passes: 1 }
    };

    return defaults[contentType];
  }

  private mockTokenUsage(prompt: string) {
    // Mock token calculation based on rough estimates
    const promptTokens = Math.ceil(prompt.length / 4);
    const completionTokens = Math.ceil(promptTokens * 0.7);
    
    return {
      prompt_tokens: promptTokens,
      completion_tokens: completionTokens,
      total_tokens: promptTokens + completionTokens
    };
  }

  private generateArtifactTitle(context: GenerationContext): string {
    const typeNames = {
      [ContentType.CMA_REPORT]: 'CMA Report',
      [ContentType.PITCH_DECK]: 'Investor Pitch Deck',
      [ContentType.MARKET_REPORT]: 'Market Analysis',
      [ContentType.SOCIAL_POST]: 'Social Media Post',
      [ContentType.NEWSLETTER]: 'Newsletter'
    };

    const baseName = typeNames[context.content_type];
    const propertyContext = context.property_record?.address ? ` - ${context.property_record.address.split(',')[0]}` : '';
    const timestamp = new Date().toLocaleDateString();

    return `${baseName}${propertyContext} (${timestamp})`;
  }

  private inferChannel(contentType: ContentType): string {
    const channelMap = {
      [ContentType.CMA_REPORT]: 'client_presentation',
      [ContentType.PITCH_DECK]: 'investor_presentation',
      [ContentType.MARKET_REPORT]: 'market_communication',
      [ContentType.SOCIAL_POST]: 'social_media',
      [ContentType.NEWSLETTER]: 'email_marketing'
    };
    
    return channelMap[contentType];
  }

  // =============================================================================
  // FORMATTING HELPERS
  // =============================================================================

  private formatPropertyDetails(property?: PropertyRecord): string {
    if (!property) return 'Property details not available';
    
    return `Address: ${property.address}
Type: ${property.type}
Size: ${property.details.sqft} sqft
Bedrooms: ${property.details.bedrooms}
Bathrooms: ${property.details.bathrooms}
Year Built: ${property.details.year_built}
Current Price: $${property.details.price?.toLocaleString() || 'TBD'}`;
  }

  private formatMarketContext(neighborhood?: NeighborhoodFacts): string {
    if (!neighborhood) return 'Market context not available';
    
    return `Neighborhood: ${neighborhood.name}, ${neighborhood.city}, ${neighborhood.state}
Population: ${neighborhood.demographics.population?.toLocaleString() || 'N/A'}
Median Income: $${neighborhood.demographics.median_income?.toLocaleString() || 'N/A'}
Key Amenities: ${neighborhood.amenities.join(', ')}
Transportation: Walkability score ${neighborhood.transportation.walkability_score || 'N/A'}`;
  }

  private formatAgentContext(agent?: AgentProfile): string {
    if (!agent) return 'Agent context not available';
    
    return `Agent: ${agent.name}
Brokerage: ${agent.brokerage}
Experience: ${agent.experience_years} years
Specialties: ${agent.specialties.join(', ')}
Markets: ${agent.markets.join(', ')}
Bio: ${agent.bio}`;
  }

  private formatBrandGuidelines(brand?: BrandGuidelines): string {
    if (!brand) return 'Brand guidelines not specified';
    
    return `Voice Tone: ${brand.voice_tone}
Writing Style: ${brand.writing_style}
Primary Color: ${brand.brand_colors.primary}
Secondary Color: ${brand.brand_colors.secondary}
Avoid Terms: ${brand.avoid_terms.join(', ')}`;
  }

  private formatComparableData(comparables?: any[]): string {
    if (!comparables || comparables.length === 0) return 'No comparable data available';
    
    return comparables.map(comp => 
      `${comp.address}: $${comp.price.toLocaleString()} (${comp.sqft} sqft, $${comp.price/comp.sqft}/sqft)`
    ).join('\n');
  }

  private formatFinancialData(property?: PropertyRecord): string {
    if (!property?.details.price) return 'Financial data not available';
    
    return `Current Price: $${property.details.price.toLocaleString()}
Price per SqFt: $${Math.round(property.details.price / (property.details.sqft || 1))}
Estimated Monthly Payment: $${Math.round(property.details.price * 0.004)} (rough estimate)`;
  }

  private formatMarketData(neighborhood?: NeighborhoodFacts): string {
    if (!neighborhood) return 'Market data not available';
    
    return `Area: ${neighborhood.name}
Demographics: ${neighborhood.demographics.population} residents
Economic Profile: $${neighborhood.demographics.median_income?.toLocaleString()} median income
Development: ${neighborhood.development.upcoming_projects?.length || 0} upcoming projects`;
  }

  private formatHistoricalTrends(priceHistory?: any[]): string {
    if (!priceHistory || priceHistory.length === 0) return 'No historical trends available';
    
    return priceHistory.map(entry => 
      `${entry.date}: $${entry.price.toLocaleString()} (${entry.event})`
    ).join('\n');
  }

  private formatMarketArea(neighborhood?: NeighborhoodFacts): string {
    return neighborhood ? `${neighborhood.name}, ${neighborhood.city}, ${neighborhood.state}` : 'Market area not specified';
  }

  private formatPropertyContext(property?: PropertyRecord): string {
    return property ? `${property.address} - ${property.type} property` : 'Property context not available';
  }

  private formatMarketUpdates(neighborhood?: NeighborhoodFacts): string {
    if (!neighborhood) return 'Market updates not available';
    
    return `Recent developments in ${neighborhood.name}: ${neighborhood.development.recent_developments?.join(', ') || 'No recent updates'}`;
  }

  private formatFeaturedProperties(properties: (PropertyRecord | undefined)[]): string {
    const validProperties = properties.filter(Boolean) as PropertyRecord[];
    if (validProperties.length === 0) return 'No featured properties available';
    
    return validProperties.map(prop => 
      `${prop.address}: ${prop.details.bedrooms}BR/${prop.details.bathrooms}BA, ${prop.details.sqft} sqft`
    ).join('\n');
  }

  // Extraction helpers
  private extractNewsletterTheme(prompt: string): string {
    if (prompt.toLowerCase().includes('market')) return 'Market Updates';
    if (prompt.toLowerCase().includes('listing')) return 'New Listings';
    return 'General Real Estate News';
  }

  private extractInvestmentType(prompt: string): string {
    if (prompt.toLowerCase().includes('flip')) return 'fix-and-flip';
    if (prompt.toLowerCase().includes('rental')) return 'buy-and-hold';
    if (prompt.toLowerCase().includes('commercial')) return 'commercial';
    return 'residential investment';
  }

  private extractTimePeriod(prompt: string): string {
    if (prompt.toLowerCase().includes('month')) return 'monthly';
    if (prompt.toLowerCase().includes('quarter')) return 'quarterly';
    if (prompt.toLowerCase().includes('year')) return 'yearly';
    return 'current period';
  }

  private extractPropertyTypes(prompt: string): string {
    const types: string[] = [];
    if (prompt.toLowerCase().includes('residential')) types.push('residential');
    if (prompt.toLowerCase().includes('commercial')) types.push('commercial');
    if (prompt.toLowerCase().includes('condo')) types.push('condominiums');
    return types.length > 0 ? types.join(', ') : 'all property types';
  }

  private extractSocialPlatform(prompt: string): string {
    if (prompt.toLowerCase().includes('instagram')) return 'instagram';
    if (prompt.toLowerCase().includes('facebook')) return 'facebook';
    if (prompt.toLowerCase().includes('linkedin')) return 'linkedin';
    if (prompt.toLowerCase().includes('twitter')) return 'twitter';
    return 'instagram'; // Default
  }

  private getSocialCharacterLimit(platform: string): number {
    const limits = {
      twitter: 280,
      instagram: 2200,
      facebook: 63206,
      linkedin: 3000
    };
    return limits[platform as keyof typeof limits] || 280;
  }

  private getSocialHashtagCount(platform: string): number {
    const counts = {
      twitter: 2,
      instagram: 10,
      facebook: 3,
      linkedin: 5
    };
    return counts[platform as keyof typeof counts] || 5;
  }

  private extractCallToAction(prompt: string): string {
    if (prompt.toLowerCase().includes('contact')) return 'contact';
    if (prompt.toLowerCase().includes('visit')) return 'schedule_showing';
    if (prompt.toLowerCase().includes('learn')) return 'learn_more';
    return 'engage';
  }

  private extractTargetLength(prompt: string): string {
    if (prompt.toLowerCase().includes('brief')) return 'short (300-500 words)';
    if (prompt.toLowerCase().includes('detailed')) return 'long (800-1200 words)';
    return 'medium (500-800 words)';
  }

  // =============================================================================
  // MOCK CONTENT GENERATORS
  // =============================================================================

  private generateMockCMAContent() {
    return {
      executive_summary: "This comprehensive CMA analysis evaluates the current market position and valuation range for the subject property. Based on recent comparable sales and current market conditions, the property demonstrates strong competitive positioning within the local market segment.",
      
      market_analysis: {
        avg_price: 485000,
        median_price: 475000,
        price_per_sqft: 285,
        market_trend: "up",
        days_on_market: 32,
        inventory: 156
      },
      
      comparables: [
        {
          address: "123 Similar St",
          price: 489000,
          sqft: 1685,
          price_per_sqft: 290,
          bedrooms: 3,
          bathrooms: 2,
          sold_date: "2024-09-15",
          distance: 0.3
        },
        {
          address: "456 Nearby Ave", 
          price: 472000,
          sqft: 1650,
          price_per_sqft: 286,
          bedrooms: 3,
          bathrooms: 2,
          sold_date: "2024-09-08",
          distance: 0.5
        },
        {
          address: "789 Close Cir",
          price: 495000,
          sqft: 1720,
          price_per_sqft: 288,
          bedrooms: 3,
          bathrooms: 2.5,
          sold_date: "2024-08-28",
          distance: 0.4
        }
      ],
      
      valuation: {
        estimated_value: 485000,
        confidence_range: { min: 470000, max: 500000 },
        methodology: ["Sales comparison approach", "Market trend analysis", "Location adjustment factors"]
      },
      
      insights: [
        "The local market shows strong upward momentum with 8.2% appreciation over the past 12 months.",
        "Properties in this price range are experiencing faster than average absorption, indicating healthy buyer demand.",
        "The subject property's condition and features align well with recent buyer preferences in this market segment.",
        "Inventory levels remain below historical averages, creating a favorable environment for sellers."
      ],
      
      disclaimers: [
        "This analysis is based on available public records and market data as of the report date.",
        "All information should be independently verified and should not be the sole basis for financial decisions.",
        "Market conditions can change rapidly and may affect property values."
      ]
    };
  }

  private generateMockPitchDeckContent() {
    return {
      slides: [
        {
          id: "slide_1",
          type: "title",
          title: "Investment Opportunity",
          content: {
            subtitle: "Prime Real Estate Investment",
            text: "Exceptional value creation opportunity in high-growth market",
            metrics: [
              { label: "Projected IRR", value: "18.5%", trend: "up" },
              { label: "Investment Period", value: "24 months", trend: "neutral" }
            ]
          }
        },
        {
          id: "slide_2", 
          type: "investment-highlights",
          title: "Investment Highlights",
          content: {
            bullets: [
              "Below-market acquisition price with immediate equity upside",
              "Located in rapidly appreciating neighborhood with strong fundamentals",
              "Multiple exit strategies including hold, improve, or redevelop",
              "Experienced team with proven track record in similar investments"
            ]
          }
        },
        {
          id: "slide_3",
          type: "property-overview", 
          title: "Property Overview",
          content: {
            text: "Well-positioned asset with strong potential for value enhancement",
            bullets: [
              "1,685 square feet with 3BR/2BA configuration",
              "Solid construction with good bones requiring cosmetic updates",
              "Large lot with potential for expansion or additional units",
              "Prime location with excellent walkability and transit access"
            ]
          }
        },
        {
          id: "slide_4",
          type: "market-analysis",
          title: "Market Analysis", 
          content: {
            text: "Robust market fundamentals support long-term appreciation",
            bullets: [
              "8.2% annual appreciation over past 12 months",
              "Below-average inventory creating seller's market conditions",
              "Strong demographic trends driving housing demand",
              "Upcoming infrastructure improvements will enhance desirability"
            ]
          }
        },
        {
          id: "slide_5",
          type: "financial-projections",
          title: "Financial Projections",
          content: {
            text: "Conservative projections show attractive risk-adjusted returns",
            metrics: [
              { label: "Acquisition Price", value: "$465,000", trend: "neutral" },
              { label: "Renovation Budget", value: "$35,000", trend: "neutral" },
              { label: "Projected Sale Price", value: "$575,000", trend: "up" },
              { label: "Net Profit", value: "$75,000", trend: "up" }
            ]
          }
        },
        {
          id: "slide_6",
          type: "conclusion",
          title: "Investment Recommendation",
          content: {
            text: "Strong buy recommendation based on market analysis and financial projections",
            bullets: [
              "Immediate action required due to competitive market conditions",
              "All due diligence materials available for qualified investors",
              "Financing options structured to optimize returns",
              "Timeline allows for completion within 24-month investment horizon"
            ]
          }
        }
      ],
      
      theme: {
        primaryColor: "#2563eb",
        accentColor: "#7c3aed", 
        fontFamily: "Inter, sans-serif"
      }
    };
  }

  private generateMockMarketReportContent() {
    return {
      executive_summary: "The local real estate market continues to demonstrate resilience and growth, with key indicators pointing toward sustained demand and controlled inventory levels. This report analyzes current market conditions and provides insights for buyers, sellers, and investors.",
      
      market_metrics: [
        { name: "Median Sale Price", value: 475000, unit: "USD", trend: "up", changePercent: 8.2 },
        { name: "Average Days on Market", value: 32, unit: "days", trend: "down", changePercent: -12.5 },
        { name: "Months of Inventory", value: 2.8, unit: "months", trend: "stable", changePercent: 2.1 },
        { name: "Sale-to-List Ratio", value: 98.5, unit: "percent", trend: "up", changePercent: 3.2 }
      ],
      
      market_segments: [
        { name: "Entry Level ($300-450K)", propertyType: "Condos/Townhomes", avgPrice: 385000, priceChange: 9.1, volume: 142, daysOnMarket: 28 },
        { name: "Mid-Range ($450-650K)", propertyType: "Single Family", avgPrice: 542000, priceChange: 7.8, volume: 89, daysOnMarket: 35 },
        { name: "Luxury ($650K+)", propertyType: "Executive Homes", avgPrice: 785000, priceChange: 6.4, volume: 34, daysOnMarket: 45 }
      ],
      
      insights: [
        "Buyer demand remains strong across all price segments, with entry-level properties experiencing the fastest appreciation.",
        "Inventory constraints continue to favor sellers, though new listings are beginning to increase seasonally.",
        "Interest rate fluctuations have created pockets of opportunity for well-qualified buyers.",
        "The luxury segment shows signs of normalization after rapid growth in previous quarters."
      ],
      
      forecast: {
        period: "Next 12 Months",
        predictions: [
          { metric: "Price Appreciation", value: 6.5, confidence: 0.78 },
          { metric: "Sales Volume", value: 4.2, confidence: 0.82 },
          { metric: "Average DOM", value: 35, confidence: 0.75 }
        ]
      }
    };
  }

  private generateMockSocialContent() {
    return {
      content: "🏡✨ Just listed! This stunning 3BR/2BA home in prime location offers the perfect blend of comfort and style. From the open-concept living to the beautifully updated kitchen, every detail has been thoughtfully designed. Ready to call this place home? 🔑",
      
      hashtags: [
        "#JustListed",
        "#RealEstate",
        "#DreamHome",
        "#OpenHouse", 
        "#YourNextHome",
        "#PropertyExpert",
        "#HomeSweetHome",
        "#NewListing"
      ],
      
      character_count: 287,
      
      visual_suggestions: [
        "Hero shot of front exterior with great curb appeal",
        "Bright, welcoming living room showing open concept",
        "Beautiful kitchen highlighting modern updates",
        "Master bedroom with staging to show scale"
      ],
      
      call_to_action: "DM for private showing or more details!",
      
      engagement_hooks: [
        "What's your favorite feature in this home?",
        "Tag someone who would love this space!",
        "Guess the listing price! 🤔"
      ]
    };
  }

  private generateMockNewsletterContent() {
    return {
      subject_line: "Your October Market Update + New Listings Inside 📊",
      
      sections: [
        {
          type: "greeting",
          title: "Hello from Your Local Market Expert!",
          content: "October has been an exciting month in our local real estate market. I'm thrilled to share the latest insights and opportunities with you."
        },
        {
          type: "market-update", 
          title: "Market Pulse: What's Happening Now",
          content: "Our market continues to show remarkable resilience with median home prices up 8.2% year-over-year. Buyer activity remains strong, and we're seeing healthy competition for well-priced properties. Days on market have decreased to an average of 32 days, indicating efficient market conditions."
        },
        {
          type: "featured-listings",
          title: "Featured Properties This Month", 
          content: "Take a look at these exceptional properties that recently hit the market. Each offers unique value propositions for different buyer segments."
        },
        {
          type: "neighborhood-spotlight",
          title: "Neighborhood Spotlight: Downtown District",
          content: "The Downtown District continues to evolve with new amenities and infrastructure improvements. Recent developments include the new transit hub and waterfront park, making this an increasingly attractive area for both residents and investors."
        },
        {
          type: "market-tip",
          title: "Insider Tip: Timing Your Next Move",
          content: "If you're considering buying or selling, current market conditions present unique opportunities. Sellers are benefiting from strong demand, while buyers who act decisively are securing great properties. Let's discuss how these trends might impact your real estate goals."
        },
        {
          type: "call-to-action",
          title: "Ready to Make Your Move?",
          content: "Whether you're thinking about buying, selling, or investing, I'm here to guide you through every step. Market conditions are dynamic, and having an experienced professional on your side makes all the difference."
        }
      ],
      
      signature: "Best regards,\n[Agent Name]\n[Contact Information]\n[Brokerage Name]",
      
      disclaimers: [
        "Market data compiled from local MLS and public records",
        "This information is for general guidance only",
        "Individual results may vary based on specific circumstances"
      ]
    };
  }
}

// =============================================================================
// SINGLETON EXPORT  
// =============================================================================

export default ContentEngine.getInstance();