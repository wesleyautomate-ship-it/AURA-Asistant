/**
 * Aura v3.0 Context-Aware AI Continuity System
 * 
 * Smart contextual memory for follow-up tasks:
 * ✅ Maintain short-term memory of last 3-5 tasks
 * ✅ Feed context into new orchestrations as metadata
 * ✅ Enable intelligent follow-up chaining 
 * ✅ Visible task lineage and relationship tracking
 * ✅ Contextual prompt enhancement based on history
 * ✅ Smart context decay and relevance scoring
 * ✅ Cross-session context persistence
 * 
 * Features:
 * - Intelligent task relationship detection
 * - Context relevance scoring and decay
 * - Follow-up suggestion engine
 * - Visual task lineage mapping
 * - Contextual prompt enhancement
 * - Cross-session memory persistence
 */

import { useCommandStore } from '../store/commandStore';

// Configuration for AI continuity
const AI_CONTINUITY_CONFIG = {
  MEMORY: {
    MAX_CONTEXT_ITEMS: 5, // Maximum context items to maintain
    CONTEXT_DECAY_HOURS: 24, // Hours before context starts decaying
    RELEVANCE_THRESHOLD: 0.3, // Minimum relevance score to keep context
    RELATIONSHIP_STRENGTH_THRESHOLD: 0.4, // Minimum strength for task relationships
  },
  ENHANCEMENT: {
    ENABLE_PROMPT_ENHANCEMENT: true,
    CONTEXT_INJECTION_TEMPLATE: true,
    FOLLOW_UP_SUGGESTIONS: true,
    TASK_CHAINING_MAX_DEPTH: 3, // Maximum task chain depth
  },
  ANALYSIS: {
    SEMANTIC_SIMILARITY_ENABLED: true, // Would require NLP service
    KEYWORD_EXTRACTION: true,
    TOPIC_CLUSTERING: true,
    TEMPORAL_ANALYSIS: true,
  },
  PERSISTENCE: {
    SAVE_CONTEXT_TO_STORAGE: true,
    CONTEXT_STORAGE_KEY: 'aura_ai_context',
    MAX_STORED_SESSIONS: 10,
    CLEANUP_INTERVAL: 3600000, // 1 hour
  }
};

class AIContinuityService {
  constructor() {
    this.isInitialized = false;
    this.contextMemory = [];
    this.taskLineage = new Map(); // taskId -> relationships
    this.contextGraph = new Map(); // topic -> related tasks
    this.followUpSuggestions = [];
    this.cleanupInterval = null;
    
    this.bindMethods();
    this.loadPersistedContext();
  }

  bindMethods() {
    this.analyzeTaskContext = this.analyzeTaskContext.bind(this);
    this.enhancePrompt = this.enhancePrompt.bind(this);
    this.generateFollowUpSuggestions = this.generateFollowUpSuggestions.bind(this);
    this.performContextCleanup = this.performContextCleanup.bind(this);
  }

  async initialize() {
    if (this.isInitialized) {
      console.log('[AIContinuity] Already initialized');
      return;
    }

    console.log('[AIContinuity] Initializing AI continuity system');
    this.isInitialized = true;

    // Register with command store
    this.registerWithStore();

    // Start cleanup interval
    this.startCleanupProcess();

    // Analyze existing context
    await this.analyzeExistingContext();

    console.log('[AIContinuity] AI continuity system initialized');
  }

  destroy() {
    if (!this.isInitialized) return;

    console.log('[AIContinuity] Destroying AI continuity system');
    
    // Save current context
    this.persistContext();
    
    // Stop cleanup process
    this.stopCleanupProcess();
    
    // Clear memory
    this.contextMemory = [];
    this.taskLineage.clear();
    this.contextGraph.clear();
    this.followUpSuggestions = [];
    
    this.isInitialized = false;
  }

  async analyzeExistingContext() {
    const store = useCommandStore.getState();
    const contextHistory = store.session?.contextHistory || [];
    
    if (contextHistory.length === 0) {
      console.log('[AIContinuity] No existing context to analyze');
      return;
    }

    console.log(`[AIContinuity] Analyzing ${contextHistory.length} existing context items`);

    for (const contextItem of contextHistory.slice(-AI_CONTINUITY_CONFIG.MEMORY.MAX_CONTEXT_ITEMS)) {
      await this.processContextItem(contextItem, 'existing');
    }
  }

