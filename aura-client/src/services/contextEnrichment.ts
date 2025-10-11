/**
 * Aura Context Validation and Enrichment Service
 * 
 * Self-healing system that validates, enriches, and repairs incomplete workflow payloads
 * before they reach backend APIs. Ensures users never see "422 Unprocessable Content" errors.
 * 
 * Features:
 * ✅ Payload validation with detailed field checking
 * ✅ Context inference from recent task history  
 * ✅ Intelligent fallback strategies
 * ✅ Comprehensive error recovery
 * ✅ Debug logging and traceability
 */

import { Intent, IntentType } from './intentParser';

// Required fields for each workflow type
export interface WorkflowFieldRequirements {
  [key: string]: {
    required: string[];
    optional: string[];
    fallbacks: Record<string, any>;
  };
}

export const WORKFLOW_REQUIREMENTS: WorkflowFieldRequirements = {
  CMA: {
    required: ['location'],
    optional: ['property_type', 'date_range'],
    fallbacks: {
      location: 'Dubai Marina' // Default location
    }
  },
  MARKET_REPORT: {
    required: ['location'],
    optional: ['property_type', 'metrics'],
    fallbacks: {
      location: 'Dubai',
      property_type: 'mixed'
    }
  },
  SOCIAL_POST: {
    required: ['topic', 'query'], // Backend expects these specific fields
    optional: ['platform', 'category', 'content'],
    fallbacks: {
      topic: 'property update',
      query: 'real estate market',
      platform: 'instagram',
      category: 'marketing'
    }
  }
};

// Context inference patterns
export interface ContextInference {
  location?: string;
  topic?: string;
  query?: string;
  property_type?: string;
  propertyType?: string;
  taskType?: IntentType;
  confidence: number;
  source: 'recent_task' | 'prompt_analysis' | 'user_context' | 'fallback';
  [key: string]: string | number | IntentType | undefined; // Allow dynamic field access
}

// Enhanced payload with validation metadata
export interface EnrichedPayload {
  originalIntent: Intent;
  enrichedFields: Record<string, any>;
  validationStatus: 'valid' | 'enriched' | 'fallback';
  missingFields: string[];
  inferredFields: Record<string, ContextInference>;
  debugLog: string[];
  canProceed: boolean;
  fallbackReason?: string;
}

/**
 * Context Enrichment Service
 */
export class ContextEnrichmentService {
  private debugLogs: string[] = [];

  /**
   * Validate and enrich workflow payload before API call
   */
  async enrichWorkflowPayload(
    intent: Intent,
    recentTasks: any[] = [],
    contextHistory: string[] = [],
    originalPrompt: string = ''
  ): Promise<EnrichedPayload> {
    this.debugLogs = [];
    this.log(`🔍 Starting payload enrichment for ${intent.type}`, 'info');
    
    // Get requirements for this workflow type
    const requirements = WORKFLOW_REQUIREMENTS[intent.type];
    if (!requirements) {
      this.log(`❌ No requirements found for ${intent.type}`, 'error');
      return this.createFallbackPayload(intent, 'Unknown workflow type');
    }

    // Check which required fields are missing
    const missingFields = this.findMissingFields(intent, requirements);
    this.log(`📋 Required fields check: ${missingFields.length === 0 ? '✅ All present' : `❌ Missing: ${missingFields.join(', ')}`}`, 'info');

    // If no missing fields, payload is valid
    if (missingFields.length === 0) {
      return {
        originalIntent: intent,
        enrichedFields: this.extractIntentFields(intent),
        validationStatus: 'valid',
        missingFields: [],
        inferredFields: {},
        debugLog: this.debugLogs,
        canProceed: true
      };
    }

    // Attempt to infer missing fields
    this.log(`🧠 Attempting to infer missing fields: ${missingFields.join(', ')}`, 'info');
    const inferences = await this.inferMissingFields(
      missingFields,
      intent,
      recentTasks,
      contextHistory,
      originalPrompt
    );

    // Build enriched payload
    const enrichedFields = {
      ...this.extractIntentFields(intent),
      ...this.applyInferences(inferences, missingFields)
    };

    // Apply fallbacks for any still-missing required fields
    const stillMissing = this.findMissingFieldsFromPayload(enrichedFields, requirements);
    if (stillMissing.length > 0) {
      this.log(`🔄 Applying fallbacks for: ${stillMissing.join(', ')}`, 'warn');
      this.applyFallbacks(enrichedFields, stillMissing, requirements);
    }

    // Final validation
    const finalMissing = this.findMissingFieldsFromPayload(enrichedFields, requirements);
    const canProceed = finalMissing.length === 0;

    this.log(`${canProceed ? '✅' : '❌'} Final validation: ${canProceed ? 'Can proceed' : `Still missing: ${finalMissing.join(', ')}`}`, canProceed ? 'success' : 'error');

    return {
      originalIntent: intent,
      enrichedFields,
      validationStatus: canProceed ? 'enriched' : 'fallback',
      missingFields: finalMissing,
      inferredFields: inferences,
      debugLog: this.debugLogs,
      canProceed,
      fallbackReason: canProceed ? undefined : `Could not resolve required fields: ${finalMissing.join(', ')}`
    };
  }

