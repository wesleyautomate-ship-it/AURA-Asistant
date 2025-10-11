/**
 * Memory Service - Content Intelligence Layer
 * ==========================================
 * 
 * Provides persistent memory capabilities for Aura v3.3 intelligent content generation:
 * - Entity memory (agent profiles, brand kits, properties, neighborhoods)
 * - Task memory (conversation context, decisions, generated artifacts)
 * - Semantic retrieval for contextual content generation
 * 
 * Version: 3.3.0
 * Phase: Content Intelligence Layer
 */

import { ContentType } from '../../types/contentSchemas';

// =============================================================================
// ENTITY MEMORY TYPES
// =============================================================================

export interface AgentProfile {
  id: string;
  name: string;
  brokerage: string;
  specialties: string[];
  markets: string[];
  experience_years: number;
  bio: string;
  contact: {
    email: string;
    phone: string;
    website?: string;
  };
  voice_preferences: {
    tone: 'professional' | 'friendly' | 'authoritative' | 'casual';
    style: 'concise' | 'detailed' | 'storytelling';
    avoid_terms?: string[];
  };
  branding: {
    colors: {
      primary: string;
      secondary: string;
      accent?: string;
    };
    fonts: {
      headings: string;
      body: string;
    };
    logo_url?: string;
  };
  created_at: string;
  updated_at: string;
}

