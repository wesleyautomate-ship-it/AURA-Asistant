import { IntelligenceContent as ApiIntelligenceContent } from '../types/intelligence';
import { IntelligenceContent as StoreIntelligenceContent } from '../store/commandStore';

const normalizeMemoryValue = (input: unknown, index: number): string => {
  if (!input) {
    return `Memory ${index + 1}`;
  }

  if (typeof input === 'string') {
    return input;
  }

  if (typeof input === 'object') {
    const record = input as Record<string, unknown>;
    const candidate = record['title'] || record['summary'] || record['description'];
    if (typeof candidate === 'string' && candidate.trim().length > 0) {
      return candidate;
    }
    try {
      return JSON.stringify(record);
    } catch (error) {
      console.warn('[IntelContent] Failed to stringify memory context entry', error);
    }
  }

  return `Memory ${index + 1}`;
};

export const mapApiIntelligenceContent = (content: ApiIntelligenceContent): StoreIntelligenceContent => {
  const relevantMemories = (content.memory_context.relevant_memories || []).map((item, index) =>
    normalizeMemoryValue(item, index)
  );

  const structured = content.generated_content.structured || {};
  const keyInsights = content.generated_content.key_insights || [];
  const actionableRecommendations = content.generated_content.actionable_recommendations || [];
  const sources = content.metadata.sources || [];

  return {
    contentId: content.content_id,
    taskId: content.task_id,
    contentType: content.content_type,
    title: content.title,
    enhanced: content.enhanced,
    qualityScore: content.quality_scores?.overall_score ?? 0,
    memoryContext: {
      relevantMemories,
      contextualInsights: content.memory_context.contextual_insights || [],
      brandAlignment: content.memory_context.brand_alignment ?? 0.8
    },
    generatedContent: {
      structured,
      narrative: content.generated_content.narrative || '',
      keyInsights,
      actionableRecommendations
    },
    metadata: {
      generationTimestamp: new Date(content.metadata.generation_timestamp).toISOString(),
      model: content.metadata.model,
      processingTime: content.metadata.processing_time_ms ?? 0,
      confidenceLevel: content.metadata.confidence_level ?? 0.8,
      sources,
      listingId: content.metadata.listing_id || undefined
    },
    exportReady: content.export_ready ?? true,
    version: content.version || '3.4'
  };
};

export default mapApiIntelligenceContent;