  /**
   * Find missing required fields in intent
   */
  private findMissingFields(intent: Intent, requirements: WorkflowFieldRequirements[string]): string[] {
    const missing: string[] = [];
    
    for (const field of requirements.required) {
      if (!this.hasIntentField(intent, field)) {
        missing.push(field);
      }
    }
    
    return missing;
  }

  /**
   * Find missing fields in built payload
   */
  private findMissingFieldsFromPayload(payload: Record<string, any>, requirements: WorkflowFieldRequirements[string]): string[] {
    const missing: string[] = [];
    
    for (const field of requirements.required) {
      if (!payload[field] || payload[field] === null || payload[field] === undefined || payload[field] === '') {
        missing.push(field);
      }
    }
    
    return missing;
  }

  /**
   * Check if intent has a specific field
   */
  private hasIntentField(intent: Intent, field: string): boolean {
    switch (field) {
      case 'location':
        return !!(intent.location && intent.location.trim() !== '');
      case 'topic':
        return !!(intent.topic && intent.topic.trim() !== '');
      case 'query': // Special case for social post query field
        return !!(intent.topic && intent.topic.trim() !== ''); // Map topic to query
      default:
        return !!(intent as any)[field];
    }
  }

  /**
   * Extract existing fields from intent
   */
  private extractIntentFields(intent: Intent): Record<string, any> {
    const fields: Record<string, any> = {};
    
    if (intent.location) fields.location = intent.location;
    if (intent.topic) {
      fields.topic = intent.topic;
      fields.query = intent.topic; // Map topic to query for social posts
    }
    
    return fields;
  }

  /**
   * Infer missing fields from context
   */
  private async inferMissingFields(
    missingFields: string[],
    intent: Intent,
    recentTasks: any[],
    contextHistory: string[],
    originalPrompt: string
  ): Promise<Record<string, ContextInference>> {
    const inferences: Record<string, ContextInference> = {};

    for (const field of missingFields) {
      const inference = await this.inferSingleField(field, intent, recentTasks, contextHistory, originalPrompt);
      if (inference) {
        inferences[field] = inference;
        this.log(`🎯 Inferred ${field}: "${inference[field]}" (${inference.source}, confidence: ${inference.confidence})`, 'success');
      } else {
        this.log(`❓ Could not infer ${field} from context`, 'warn');
      }
    }

    return inferences;
  }

  /**
   * Infer a single field from context
   */
  private async inferSingleField(
    field: string,
    intent: Intent,
    recentTasks: any[],
    contextHistory: string[],
    originalPrompt: string
  ): Promise<ContextInference | null> {
    
    // Strategy 1: From recent tasks (highest confidence)
    const taskInference = this.inferFromRecentTasks(field, recentTasks, intent.type);
    if (taskInference) {
      return { ...taskInference, confidence: Math.min(0.9, taskInference.confidence + 0.2) };
    }

    // Strategy 2: From context history
    const contextInference = this.inferFromContextHistory(field, contextHistory);
    if (contextInference) {
      return { ...contextInference, confidence: Math.min(0.8, contextInference.confidence + 0.1) };
    }

    // Strategy 3: From prompt analysis
    const promptInference = this.inferFromPrompt(field, originalPrompt);
    if (promptInference) {
      return promptInference;
    }

    // Strategy 4: Smart defaults based on intent type and context
    const smartDefault = this.getSmartDefault(field, intent, recentTasks);
    if (smartDefault) {
      return smartDefault;
    }

    return null;
  }

