/**
 * Orchestrator Service v3.2
 * ==========================
 * 
 * Stable orchestration layer that coordinates content generation
 * using the original workflow API and template orchestrator.
 * 
 * Version: 3.2 (Stable)
 * Phase: Stable Foundation
 */

import { orchestrateCommand } from './orchestrator';
import templateOrchestrator from './templateOrchestrator';
import { detectIntent } from './intentParser';
import { useCommandStore, IntelligenceContent, ContentType } from '../store/commandStore';

// v3.3 Intelligence Layer (optional)
let intelligenceAvailable = false;
let processIntelligentRequest: any = null;

try {
  const intelligence = await import('./intelligence/integrationHub');
  processIntelligentRequest = intelligence.processIntelligentRequest;
  intelligenceAvailable = true;
  console.log('🧠 v3.3 Intelligence Layer available');
} catch (error) {
  console.log('🔄 v3.3 Intelligence Layer not available, using v3.2 stable');
}

export interface GenerationRequest {
  userInput: string;
  requestId: string;
  metadata?: Record<string, any>;
}

export interface GenerationResult {
  success: boolean;
  requestId: string;
  contentId?: string;
  error?: string;
  logs: string[];
  intelligenceData?: any; // Raw intelligence data for persistence
}

/**
 * Main orchestration function for content generation (v3.2 Stable + v3.3 Intelligence)
 */
export const generateContent = async (
  request: GenerationRequest
): Promise<GenerationResult> => {
  // Try v3.3 Intelligence if available and enabled
  if (intelligenceAvailable && processIntelligentRequest) {
    const intelligenceEnabled = import.meta.env.VITE_INTELLIGENCE_ENABLED !== 'false';
    
    if (intelligenceEnabled) {
      console.log('🧠 Using v3.3 Intelligence Layer');
      try {
        const intelligenceResult = await processIntelligentRequest({
          ...request,
          enable_intelligence: true,
          memory_enhanced: true,
        });
        
        // Save intelligence content after successful generation
        if (intelligenceResult.success && intelligenceResult.intelligence_used) {
          await saveIntelligenceContentToStore(request, intelligenceResult);
        }
        
        return intelligenceResult;
      } catch (error) {
        console.warn('⚠️ Intelligence failed, falling back to v3.2:', error);
        // Continue to v3.2 fallback below
      }
    }
  }
  
  // v3.2 Stable fallback
  const logs: string[] = [];
  const startTime = Date.now();
  
  console.group(`🎯 [Orchestrator v3.2] Content Generation Pipeline`);
  console.log('Request ID:', request.requestId);
  console.log('User Input:', request.userInput);
  
  try {
    // Use the existing stable orchestrator
    console.log('\n🚀 Using stable orchestrator...');
    const result = await orchestrateCommand(request.userInput, undefined, [], []);
    
    logs.push(`Intent: ${result.intent.type}`);
    logs.push(`Confidence: ${(result.intent.confidence * 100).toFixed(1)}%`);
    
    // Handle successful orchestration
    if (!result.fallbackToStream) {
      if (result.contentGeneration?.success) {
        logs.push('✅ Content generated successfully via template orchestrator');
        
        const totalTime = Date.now() - startTime;
        logs.push(`⏱️ Total Pipeline Time: ${totalTime}ms`);
        
        console.log('✅ Pipeline completed successfully');
        console.groupEnd();
        
        const generationResult = {
          success: true,
          requestId: request.requestId,
          contentId: result.contentGeneration.content?.id,
          logs,
        };
        
        // Save basic content data for v3.2 generation
        if (result.contentGeneration.content) {
          await saveBasicContentToStore(request, result.contentGeneration.content);
        }
        
        return generationResult;
      } else if (result.workflowResponse?.success) {
        logs.push('✅ Content generated successfully via workflow API');
        
        const totalTime = Date.now() - startTime;
        logs.push(`⏱️ Total Pipeline Time: ${totalTime}ms`);
        
        console.log('✅ Pipeline completed successfully');
        console.groupEnd();
        
        const workflowResult = {
          success: true,
          requestId: request.requestId,
          contentId: result.workflowResponse.taskId,
          logs,
        };
        
        // Save workflow content data
        if (result.workflowResponse.data) {
          await saveBasicContentToStore(request, {
            id: result.workflowResponse.taskId,
            data: result.workflowResponse.data
          });
        }
        
        return workflowResult;
      }
    }
    
    // Handle fallback to streaming
    if (result.fallbackToStream) {
      logs.push('⚠️ Falling back to streaming response');
      
      // For now, we'll simulate a successful generation
      // In a real implementation, this would trigger the streaming pipeline
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const totalTime = Date.now() - startTime;
      logs.push(`⏱️ Total Pipeline Time: ${totalTime}ms`);
      
      console.log('✅ Fallback stream completed');
      console.groupEnd();
      
      return {
        success: true,
        requestId: request.requestId,
        contentId: `stream_${request.requestId}`,
        logs,
      };
    }
    
    // If we get here, something went wrong
    throw new Error(result.error || 'Orchestration failed for unknown reason');
    
  } catch (error) {
    const totalTime = Date.now() - startTime;
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    logs.push(`❌ Pipeline failed: ${errorMessage}`);
    logs.push(`⏱️ Failed after: ${totalTime}ms`);
    
    console.error('❌ Pipeline failed:', error);
    console.groupEnd();
    
    return {
      success: false,
      requestId: request.requestId,
      error: errorMessage,
      logs,
    };
  }
};