export interface PropertyRecord {
  id: string;
  mls_id?: string;
  address: string;
  type: 'residential' | 'commercial' | 'land' | 'mixed';
  details: {
    sqft?: number;
    bedrooms?: number;
    bathrooms?: number;
    year_built?: number;
    lot_size?: string;
    price?: number;
    price_history?: Array<{
      date: string;
      price: number;
      event: 'listing' | 'price_change' | 'sale' | 'withdrawal';
    }>;
  };
  location: {
    neighborhood: string;
    city: string;
    state: string;
    zip: string;
    lat?: number;
    lng?: number;
  };
  market_data: {
    comparables?: Array<{
      address: string;
      price: number;
      sqft: number;
      distance_miles: number;
      sold_date: string;
    }>;
    neighborhood_stats?: {
      median_price: number;
      avg_days_on_market: number;
      price_trend: 'up' | 'down' | 'stable';
    };
  };
  images?: Array<{
    url: string;
    type: 'exterior' | 'interior' | 'amenity';
    description?: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface NeighborhoodFacts {
  id: string;
  name: string;
  city: string;
  state: string;
  demographics: {
    population?: number;
    median_income?: number;
    avg_age?: number;
  };
  amenities: string[];
  schools?: Array<{
    name: string;
    type: 'elementary' | 'middle' | 'high';
    rating?: number;
  }>;
  transportation: {
    walkability_score?: number;
    public_transit?: string[];
    major_highways?: string[];
  };
  development: {
    upcoming_projects?: string[];
    recent_developments?: string[];
  };
  created_at: string;
  updated_at: string;
}

export interface GeneratedArtifact {
  id: string;
  task_id: string;
  content_type: ContentType;
  title: string;
  content: any; // The actual generated content
  metadata: {
    template_used: string;
    brand_compliance_score?: number;
    generation_params: Record<string, any>;
    validation_results?: Record<string, any>;
  };
  related_entities: {
    agent_id?: string;
    property_id?: string;
    neighborhood_id?: string;
  };
  usage_context: {
    campaign_id?: string;
    channel: string;
    target_audience?: string;
  };
  created_at: string;
  updated_at: string;
}

// =============================================================================
// TASK MEMORY TYPES
// =============================================================================

export interface TaskMemory {
  session_id: string;
  task_id: string;
  conversation_context: {
    user_prompts: Array<{
      timestamp: string;
      prompt: string;
      intent: string;
      entities_extracted: Record<string, any>;
    }>;
    ai_responses: Array<{
      timestamp: string;
      response: string;
      content_generated?: string;
      confidence_score?: number;
    }>;
    decisions_made: Array<{
      timestamp: string;
      decision_point: string;
      choice: string;
      reasoning: string;
    }>;
  };
  context_continuity: {
    current_property?: string;
    current_campaign?: string;
    active_brand_kit?: string;
    carry_forward: Record<string, any>;
  };
  created_at: string;
  updated_at: string;
}

// =============================================================================
// MEMORY SERVICE INTERFACE
// =============================================================================

export interface MemoryQueryOptions {
  limit?: number;
  relevance_threshold?: number;
  entity_types?: string[];
  time_window?: {
    start: string;
    end: string;
  };
  scope?: {
    org_id?: string;
    user_id?: string;
    session_id?: string;
  };
}

export interface MemoryRecallResult {
  entity: any;
  relevance_score: number;
  last_used: string;
  usage_count: number;
}

export class MemoryService {
  private static instance: MemoryService;
  private memoryCache: Map<string, any> = new Map();
  private embeddings: Map<string, number[]> = new Map();

  private constructor() {
    this.initializeMemoryService();
  }

  public static getInstance(): MemoryService {
    if (!MemoryService.instance) {
      MemoryService.instance = new MemoryService();
    }
    return MemoryService.instance;
  }

  private async initializeMemoryService(): Promise<void> {
    console.log('[MemoryService] Initializing content intelligence memory...');
    
    // Initialize in-memory cache
    this.memoryCache.clear();
    
    // In a real implementation, this would connect to:
    // - Postgres for structured entity data
    // - pgvector for semantic embeddings
    // - Redis for hot cache and session data
    
    console.log('[MemoryService] Memory service initialized');
  }

  // =============================================================================
  // ENTITY MEMORY OPERATIONS
  // =============================================================================

  public async upsertAgent(agent: AgentProfile): Promise<void> {
    console.log(`[MemoryService] Upserting agent profile: ${agent.name}`);
    
    const key = `agent:${agent.id}`;
    this.memoryCache.set(key, {
      ...agent,
      updated_at: new Date().toISOString()
    });
    
    // Generate embeddings for semantic search
    await this.generateEntityEmbedding(key, this.serializeAgentForEmbedding(agent));
  }

  public async upsertProperty(property: PropertyRecord): Promise<void> {
    console.log(`[MemoryService] Upserting property: ${property.address}`);
    
    const key = `property:${property.id}`;
    this.memoryCache.set(key, {
      ...property,
      updated_at: new Date().toISOString()
    });
    
    await this.generateEntityEmbedding(key, this.serializePropertyForEmbedding(property));
  }

  public async upsertNeighborhood(neighborhood: NeighborhoodFacts): Promise<void> {
    console.log(`[MemoryService] Upserting neighborhood: ${neighborhood.name}`);
    
    const key = `neighborhood:${neighborhood.id}`;
    this.memoryCache.set(key, {
      ...neighborhood,
      updated_at: new Date().toISOString()
    });
    
    await this.generateEntityEmbedding(key, this.serializeNeighborhoodForEmbedding(neighborhood));
  }

  public async upsertArtifact(artifact: GeneratedArtifact): Promise<void> {
    console.log(`[MemoryService] Upserting generated artifact: ${artifact.title}`);
    
    const key = `artifact:${artifact.id}`;
    this.memoryCache.set(key, {
      ...artifact,
      updated_at: new Date().toISOString()
    });
    
    await this.generateEntityEmbedding(key, this.serializeArtifactForEmbedding(artifact));
  }

  // =============================================================================
  // TASK MEMORY OPERATIONS
  // =============================================================================

  public async upsertTaskMemory(taskMemory: TaskMemory): Promise<void> {
    console.log(`[MemoryService] Upserting task memory: ${taskMemory.task_id}`);
    
    const key = `task:${taskMemory.task_id}`;
    this.memoryCache.set(key, {
      ...taskMemory,
      updated_at: new Date().toISOString()
    });
  }

  public async getTaskMemory(taskId: string): Promise<TaskMemory | null> {
    const key = `task:${taskId}`;
    const memory = this.memoryCache.get(key);
    
    if (memory) {
      console.log(`[MemoryService] Retrieved task memory for: ${taskId}`);
    }
    
    return memory || null;
  }

  public async addToTaskContext(
    taskId: string, 
    contextType: 'user_prompt' | 'ai_response' | 'decision',
    contextData: any
  ): Promise<void> {
    const existing = await this.getTaskMemory(taskId);
    
    if (!existing) {
      // Create new task memory
      const newTaskMemory: TaskMemory = {
        session_id: contextData.session_id || 'unknown',
        task_id: taskId,
        conversation_context: {
          user_prompts: [],
          ai_responses: [],
          decisions_made: []
        },
        context_continuity: {},
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      await this.upsertTaskMemory(newTaskMemory);
    }
    
    const memory = await this.getTaskMemory(taskId);
    if (!memory) return;
    
    // Add context based on type
    switch (contextType) {
      case 'user_prompt':
        memory.conversation_context.user_prompts.push({
          timestamp: new Date().toISOString(),
          prompt: contextData.prompt,
          intent: contextData.intent || 'unknown',
          entities_extracted: contextData.entities || {}
        });
        break;
        
      case 'ai_response':
        memory.conversation_context.ai_responses.push({
          timestamp: new Date().toISOString(),
          response: contextData.response,
          content_generated: contextData.content_generated,
          confidence_score: contextData.confidence_score
        });
        break;
        
      case 'decision':
        memory.conversation_context.decisions_made.push({
          timestamp: new Date().toISOString(),
          decision_point: contextData.decision_point,
          choice: contextData.choice,
          reasoning: contextData.reasoning
        });
        break;
    }
    
    await this.upsertTaskMemory(memory);
  }

  // =============================================================================
  // SEMANTIC RECALL OPERATIONS
  // =============================================================================

  public async recall(
    query: string,
    options: MemoryQueryOptions = {}
  ): Promise<MemoryRecallResult[]> {
    console.log(`[MemoryService] Recalling memories for query: "${query}"`);
    
    // Generate query embedding
    const queryEmbedding = await this.generateQueryEmbedding(query);
    
    // Find most relevant entities
    const results: MemoryRecallResult[] = [];
    const limit = options.limit || 10;
    const threshold = options.relevance_threshold || 0.7;
    
    for (const [key, embedding] of this.embeddings.entries()) {
      const similarity = this.calculateCosineSimilarity(queryEmbedding, embedding);
      
      if (similarity >= threshold) {
        const entity = this.memoryCache.get(key);
        if (entity) {
          results.push({
            entity,
            relevance_score: similarity,
            last_used: entity.updated_at || entity.created_at,
            usage_count: 1 // In real implementation, track actual usage
          });
        }
      }
    }
    
    // Sort by relevance and limit
    const sortedResults = results
      .sort((a, b) => b.relevance_score - a.relevance_score)
      .slice(0, limit);
    
    console.log(`[MemoryService] Found ${sortedResults.length} relevant memories`);
    
    return sortedResults;
  }

  public async recallByEntityType(
    entityType: string,
    options: MemoryQueryOptions = {}
  ): Promise<MemoryRecallResult[]> {
    console.log(`[MemoryService] Recalling entities of type: ${entityType}`);
    
    const results: MemoryRecallResult[] = [];
    const limit = options.limit || 10;
    
    for (const [key, entity] of this.memoryCache.entries()) {
      if (key.startsWith(`${entityType}:`)) {
        results.push({
          entity,
          relevance_score: 1.0,
          last_used: entity.updated_at || entity.created_at,
          usage_count: 1
        });
      }
    }
    
    return results.slice(0, limit);
  }

  public async getContextSummary(
    taskId: string,
    includeArtifacts: boolean = true
  ): Promise<{
    conversation_summary: string;
    key_entities: any[];
    recent_decisions: any[];
    related_artifacts?: any[];
  }> {
    const taskMemory = await this.getTaskMemory(taskId);
    
    if (!taskMemory) {
      return {
        conversation_summary: 'No conversation context found',
        key_entities: [],
        recent_decisions: []
      };
    }
    
    // Generate conversation summary
    const recentPrompts = taskMemory.conversation_context.user_prompts.slice(-3);
    const recentResponses = taskMemory.conversation_context.ai_responses.slice(-3);
    
    const conversationSummary = this.summarizeConversation(recentPrompts, recentResponses);
    
    // Get key entities mentioned in conversation
    const keyEntities = await this.extractKeyEntitiesFromMemory(taskMemory);
    
    // Get recent decisions
    const recentDecisions = taskMemory.conversation_context.decisions_made.slice(-5);
    
    const result: any = {
      conversation_summary: conversationSummary,
      key_entities: keyEntities,
      recent_decisions: recentDecisions
    };
    
    // Include related artifacts if requested
    if (includeArtifacts) {
      result.related_artifacts = await this.getRelatedArtifacts(taskId);
    }
    
    return result;
  }

  // =============================================================================
  // EMBEDDING OPERATIONS (MOCK IMPLEMENTATION)
  // =============================================================================

  private async generateEntityEmbedding(key: string, text: string): Promise<void> {
    // In real implementation, this would use OpenAI embeddings or similar
    // For now, generate a mock embedding based on text hash
    const embedding = this.mockEmbedding(text);
    this.embeddings.set(key, embedding);
  }

  private async generateQueryEmbedding(query: string): Promise<number[]> {
    return this.mockEmbedding(query);
  }

  private mockEmbedding(text: string): number[] {
    // Generate a consistent 768-dimensional mock embedding
    const dimensions = 768;
    const embedding = new Array(dimensions);
    
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    
    for (let i = 0; i < dimensions; i++) {
      // Use hash and position to generate consistent values
      const seed = hash + i;
      embedding[i] = (Math.sin(seed) + 1) / 2; // Normalize to [0, 1]
    }
    
    return embedding;
  }

  private calculateCosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) return 0;
    
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    if (normA === 0 || normB === 0) return 0;
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  // =============================================================================
  // SERIALIZATION HELPERS
  // =============================================================================

  private serializeAgentForEmbedding(agent: AgentProfile): string {
    return [
      agent.name,
      agent.brokerage,
      agent.specialties.join(' '),
      agent.markets.join(' '),
      agent.bio,
      agent.voice_preferences.tone,
      agent.voice_preferences.style
    ].join(' ').toLowerCase();
  }

  private serializePropertyForEmbedding(property: PropertyRecord): string {
    return [
      property.address,
      property.type,
      property.location.neighborhood,
      property.location.city,
      property.location.state,
      property.details.bedrooms?.toString() || '',
      property.details.bathrooms?.toString() || '',
      property.details.sqft?.toString() || ''
    ].join(' ').toLowerCase();
  }

  private serializeNeighborhoodForEmbedding(neighborhood: NeighborhoodFacts): string {
    return [
      neighborhood.name,
      neighborhood.city,
      neighborhood.state,
      neighborhood.amenities.join(' '),
      neighborhood.schools?.map(s => s.name).join(' ') || '',
      neighborhood.transportation.public_transit?.join(' ') || ''
    ].join(' ').toLowerCase();
  }

  private serializeArtifactForEmbedding(artifact: GeneratedArtifact): string {
    return [
      artifact.title,
      artifact.content_type,
      artifact.metadata.template_used,
      JSON.stringify(artifact.content).substring(0, 500)
    ].join(' ').toLowerCase();
  }

  private summarizeConversation(prompts: any[], responses: any[]): string {
    if (prompts.length === 0) return 'No conversation history';
    
    const recentPrompt = prompts[prompts.length - 1];
    const recentResponse = responses[responses.length - 1];
    
    return `Recent conversation focused on "${recentPrompt.intent}" with user asking about "${recentPrompt.prompt.substring(0, 100)}...". AI provided response with ${recentResponse?.confidence_score ? Math.round(recentResponse.confidence_score * 100) + '%' : 'unknown'} confidence.`;
  }

  private async extractKeyEntitiesFromMemory(taskMemory: TaskMemory): Promise<any[]> {
    // Extract entities from conversation context
    const entities: any[] = [];
    
    for (const prompt of taskMemory.conversation_context.user_prompts) {
      if (prompt.entities_extracted) {
        Object.entries(prompt.entities_extracted).forEach(([key, value]) => {
          entities.push({ type: key, value, source: 'user_prompt' });
        });
      }
    }
    
    return entities.slice(0, 10); // Return top 10 entities
  }

  private async getRelatedArtifacts(taskId: string): Promise<any[]> {
    const artifacts: any[] = [];
    
    for (const [key, entity] of this.memoryCache.entries()) {
      if (key.startsWith('artifact:') && entity.task_id === taskId) {
        artifacts.push(entity);
      }
    }
    
    return artifacts.slice(0, 5); // Return up to 5 related artifacts
  }

  // =============================================================================
  // CLEANUP AND MAINTENANCE
  // =============================================================================

  public async cleanup(options: {
    older_than_days?: number;
    entity_types?: string[];
  } = {}): Promise<void> {
    console.log('[MemoryService] Starting memory cleanup...');
    
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - (options.older_than_days || 90));
    
    let cleanedCount = 0;
    
    for (const [key, entity] of this.memoryCache.entries()) {
      const entityDate = new Date(entity.updated_at || entity.created_at);
      
      if (entityDate < cutoffDate) {
        this.memoryCache.delete(key);
        this.embeddings.delete(key);
        cleanedCount++;
      }
    }
    
    console.log(`[MemoryService] Cleaned up ${cleanedCount} old memory entries`);
  }

  public getStats(): {
    total_entities: number;
    by_type: Record<string, number>;
    memory_size_mb: number;
    embedding_count: number;
  } {
    const byType: Record<string, number> = {};
    
    for (const key of this.memoryCache.keys()) {
      const type = key.split(':')[0];
      byType[type] = (byType[type] || 0) + 1;
    }
    
    return {
      total_entities: this.memoryCache.size,
      by_type: byType,
      memory_size_mb: Math.round((JSON.stringify(Array.from(this.memoryCache.values())).length) / 1024 / 1024 * 100) / 100,
      embedding_count: this.embeddings.size
    };
  }
}

// =============================================================================
// SINGLETON EXPORT
// =============================================================================

export default MemoryService.getInstance();