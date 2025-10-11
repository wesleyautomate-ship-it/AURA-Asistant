/**
 * Memory Service v3.3
 * ====================
 * 
 * Intelligent memory layer that extends existing commandStore
 * to provide context-aware content generation with semantic recall.
 * 
 * Integrates with: commandStore.ts, contextEnrichment.ts
 */

import { useCommandStore } from '../../store/commandStore';

export interface AgentProfile {
  id: string;
  name: string;
  specialties: string[];
  voice_preferences: {
    tone: 'professional' | 'casual' | 'expert' | 'friendly';
    style: string;
  };
  brand_preferences?: {
    colors: string[];
    fonts: string[];
    logo_url?: string;
  };
  created_at: Date;
  updated_at: Date;
}

export interface PropertyRecord {
  id: string;
  address: string;
  property_type: string;
  market_data: {
    current_price?: number;
    estimated_value?: number;
    market_trends: string[];
  };
  context_usage: number;
  last_referenced: Date;
}

export interface ContentMemory {
  id: string;
  request_id: string;
  content_type: string;
  generated_content: any;
  quality_score: number;
  context_used: string[];
  success_metrics?: {
    user_satisfaction?: number;
    reuse_count?: number;
  };
  created_at: Date;
}

export interface MemoryContext {
  agents: AgentProfile[];
  properties: PropertyRecord[];
  recent_content: ContentMemory[];
  conversation_history: string[];
  user_preferences: Record<string, any>;
}

class MemoryService {
  private static instance: MemoryService;
  
  public static getInstance(): MemoryService {
    if (!MemoryService.instance) {
      MemoryService.instance = new MemoryService();
    }
    return MemoryService.instance;
  }

  /**
   * Store agent profile with intelligent defaults
   */
  async upsertAgent(agent: Partial<AgentProfile> & { id: string; name: string }): Promise<void> {
    const store = useCommandStore.getState();
    
    const fullAgent: AgentProfile = {
      ...agent,
      specialties: agent.specialties || [],
      voice_preferences: agent.voice_preferences || {
        tone: 'professional',
        style: 'clear and informative'
      },
      created_at: new Date(),
      updated_at: new Date(),
    } as AgentProfile;
    
    console.log('[Memory] Storing agent profile:', fullAgent.name);
    
    // Store in existing user session or create new memory store
    // For now, we'll use browser localStorage as the memory backend
    this.storeInMemory('agents', fullAgent.id, fullAgent);
  }

  /**
   * Store property record with market context
   */
  async upsertProperty(property: Partial<PropertyRecord> & { id: string; address: string }): Promise<void> {
    const fullProperty: PropertyRecord = {
      ...property,
      property_type: property.property_type || 'mixed',
      market_data: property.market_data || {
        market_trends: []
      },
      context_usage: property.context_usage || 0,
      last_referenced: new Date(),
    } as PropertyRecord;
    
    console.log('[Memory] Storing property record:', fullProperty.address);
    this.storeInMemory('properties', fullProperty.id, fullProperty);
  }

  /**
   * Store generated content for future reference
   */
  async storeContent(content: Partial<ContentMemory> & { 
    request_id: string; 
    content_type: string; 
    generated_content: any;
  }): Promise<void> {
    const fullContent: ContentMemory = {
      ...content,
      id: content.id || `content_${Date.now()}`,
      quality_score: content.quality_score || 0.8,
      context_used: content.context_used || [],
      created_at: new Date(),
    } as ContentMemory;
    
    console.log('[Memory] Storing content memory:', fullContent.content_type);
    this.storeInMemory('content', fullContent.id, fullContent);
  }