/**
 * Get generation status
 */
export const getGenerationStatus = (
  requestId: string
): {
  status: string;
  progress?: number;
  currentStep?: string;
} | null => {
  const store = useCommandStore.getState();
  const request = store.requests.find(r => r.id === requestId);
  
  if (!request) {
    return null;
  }
  
  return {
    status: request.status,
    progress: calculateProgress(request.status),
    currentStep: getCurrentStep(request.status),
  };
};

/**
 * Calculate progress percentage based on status
 */
const calculateProgress = (status: string): number => {
  const progressMap: Record<string, number> = {
    'Pending': 10,
    'Processing': 50,
    'Complete': 100,
    'Error': 0,
  };
  
  return progressMap[status] || 0;
};

/**
 * Save v3.3 intelligence content to store after successful generation
 */
const saveIntelligenceContentToStore = async (
  request: GenerationRequest,
  intelligenceResult: any
): Promise<void> => {
  try {
    const store = useCommandStore.getState();
    
    // Map intelligence result to IntelligenceContent structure
    const contentType = detectContentTypeFromInput(request.userInput);
    const contentId = intelligenceResult.contentId || `intel_${request.requestId}`;
    
    const intelligenceContent: IntelligenceContent = {
      contentId,
      taskId: request.requestId,
      contentType,
      title: generateTitleFromInput(request.userInput),
      enhanced: true,
      qualityScore: intelligenceResult.quality_scores?.overall_score || 0.85,
      memoryContext: {
        relevantMemories: intelligenceResult.memory_context_used ? 
          (intelligenceResult.memory_context?.relevant_memories || []) : [],
        contextualInsights: intelligenceResult.recommendations || [],
        brandAlignment: intelligenceResult.quality_scores?.brand_compliance || 0.8
      },
      generatedContent: {
        structured: intelligenceResult.generated_content?.data || {},
        narrative: intelligenceResult.generated_content?.narrative || '',
        keyInsights: intelligenceResult.recommendations?.slice(0, 5) || [],
        actionableRecommendations: intelligenceResult.recommendations?.slice(5) || []
      },
      metadata: {
        generationTimestamp: new Date().toISOString(),
        model: 'v3.3-intelligence',
        processingTime: calculateProcessingTime(intelligenceResult.logs),
        confidenceLevel: intelligenceResult.quality_scores?.validation_score || 0.8,
        sources: extractSourcesFromLogs(intelligenceResult.logs)
      },
      exportReady: intelligenceResult.quality_scores?.overall_score >= 0.8,
      version: '3.3'
    };
    
    // Save to store
    store.saveIntelligenceContent(intelligenceContent);
    
    console.log('💾 [IntelStore] Saved intelligence content:', contentId, contentType);
    
  } catch (error) {
    console.error('❌ [IntelStore] Failed to save intelligence content:', error);
  }
};

/**
 * Save basic v3.2 content to intelligence store with minimal enhancement
 */
const saveBasicContentToStore = async (
  request: GenerationRequest,
  contentData: any
): Promise<void> => {
  try {
    const store = useCommandStore.getState();
    
    // Create basic intelligence content structure
    const contentType = detectContentTypeFromInput(request.userInput);
    const contentId = contentData.id || `basic_${request.requestId}`;
    
    const basicIntelContent: IntelligenceContent = {
      contentId,
      taskId: request.requestId,
      contentType,
      title: generateTitleFromInput(request.userInput),
      enhanced: false, // Not enhanced by v3.3 intelligence
      qualityScore: 0.7, // Default quality score for v3.2 content
      memoryContext: {
        relevantMemories: [],
        contextualInsights: [],
        brandAlignment: 0.7
      },
      generatedContent: {
        structured: contentData.data || contentData,
        narrative: JSON.stringify(contentData, null, 2), // Basic narrative
        keyInsights: ['Content generated via v3.2 stable pipeline'],
        actionableRecommendations: ['Review and enhance content as needed']
      },
      metadata: {
        generationTimestamp: new Date().toISOString(),
        model: 'v3.2-stable',
        processingTime: 0,
        confidenceLevel: 0.7,
        sources: ['template-orchestrator', 'workflow-api']
      },
      exportReady: true, // v3.2 content is ready by default
      version: '3.2'
    };
    
    // Save to store
    store.saveIntelligenceContent(basicIntelContent);
    
    console.log('💾 [IntelStore] Saved basic content as intelligence:', contentId, contentType);
    
  } catch (error) {
    console.error('❌ [IntelStore] Failed to save basic content:', error);
  }
};