  /**
   * Infer from recent task history
   */
  private inferFromRecentTasks(field: string, recentTasks: any[], currentIntentType: IntentType): ContextInference | null {
    // Look at the 3 most recent tasks
    const relevantTasks = recentTasks.slice(0, 3);

    for (const task of relevantTasks) {
      let value: string | undefined;
      let confidence = 0.7;

      // Extract field based on task structure
      if (field === 'location') {
        value = task.metadata?.location || this.extractLocationFromTitle(task.title);
        
        // Higher confidence if same task type
        if (task.type === currentIntentType) confidence = 0.8;
        
        // Special boost for CMA tasks when inferring location
        if (task.type === 'CMA' && currentIntentType !== 'CMA') confidence = 0.85;
        
      } else if (field === 'topic' || field === 'query') {
        value = task.metadata?.topic || this.extractTopicFromTitle(task.title);
        
        // Higher confidence for social post tasks
        if (task.type === 'SOCIAL_POST') confidence = 0.8;
      }

      if (value && value.trim() !== '') {
        return {
          [field]: value,
          confidence,
          source: 'recent_task'
        };
      }
    }

    return null;
  }

  /**
   * Infer from context history
   */
  private inferFromContextHistory(field: string, contextHistory: string[]): ContextInference | null {
    // Look at recent context (last 3 items)
    const recentContext = contextHistory.slice(-3);

    for (const context of recentContext.reverse()) { // Start with most recent
      let value: string | undefined;

      if (field === 'location') {
        value = this.extractLocationFromText(context);
      } else if (field === 'topic' || field === 'query') {
        value = this.extractTopicFromText(context);
      }

      if (value && value.trim() !== '') {
        return {
          [field]: value,
          confidence: 0.6,
          source: 'user_context'
        };
      }
    }

    return null;
  }

  /**
   * Infer from original prompt
   */
  private inferFromPrompt(field: string, prompt: string): ContextInference | null {
    if (!prompt || prompt.trim() === '') return null;

    let value: string | undefined;
    let confidence = 0.5;

    if (field === 'location') {
      value = this.extractLocationFromText(prompt);
    } else if (field === 'topic' || field === 'query') {
      value = this.extractTopicFromText(prompt);
      
      // For vague prompts like "make a post for it", extract context
      if (!value && prompt.toLowerCase().includes('post')) {
        value = this.inferTopicFromVaguePrompt(prompt);
        confidence = 0.3;
      }
    }

    if (value && value.trim() !== '') {
      return {
        [field]: value,
        confidence,
        source: 'prompt_analysis'
      };
    }

    return null;
  }

  /**
   * Get smart defaults based on context
   */
  private getSmartDefault(field: string, intent: Intent, recentTasks: any[]): ContextInference | null {
    const requirements = WORKFLOW_REQUIREMENTS[intent.type];
    if (!requirements?.fallbacks[field]) return null;

    let defaultValue = requirements.fallbacks[field];
    let confidence = 0.3;

    // Enhance defaults based on context
    if (field === 'topic' && intent.type === 'SOCIAL_POST') {
      // If we have recent CMA or Market Report tasks, use those as topic context
      const recentPropertyTask = recentTasks.find(task => 
        task.type === 'CMA' || task.type === 'MARKET_REPORT'
      );
      
      if (recentPropertyTask?.metadata?.location) {
        defaultValue = `${recentPropertyTask.metadata.location} property update`;
        confidence = 0.5;
      }
    }

    return {
      [field]: defaultValue,
      confidence,
      source: 'fallback'
    };
  }

  /**
   * Apply inferences to payload
   */
  private applyInferences(inferences: Record<string, ContextInference>, missingFields: string[]): Record<string, any> {
    const enriched: Record<string, any> = {};

    for (const field of missingFields) {
      const inference = inferences[field];
      if (inference && inference[field] !== undefined) {
        enriched[field] = inference[field];
      }
    }

    return enriched;
  }

  /**
   * Apply fallback values
   */
  private applyFallbacks(payload: Record<string, any>, missingFields: string[], requirements: WorkflowFieldRequirements[string]): void {
    for (const field of missingFields) {
      if (requirements.fallbacks[field]) {
        payload[field] = requirements.fallbacks[field];
        this.log(`🔄 Applied fallback for ${field}: ${requirements.fallbacks[field]}`, 'warn');
      }
    }
  }