  /**
   * Semantic recall - find relevant memories based on query
   */
  async recall(query: string, options: { 
    limit?: number;
    content_types?: string[];
    time_window?: number; // days
  } = {}): Promise<{
    agents: AgentProfile[];
    properties: PropertyRecord[];
    content: ContentMemory[];
    relevance_score: number;
  }> {
    console.log('[Memory] Performing semantic recall for:', query);
    
    const { limit = 5, content_types = [], time_window = 30 } = options;
    
    // Simple text-based matching for now (in production, use embeddings)
    const queryLower = query.toLowerCase();
    
    const agents = this.searchMemory<AgentProfile>('agents', (agent) => 
      agent.name.toLowerCase().includes(queryLower) ||
      agent.specialties.some(s => s.toLowerCase().includes(queryLower))
    ).slice(0, limit);
    
    const properties = this.searchMemory<PropertyRecord>('properties', (prop) => 
      prop.address.toLowerCase().includes(queryLower) ||
      prop.property_type.toLowerCase().includes(queryLower)
    ).slice(0, limit);
    
    const content = this.searchMemory<ContentMemory>('content', (cont) => 
      (content_types.length === 0 || content_types.includes(cont.content_type)) &&
      this.isWithinTimeWindow(cont.created_at, time_window)
    ).slice(0, limit);
    
    const relevanceScore = this.calculateRelevanceScore(query, { agents, properties, content });
    
    console.log(`[Memory] Found ${agents.length} agents, ${properties.length} properties, ${content.length} content items`);
    
    return {
      agents,
      properties,
      content,
      relevance_score: relevanceScore,
    };
  }

  /**
   * Build enriched context for content generation
   */
  async buildContext(query: string, requestId: string): Promise<MemoryContext> {
    const recalled = await this.recall(query);
    const store = useCommandStore.getState();
    
    return {
      agents: recalled.agents,
      properties: recalled.properties,
      recent_content: recalled.content,
      conversation_history: this.getRecentConversation(store.chatHistory, 10),
      user_preferences: this.getUserPreferences(),
    };
  }

  /**
   * Update context usage tracking
   */
  async updateUsage(entityId: string, entityType: 'agent' | 'property' | 'content'): Promise<void> {
    const key = entityType === 'agent' ? 'agents' : 
                entityType === 'property' ? 'properties' : 'content';
    
    const entity = this.getFromMemory(key, entityId);
    if (entity) {
      if ('context_usage' in entity) {
        entity.context_usage++;
      }
      if ('last_referenced' in entity) {
        entity.last_referenced = new Date();
      }
      this.storeInMemory(key, entityId, entity);
    }
  }

  // Private helper methods

  private storeInMemory(collection: string, id: string, data: any): void {
    const key = `aura_memory_${collection}`;
    const existing = JSON.parse(localStorage.getItem(key) || '{}');
    existing[id] = data;
    localStorage.setItem(key, JSON.stringify(existing));
  }

  private getFromMemory<T>(collection: string, id: string): T | null {
    const key = `aura_memory_${collection}`;
    const existing = JSON.parse(localStorage.getItem(key) || '{}');
    return existing[id] || null;
  }

  private searchMemory<T>(collection: string, predicate: (item: T) => boolean): T[] {
    const key = `aura_memory_${collection}`;
    const existing = JSON.parse(localStorage.getItem(key) || '{}');
    return Object.values(existing).filter(predicate) as T[];
  }

  private isWithinTimeWindow(date: Date | string, windowDays: number): boolean {
    const itemDate = typeof date === 'string' ? new Date(date) : date;
    const cutoff = new Date(Date.now() - windowDays * 24 * 60 * 60 * 1000);
    return itemDate >= cutoff;
  }

  private calculateRelevanceScore(query: string, results: any): number {
    // Simple relevance scoring - in production, use semantic similarity
    const totalItems = results.agents.length + results.properties.length + results.content.length;
    return Math.min(totalItems / 10, 1.0); // Normalize to 0-1
  }

  private getRecentConversation(history: any[], limit: number): string[] {
    if (!Array.isArray(history)) return [];
    return history
      .slice(-limit)
      .map(item => typeof item === 'string' ? item : item.message || '')
      .filter(msg => msg.trim().length > 0);
  }

  private getUserPreferences(): Record<string, any> {
    return JSON.parse(localStorage.getItem('aura_user_preferences') || '{}');
  }
}

// Export singleton instance
export const memoryService = MemoryService.getInstance();