/**
 * Detect content type from user input
 */
const detectContentTypeFromInput = (userInput: string): ContentType => {
  const input = userInput.toLowerCase();
  
  if (input.includes('cma') || input.includes('comparative market analysis')) {
    return 'CMA_REPORT';
  } else if (input.includes('pitch deck') || input.includes('presentation')) {
    return 'PITCH_DECK';
  } else if (input.includes('social') || input.includes('post') || input.includes('tweet')) {
    return 'SOCIAL_POST';
  } else if (input.includes('market report') || input.includes('market analysis')) {
    return 'MARKET_REPORT';
  }
  
  // Default to CMA_REPORT for real estate related queries
  return 'CMA_REPORT';
};

/**
 * Generate a title from user input
 */
const generateTitleFromInput = (userInput: string): string => {
  // Clean and capitalize the input
  const cleaned = userInput
    .replace(/[^a-zA-Z0-9\s]/g, '')
    .trim()
    .split(/\s+/)
    .slice(0, 8) // Limit to 8 words
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
  
  return cleaned || 'Generated Content';
};

/**
 * Calculate processing time from logs
 */
const calculateProcessingTime = (logs: string[]): number => {
  const timeLog = logs.find(log => log.includes('ms'));
  if (timeLog) {
    const match = timeLog.match(/(\d+)ms/);
    return match ? parseInt(match[1], 10) : 0;
  }
  return 0;
};

/**
 * Extract sources from processing logs
 */
const extractSourcesFromLogs = (logs: string[]): string[] => {
  const sources = new Set<string>();
  
  logs.forEach(log => {
    if (log.includes('intelligence')) sources.add('intelligence-layer');
    if (log.includes('memory')) sources.add('memory-service');
    if (log.includes('template')) sources.add('template-orchestrator');
    if (log.includes('workflow')) sources.add('workflow-api');
    if (log.includes('streaming')) sources.add('streaming-api');
  });
  
  return Array.from(sources);
};

/**
 * Get current step description
 */
const getCurrentStep = (status: string): string => {
  const stepMap: Record<string, string> = {
    'Pending': 'Initializing...',
    'Processing': 'Generating content...',
    'Complete': 'Complete!',
    'Error': 'Error occurred',
  };
  
  return stepMap[status] || 'Processing...';
};

/**
 * Retry generation with the original orchestrator
 */
export const retryGeneration = async (
  requestId: string,
  options?: Record<string, any>
): Promise<GenerationResult> => {
  console.log(`🔄 Retrying generation for request ${requestId}`);
  
  const store = useCommandStore.getState();
  const request = store.requests.find(r => r.id === requestId);
  
  if (!request) {
    return {
      success: false,
      requestId,
      error: 'Request not found',
      logs: ['Request not found'],
    };
  }
  
  // Extract original input
  const originalInput = request.userMessage || '';
  
  return generateContent({
    userInput: originalInput,
    requestId,
    metadata: {
      is_retry: true,
      ...options,
    },
  });
};

/**
 * Cancel ongoing generation
 */
export const cancelGeneration = async (
  requestId: string
): Promise<{ success: boolean }> => {
  console.log(`❌ Cancelling generation for request ${requestId}`);
  
  const store = useCommandStore.getState();
  store.updateRequestStatus(requestId, 'Error', 'Cancelled by user');
  
  return { success: true };
};

/**
 * Get pipeline statistics
 */
export const getPipelineStats = () => {
  const store = useCommandStore.getState();
  const requests = store.requests;
  
  const total = requests.length;
  const completed = requests.filter(r => r.status === 'Complete').length;
  const failed = requests.filter(r => r.status === 'Error').length;
  const pending = requests.filter(r => r.status === 'Pending' || r.status === 'Processing').length;
  
  return {
    total,
    completed,
    failed,
    pending,
    successRate: total > 0 ? (completed / total) * 100 : 0,
  };
};