  async addTaskToContext(task, result = null) {
    console.log(`[AIContinuity] Adding task to context: ${task.id} (${task.type})`);

    const contextItem = {
      id: task.id,
      type: task.type,
      timestamp: Date.now(),
      data: task.data,
      result: result,
      prompt: this.extractPromptFromTask(task),
      keywords: await this.extractKeywords(task),
      topics: await this.identifyTopics(task),
      relevanceScore: 1.0, // Start with maximum relevance
      relationships: []
    };

    // Analyze relationships with existing context
    contextItem.relationships = await this.findTaskRelationships(contextItem);

    // Add to memory
    this.contextMemory.unshift(contextItem);

    // Maintain memory limits
    if (this.contextMemory.length > AI_CONTINUITY_CONFIG.MEMORY.MAX_CONTEXT_ITEMS) {
      const removed = this.contextMemory.splice(AI_CONTINUITY_CONFIG.MEMORY.MAX_CONTEXT_ITEMS);
      console.log(`[AIContinuity] Removed ${removed.length} old context items`);
    }

    // Update task lineage
    this.updateTaskLineage(contextItem);

    // Update context graph
    this.updateContextGraph(contextItem);

    // Generate new follow-up suggestions
    this.followUpSuggestions = await this.generateFollowUpSuggestions();

    // Persist context
    this.persistContext();

    console.log(`[AIContinuity] Context updated. Memory: ${this.contextMemory.length} items`);
  }

  extractPromptFromTask(task) {
    // Extract the user prompt/intent from task data
    if (task.data?.prompt) return task.data.prompt;
    if (task.data?.transcript) return task.data.transcript;
    if (task.data?.message) return task.data.message;
    
    // Infer prompt from task type
    switch (task.type) {
      case 'transcribe':
        return '[Voice Input]';
      case 'generate_response':
        return task.data?.context || '[AI Generation]';
      case 'save_audio':
        return '[Audio Recording]';
      default:
        return `[${task.type}]`;
    }
  }

  async extractKeywords(task) {
    const text = [
      this.extractPromptFromTask(task),
      task.data?.transcript || '',
      task.result?.transcript || '',
      task.result?.response || ''
    ].filter(Boolean).join(' ');

    // Simple keyword extraction (in production, use NLP service)
    const keywords = this.simpleKeywordExtraction(text);
    return keywords.slice(0, 10); // Top 10 keywords
  }

  simpleKeywordExtraction(text) {
    // Basic keyword extraction - remove common words, get significant terms
    const commonWords = new Set([
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
      'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
      'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were',
      'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
      'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
      'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
      'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their'
    ]);

    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2 && !commonWords.has(word));

    // Count frequency
    const frequency = {};
    words.forEach(word => {
      frequency[word] = (frequency[word] || 0) + 1;
    });