  /**
   * Create fallback payload when enrichment fails
   */
  private createFallbackPayload(intent: Intent, reason: string): EnrichedPayload {
    return {
      originalIntent: intent,
      enrichedFields: {},
      validationStatus: 'fallback',
      missingFields: [],
      inferredFields: {},
      debugLog: this.debugLogs,
      canProceed: false,
      fallbackReason: reason
    };
  }

  // Utility extraction methods
  private extractLocationFromTitle(title: string): string | undefined {
    // Extract location patterns from task titles
    const patterns = [
      /(?:CMA|report|analysis)\s+(?:for|in)\s+([A-Z][A-Za-z\s]+?)(?:\s+|$)/i,
      /([A-Z][A-Za-z\s]+?)\s+(?:market|property|CMA)/i,
      /(Dubai\s+Marina|Business\s+Bay|Downtown\s+Dubai|Palm\s+Jumeirah|DIFC|JBR)/i
    ];

    for (const pattern of patterns) {
      const match = title.match(pattern);
      if (match && match[1]) {
        return match[1].trim();
      }
    }

    return undefined;
  }

  private extractTopicFromTitle(title: string): string | undefined {
    // Extract topics from task titles
    const lower = title.toLowerCase();
    
    if (lower.includes('villa')) return 'luxury villa listing';
    if (lower.includes('apartment')) return 'apartment listing';
    if (lower.includes('penthouse')) return 'penthouse showcase';
    if (lower.includes('commercial')) return 'commercial property';
    if (lower.includes('social') || lower.includes('post')) return 'property marketing';
    
    return undefined;
  }

  private extractLocationFromText(text: string): string | undefined {
    const patterns = [
      /(Dubai\s+Marina|Business\s+Bay|Downtown\s+Dubai|Palm\s+Jumeirah|DIFC|JBR|Jumeirah)/i,
      /(?:in|at|for)\s+([A-Z][A-Za-z\s]+?)(?:\s|$|,)/i
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        return match[1].trim();
      }
    }

    return undefined;
  }

  private extractTopicFromText(text: string): string | undefined {
    const lower = text.toLowerCase();
    
    if (lower.includes('villa')) return 'luxury villa';
    if (lower.includes('apartment')) return 'apartment';
    if (lower.includes('penthouse')) return 'penthouse';
    if (lower.includes('commercial')) return 'commercial property';
    if (lower.includes('market') && lower.includes('report')) return 'market analysis';
    if (lower.includes('cma')) return 'CMA report';
    
    return undefined;
  }

  private inferTopicFromVaguePrompt(prompt: string): string {
    // Handle vague prompts like "make a post for it"
    const lower = prompt.toLowerCase();
    
    if (lower.includes('post')) return 'property update';
    if (lower.includes('social')) return 'social media content';
    
    return 'real estate content';
  }

  private log(message: string, level: 'info' | 'warn' | 'error' | 'success'): void {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = `[${timestamp}] ${message}`;
    
    this.debugLogs.push(logEntry);
    
    // Console logging with colors
    const colors = {
      info: '\x1b[36m',    // Cyan
      warn: '\x1b[33m',    // Yellow  
      error: '\x1b[31m',   // Red
      success: '\x1b[32m'  // Green
    };
    
    console.log(`${colors[level]}[ContextEnrichment] ${message}\x1b[0m`);
  }
}

// Singleton instance
export const contextEnrichmentService = new ContextEnrichmentService();

/**
 * Main enrichment function - validates and enriches workflow payloads
 */
export async function enrichWorkflowPayload(
  intent: Intent,
  recentTasks: any[] = [],
  contextHistory: string[] = [],
  originalPrompt: string = ''
): Promise<EnrichedPayload> {
  return contextEnrichmentService.enrichWorkflowPayload(
    intent,
    recentTasks,
    contextHistory,
    originalPrompt
  );
}

/**
 * Quick validation check without enrichment
 */
export function validateWorkflowPayload(intent: Intent): { isValid: boolean; missingFields: string[] } {
  const requirements = WORKFLOW_REQUIREMENTS[intent.type];
  if (!requirements) {
    return { isValid: false, missingFields: ['invalid_workflow_type'] };
  }

  const missingFields: string[] = [];
  for (const field of requirements.required) {
    if (!contextEnrichmentService['hasIntentField'](intent, field)) {
      missingFields.push(field);
    }
  }

  return {
    isValid: missingFields.length === 0,
    missingFields
  };
}