    // Return sorted by frequency
    return Object.entries(frequency)
      .sort((a, b) => b[1] - a[1])
      .map(([word]) => word);
  }

  async identifyTopics(task) {
    const keywords = await this.extractKeywords(task);
    
    // Simple topic identification based on keywords and task type
    const topics = [];
    
    // Real estate related topics
    if (keywords.some(k => ['property', 'home', 'house', 'apartment', 'condo', 'listing', 'buyer', 'seller', 'market'].includes(k))) {
      topics.push('real_estate');
    }
    
    if (keywords.some(k => ['cma', 'comparison', 'market', 'analysis', 'value', 'price', 'pricing'].includes(k))) {
      topics.push('market_analysis');
    }
    
    if (keywords.some(k => ['contract', 'offer', 'agreement', 'terms', 'negotiation'].includes(k))) {
      topics.push('contracts');
    }
    
    if (keywords.some(k => ['client', 'customer', 'buyer', 'seller', 'meeting', 'appointment'].includes(k))) {
      topics.push('client_management');
    }
    
    if (keywords.some(k => ['report', 'document', 'generate', 'create', 'prepare'].includes(k))) {
      topics.push('documentation');
    }
    
    // Task-based topics
    if (task.type === 'transcribe') topics.push('voice_input');
    if (task.type === 'generate_response') topics.push('ai_assistance');
    
    return topics.length > 0 ? topics : ['general'];
  }

  async findTaskRelationships(newContextItem) {
    const relationships = [];

    for (const existingItem of this.contextMemory) {
      const relationship = await this.calculateTaskRelationship(newContextItem, existingItem);
      
      if (relationship.strength > AI_CONTINUITY_CONFIG.MEMORY.RELATIONSHIP_STRENGTH_THRESHOLD) {
        relationships.push({
          taskId: existingItem.id,
          type: relationship.type,
          strength: relationship.strength,
          reason: relationship.reason
        });
      }
    }

    return relationships;
  }

  async calculateTaskRelationship(task1, task2) {
    let strength = 0;
    let type = 'unrelated';
    let reasons = [];

    // Temporal relationship (tasks close in time)
    const timeDiff = Math.abs(task1.timestamp - task2.timestamp);
    if (timeDiff < 600000) { // 10 minutes
      strength += 0.3;
      type = 'temporal';
      reasons.push('occurred within 10 minutes');
    } else if (timeDiff < 3600000) { // 1 hour
      strength += 0.15;
      reasons.push('occurred within 1 hour');
    }

    // Topic similarity
    const commonTopics = task1.topics.filter(topic => task2.topics.includes(topic));
    if (commonTopics.length > 0) {
      strength += 0.4 * (commonTopics.length / Math.max(task1.topics.length, task2.topics.length));
      type = 'topical';
      reasons.push(`shared topics: ${commonTopics.join(', ')}`);
    }

    // Keyword similarity
    const commonKeywords = task1.keywords.filter(keyword => task2.keywords.includes(keyword));
    if (commonKeywords.length > 0) {
      strength += 0.2 * (commonKeywords.length / Math.max(task1.keywords.length, task2.keywords.length));
      reasons.push(`shared keywords: ${commonKeywords.slice(0, 3).join(', ')}`);
    }

    // Task type relationship
    if (task1.type === task2.type) {
      strength += 0.1;
      reasons.push('same task type');
    }

    // Sequential relationship (follow-up patterns)
    if (this.isSequentialPattern(task1, task2)) {
      strength += 0.3;
      type = 'sequential';
      reasons.push('follows sequential pattern');
    }

    return {
      strength: Math.min(1.0, strength),
      type,
      reason: reasons.join('; ')
    };
  }

  isSequentialPattern(task1, task2) {
    // Common real estate workflow patterns
    const patterns = [
      ['transcribe', 'generate_response'], // Voice -> AI response
      ['generate_response', 'save_audio'], // Response -> Save
      ['market_analysis', 'documentation'], // CMA -> Report
      ['client_management', 'documentation'] // Client meeting -> Follow-up docs
    ];

    const type1 = task1.topics.includes('market_analysis') ? 'market_analysis' : task1.type;
    const type2 = task2.topics.includes('market_analysis') ? 'market_analysis' : task2.type;

    return patterns.some(([first, second]) => 
      (type1 === first && type2 === second) ||
      (type2 === first && type1 === second)
    );
  }

  updateTaskLineage(contextItem) {
    this.taskLineage.set(contextItem.id, {
      ...contextItem,
      children: [],
      parents: contextItem.relationships.map(rel => rel.taskId)
    });

    // Update parent-child relationships
    for (const relationship of contextItem.relationships) {
      const parent = this.taskLineage.get(relationship.taskId);
      if (parent && relationship.strength > 0.5) {
        parent.children.push(contextItem.id);
      }
    }
  }

  updateContextGraph(contextItem) {
    for (const topic of contextItem.topics) {
      if (!this.contextGraph.has(topic)) {
        this.contextGraph.set(topic, []);
      }
      this.contextGraph.get(topic).push({
        taskId: contextItem.id,
        timestamp: contextItem.timestamp,
        relevance: contextItem.relevanceScore
      });

      // Keep only recent items per topic
      const topicTasks = this.contextGraph.get(topic);
      if (topicTasks.length > 10) {
        this.contextGraph.set(topic, topicTasks.slice(-10));
      }
    }
  }

  async generateFollowUpSuggestions() {
    if (!AI_CONTINUITY_CONFIG.ENHANCEMENT.FOLLOW_UP_SUGGESTIONS) {
      return [];
    }

    const suggestions = [];
    const recentTasks = this.contextMemory.slice(0, 3);

    for (const task of recentTasks) {
      const taskSuggestions = await this.generateTaskSpecificSuggestions(task);
      suggestions.push(...taskSuggestions);
    }

    // Topic-based suggestions
    const topicSuggestions = await this.generateTopicBasedSuggestions();
    suggestions.push(...topicSuggestions);

    // Remove duplicates and limit
    const uniqueSuggestions = suggestions
      .filter((suggestion, index, array) => 
        array.findIndex(s => s.id === suggestion.id) === index
      )
      .slice(0, 5);

    console.log(`[AIContinuity] Generated ${uniqueSuggestions.length} follow-up suggestions`);
    return uniqueSuggestions;
  }

  async generateTaskSpecificSuggestions(task) {
    const suggestions = [];

    switch (task.type) {
      case 'transcribe':
        if (task.topics.includes('market_analysis')) {
          suggestions.push({
            id: `followup_cma_${task.id}`,
            type: 'generate_cma',
            title: 'Generate CMA Report',
            description: 'Create a comprehensive market analysis report',
            confidence: 0.8,
            relatedTaskId: task.id
          });
        }
        if (task.topics.includes('client_management')) {
          suggestions.push({
            id: `followup_summary_${task.id}`,
            type: 'generate_summary',
            title: 'Create Meeting Summary',
            description: 'Generate a summary of the client interaction',
            confidence: 0.7,
            relatedTaskId: task.id
          });
        }
        break;

      case 'generate_response':
        suggestions.push({
          id: `followup_save_${task.id}`,
          type: 'save_conversation',
          title: 'Save Conversation',
          description: 'Save this conversation for future reference',
          confidence: 0.6,
          relatedTaskId: task.id
        });
        break;
    }

    return suggestions;
  }

  async generateTopicBasedSuggestions() {
    const suggestions = [];
    const topicFrequency = {};

    // Count topic frequency in recent context
    for (const item of this.contextMemory) {
      for (const topic of item.topics) {
        topicFrequency[topic] = (topicFrequency[topic] || 0) + 1;
      }
    }

    // Generate suggestions for frequent topics
    for (const [topic, frequency] of Object.entries(topicFrequency)) {
      if (frequency >= 2) {
        const topicSuggestions = this.getTopicSuggestions(topic, frequency);
        suggestions.push(...topicSuggestions);
      }
    }

    return suggestions;
  }

  getTopicSuggestions(topic, frequency) {
    const suggestions = [];
    const confidence = Math.min(0.9, 0.3 + (frequency * 0.2));

    switch (topic) {
      case 'market_analysis':
        suggestions.push({
          id: `topic_${topic}_trends`,
          type: 'market_trends',
          title: 'Analyze Market Trends',
          description: 'Get insights on current market trends',
          confidence,
          relatedTopic: topic
        });
        break;

      case 'client_management':
        suggestions.push({
          id: `topic_${topic}_followup`,
          type: 'client_followup',
          title: 'Schedule Client Follow-up',
          description: 'Set up follow-up actions for recent client interactions',
          confidence,
          relatedTopic: topic
        });
        break;

      case 'documentation':
        suggestions.push({
          id: `topic_${topic}_organize`,
          type: 'organize_docs',
          title: 'Organize Documents',
          description: 'Review and organize recent documents',
          confidence,
          relatedTopic: topic
        });
        break;
    }

    return suggestions;
  }

  enhancePrompt(originalPrompt, contextOverride = null) {
    if (!AI_CONTINUITY_CONFIG.ENHANCEMENT.ENABLE_PROMPT_ENHANCEMENT) {
      return originalPrompt;
    }

    const relevantContext = this.getRelevantContext(originalPrompt, contextOverride);
    
    if (relevantContext.length === 0) {
      return originalPrompt;
    }

    const contextSummary = this.buildContextSummary(relevantContext);
    const enhancedPrompt = this.injectContext(originalPrompt, contextSummary);

    console.log(`[AIContinuity] Enhanced prompt with ${relevantContext.length} context items`);
    return enhancedPrompt;
  }

  getRelevantContext(prompt, contextOverride = null) {
    if (contextOverride) {
      return contextOverride;
    }

    const promptKeywords = this.simpleKeywordExtraction(prompt.toLowerCase());
    const relevantItems = [];

    for (const item of this.contextMemory) {
      let relevance = 0;

      // Keyword overlap
      const commonKeywords = item.keywords.filter(k => promptKeywords.includes(k));
      relevance += commonKeywords.length * 0.1;

      // Recency boost
      const age = Date.now() - item.timestamp;
      const recencyBoost = Math.max(0, 1 - (age / (24 * 60 * 60 * 1000))); // Decay over 24 hours
      relevance += recencyBoost * 0.3;

      // Task type relevance
      if (item.type === 'transcribe' && promptKeywords.some(k => ['voice', 'said', 'mentioned'].includes(k))) {
        relevance += 0.2;
      }

      if (relevance > AI_CONTINUITY_CONFIG.MEMORY.RELEVANCE_THRESHOLD) {
        relevantItems.push({ ...item, relevance });
      }
    }

    return relevantItems
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, 3); // Top 3 most relevant
  }

  buildContextSummary(relevantContext) {
    const summary = {
      items: relevantContext.length,
      recentPrompts: [],
      keyTopics: [],
      timeline: []
    };

    for (const item of relevantContext) {
      // Recent prompts
      if (item.prompt && item.prompt !== '[Voice Input]') {
        summary.recentPrompts.push({
          prompt: item.prompt.slice(0, 100),
          timestamp: item.timestamp,
          type: item.type
        });
      }

      // Key topics
      summary.keyTopics.push(...item.topics);

      // Timeline
      summary.timeline.push({
        id: item.id,
        type: item.type,
        timestamp: item.timestamp,
        brief: item.prompt?.slice(0, 50) || `[${item.type}]`
      });
    }

    // Remove duplicates and sort
    summary.keyTopics = [...new Set(summary.keyTopics)];
    summary.timeline.sort((a, b) => b.timestamp - a.timestamp);

    return summary;
  }

  injectContext(originalPrompt, contextSummary) {
    if (!AI_CONTINUITY_CONFIG.ENHANCEMENT.CONTEXT_INJECTION_TEMPLATE) {
      return originalPrompt;
    }

    let contextString = '';

    if (contextSummary.recentPrompts.length > 0) {
      contextString += '## Recent Context:\n';
      for (const item of contextSummary.recentPrompts.slice(0, 2)) {
        const timeAgo = this.getTimeAgo(item.timestamp);
        contextString += `- ${timeAgo}: "${item.prompt}"\n`;
      }
      contextString += '\n';
    }

    if (contextSummary.keyTopics.length > 0) {
      contextString += `## Active Topics: ${contextSummary.keyTopics.join(', ')}\n\n`;
    }

    const enhancedPrompt = contextString + '## Current Request:\n' + originalPrompt;
    
    return enhancedPrompt;
  }

  getTimeAgo(timestamp) {
    const now = Date.now();
    const diff = now - timestamp;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  }

  startCleanupProcess() {
    if (this.cleanupInterval) return;

    console.log('[AIContinuity] Starting context cleanup process');
    
    this.cleanupInterval = setInterval(() => {
      this.performContextCleanup();
    }, AI_CONTINUITY_CONFIG.PERSISTENCE.CLEANUP_INTERVAL);
  }

  stopCleanupProcess() {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
      console.log('[AIContinuity] Stopped cleanup process');
    }
  }

  performContextCleanup() {
    console.log('[AIContinuity] Performing context cleanup');
    
    const now = Date.now();
    const decayThreshold = AI_CONTINUITY_CONFIG.MEMORY.CONTEXT_DECAY_HOURS * 60 * 60 * 1000;
    
    let removedCount = 0;

    // Decay relevance scores
    this.contextMemory.forEach(item => {
      const age = now - item.timestamp;
      if (age > decayThreshold) {
        const decayFactor = Math.max(0.1, 1 - ((age - decayThreshold) / decayThreshold));
        item.relevanceScore *= decayFactor;
      }
    });

    // Remove items with low relevance
    const originalLength = this.contextMemory.length;
    this.contextMemory = this.contextMemory.filter(item => 
      item.relevanceScore >= AI_CONTINUITY_CONFIG.MEMORY.RELEVANCE_THRESHOLD
    );
    removedCount = originalLength - this.contextMemory.length;

    if (removedCount > 0) {
      console.log(`[AIContinuity] Cleaned up ${removedCount} low-relevance context items`);
      this.persistContext();
    }
  }

  persistContext() {
    if (!AI_CONTINUITY_CONFIG.PERSISTENCE.SAVE_CONTEXT_TO_STORAGE) return;

    try {
      const contextData = {
        memory: this.contextMemory.slice(0, AI_CONTINUITY_CONFIG.MEMORY.MAX_CONTEXT_ITEMS),
        suggestions: this.followUpSuggestions,
        timestamp: Date.now(),
        sessionId: useCommandStore.getState().session?.id
      };

      localStorage.setItem(
        AI_CONTINUITY_CONFIG.PERSISTENCE.CONTEXT_STORAGE_KEY,
        JSON.stringify(contextData)
      );

      console.log(`[AIContinuity] Persisted ${contextData.memory.length} context items`);
    } catch (error) {
      console.error('[AIContinuity] Failed to persist context:', error);
    }
  }

  loadPersistedContext() {
    if (!AI_CONTINUITY_CONFIG.PERSISTENCE.SAVE_CONTEXT_TO_STORAGE) return;

    try {
      const stored = localStorage.getItem(AI_CONTINUITY_CONFIG.PERSISTENCE.CONTEXT_STORAGE_KEY);
      if (!stored) return;

      const contextData = JSON.parse(stored);
      
      // Check if context is still recent (within 24 hours)
      const age = Date.now() - (contextData.timestamp || 0);
      if (age > 24 * 60 * 60 * 1000) {
        console.log('[AIContinuity] Stored context is too old, skipping load');
        return;
      }

      this.contextMemory = contextData.memory || [];
      this.followUpSuggestions = contextData.suggestions || [];

      // Rebuild derived data structures
      for (const item of this.contextMemory) {
        this.updateTaskLineage(item);
        this.updateContextGraph(item);
      }

      console.log(`[AIContinuity] Loaded ${this.contextMemory.length} persisted context items`);
    } catch (error) {
      console.error('[AIContinuity] Failed to load persisted context:', error);
    }
  }

  registerWithStore() {
    const store = useCommandStore.getState();
    
    // Add AI continuity methods to store
    store.aiContinuity = {
      addTaskToContext: this.addTaskToContext.bind(this),
      enhancePrompt: this.enhancePrompt.bind(this),
      getFollowUpSuggestions: () => this.followUpSuggestions,
      getContextMemory: () => this.contextMemory,
      getTaskLineage: (taskId) => this.taskLineage.get(taskId),
      getContextGraph: () => Object.fromEntries(this.contextGraph),
      getContextStats: () => this.getContextStats()
    };
  }

  getContextStats() {
    const totalTasks = this.contextMemory.length;
    const recentTasks = this.contextMemory.filter(item => 
      Date.now() - item.timestamp < 3600000 // Last hour
    ).length;
    
    const topicDistribution = {};
    this.contextMemory.forEach(item => {
      item.topics.forEach(topic => {
        topicDistribution[topic] = (topicDistribution[topic] || 0) + 1;
      });
    });

    const relationshipCount = this.contextMemory.reduce((sum, item) => 
      sum + item.relationships.length, 0
    );

    return {
      totalTasks,
      recentTasks,
      suggestionsCount: this.followUpSuggestions.length,
      topicDistribution,
      relationshipCount,
      lineageDepth: this.taskLineage.size,
      contextGraphSize: this.contextGraph.size
    };
  }

  // Public API
  getStatus() {
    return {
      isInitialized: this.isInitialized,
      memorySize: this.contextMemory.length,
      suggestionsCount: this.followUpSuggestions.length,
      lineageSize: this.taskLineage.size,
      graphSize: this.contextGraph.size,
      stats: this.getContextStats()
    };
  }
}

// Create singleton instance
const aiContinuityService = new AIContinuityService();

export default aiContinuityService;

// React hook for easy integration
export const useAIContinuity = () => {
  const [status, setStatus] = React.useState(aiContinuityService.getStatus());
  const store = useCommandStore();
  
  React.useEffect(() => {
    // Initialize service
    aiContinuityService.initialize();
    
    // Update status periodically
    const interval = setInterval(() => {
      setStatus(aiContinuityService.getStatus());
    }, 10000);
    
    // Cleanup on unmount
    return () => {
      clearInterval(interval);
      aiContinuityService.destroy();
    };
  }, []);
  
  return {
    ...status,
    followUpSuggestions: store.aiContinuity?.getFollowUpSuggestions() || [],
    enhancePrompt: store.aiContinuity?.enhancePrompt,
    addTaskToContext: store.aiContinuity?.addTaskToContext,
    contextMemory: store.aiContinuity?.getContextMemory() || []
  };
};