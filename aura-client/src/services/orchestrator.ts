// Orchestration Layer - Enhanced with Context Validation and Self-Healing
// Connects intent detection with appropriate workflow APIs
// Ensures users never see 422 errors through intelligent fallback strategies

import { detectIntent, Intent } from './intentParser';
import { 
  createMarketReport, 
  createSocialPost, 
  createCMA,
  WorkflowResponse
} from './workflowApi';
import { validateWorkflowPayload, enrichWorkflowPayload } from './contextEnrichment';
import templateOrchestrator, { TemplateOrchestrationResult } from './templateOrchestrator';

export interface OrchestrationResult {
  intent: Intent;
  workflowResponse?: WorkflowResponse;
  contentGeneration?: TemplateOrchestrationResult; // For AI content generation
  fallbackToStream: boolean;
  error?: string;
  parentId?: string;
  validationStatus?: 'valid' | 'enriched' | 'fallback' | 'stream';
  enrichmentLog?: string[];
  userMessage?: string; // Friendly message for UI display
}

/**
 * Enhanced orchestrate command with self-healing context validation
 * Ensures users never see 422 errors through intelligent fallback strategies
 */
export async function orchestrateCommand(
  prompt: string, 
  parentId?: string,
  recentTasks: any[] = [],
  contextHistory: string[] = []
): Promise<OrchestrationResult> {
  // Step 1: Detect user intent
  const intent = detectIntent(prompt);
  console.log('[Orchestrator] Intent detected:', intent);
  
  // Step 2: Early fallback for generic or low-confidence intents
  if (intent.type === 'GENERIC' || intent.confidence < 0.6) {
    console.log('[Orchestrator] Low confidence or generic intent - streaming fallback');
    return {
      intent,
      fallbackToStream: true,
      parentId,
      validationStatus: 'stream',
      userMessage: "I'll help you with that using my general knowledge."
    };
  }
  
  // Step 3: Check if this is a content generation request
  const isContentGeneration = intent.topic && (
    intent.topic.toLowerCase().includes('generate') ||
    intent.topic.toLowerCase().includes('create') ||
    intent.topic.toLowerCase().includes('build') ||
    intent.topic.toLowerCase().includes('pitch') ||
    intent.topic.toLowerCase().includes('deck') ||
    intent.topic.toLowerCase().includes('report')
  );
  
  // Step 4: Route to Template Orchestrator if content generation intent
  if (isContentGeneration || intent.type === 'PITCH_DECK') {
    console.log('[Orchestrator] 🎨 Routing to Template Orchestrator for content generation');
    
    try {
      const contentResult = await templateOrchestrator.orchestrateContentGeneration(
        intent,
        recentTasks,
        contextHistory,
        prompt
      );
      
      if (contentResult.success && contentResult.content) {
        console.log('[Orchestrator] ✅ Content generation completed successfully');
        return {
          intent,
          contentGeneration: contentResult,
          fallbackToStream: false,
          parentId,
          validationStatus: 'valid',
          userMessage: `I've generated your ${contentResult.content.type.toLowerCase().replace('_', ' ')} successfully! You can view and export it now.`
        };
      } else {
        console.log('[Orchestrator] Content generation failed, falling back to streaming');
        return {
          intent,
          contentGeneration: contentResult,
          fallbackToStream: true,
          parentId,
          validationStatus: 'fallback',
          userMessage: contentResult.userMessage || "I'll help you create that content through our conversation instead."
        };
      }
    } catch (error) {
      console.error('[Orchestrator] Template orchestration error:', error);
      return {
        intent,
        fallbackToStream: true,
        parentId,
        validationStatus: 'fallback',
        userMessage: "I encountered an issue generating your content. Let me help you through a conversation instead.",
        error: error instanceof Error ? error.message : 'Content generation failed'
      };
    }
  }

  // Step 4.1: Dedicated brochure workflow (prioritized before generic validation)
  if (intent.type === 'BROCHURE') {
    if (!shouldUseWorkflowAPIs()) {
      return {
        intent,
        fallbackToStream: true,
        parentId,
        validationStatus: 'fallback',
        userMessage: generateWorkflowFailureMessage(intent),
        error: 'Workflow execution disabled',
      };
    }

    const workflowResponse = await executeBrochureWorkflow(prompt, intent);
    if (workflowResponse.success) {
      return {
        intent,
        workflowResponse,
        fallbackToStream: false,
        parentId,
        validationStatus: 'valid',
        userMessage: workflowResponse.message,
      };
    }

    return {
      intent,
      workflowResponse,
      fallbackToStream: true,
      parentId,
      validationStatus: 'fallback',
      userMessage: generateWorkflowFailureMessage(intent),
      error: workflowResponse.error || 'Brochure workflow failed',
    };
  }

  // Step 5: Pre-validate payload before attempting workflow
  const validation = validateWorkflowPayload(intent);
  console.log(`[Orchestrator] Payload validation: ${validation.isValid ? '✅ Valid' : '❌ Invalid'} - Missing: ${validation.missingFields.join(', ')}`);
  
  // Step 6: If validation fails, attempt context enrichment
  if (!validation.isValid) {
    console.log('[Orchestrator] Attempting context enrichment for missing fields');
    
    try {
      const enrichment = await enrichWorkflowPayload(intent, recentTasks, contextHistory, prompt);
      
      // If enrichment fails, provide graceful fallback
      if (!enrichment.canProceed) {
        console.log(`[Orchestrator] Enrichment failed: ${enrichment.fallbackReason}`);
        return {
          intent,
          fallbackToStream: true,
          parentId,
          validationStatus: 'fallback',
          enrichmentLog: enrichment.debugLog,
          userMessage: generateContextualFallbackMessage(intent, enrichment.missingFields),
          error: enrichment.fallbackReason
        };
      }
      
      console.log(`[Orchestrator] Context enrichment successful: ${enrichment.validationStatus}`);
    } catch (enrichError) {
      console.error('[Orchestrator] Context enrichment error:', enrichError);
      return {
        intent,
        fallbackToStream: true,
        parentId,
        validationStatus: 'fallback',
        userMessage: generateContextualFallbackMessage(intent, validation.missingFields),
        error: 'Context enrichment failed'
      };
    }
  }
  
  // Step 7: Execute validated workflow with comprehensive error handling
  try {
    let workflowResponse: WorkflowResponse | undefined;
    
    switch (intent.type) {
      case 'CMA':
        console.log('[Orchestrator] Executing CMA workflow');
        workflowResponse = await executeCMAWorkflow(intent, recentTasks, contextHistory, prompt);
        break;
      
      case 'MARKET_REPORT':
        console.log('[Orchestrator] Executing Market Report workflow');
        workflowResponse = await createMarketReport(intent, recentTasks, contextHistory, prompt);
        break;
      
      case 'SOCIAL_POST':
        console.log('[Orchestrator] Executing Social Post workflow');
        workflowResponse = await createSocialPost(intent, recentTasks, contextHistory, prompt);
        break;
      
      case 'BROCHURE':
        console.log('[Orchestrator] Executing Brochure workflow');
        workflowResponse = await executeBrochureWorkflow(prompt, intent);
        break;
      
      default:
        console.log('[Orchestrator] Unknown intent type, falling back to streaming');
        return {
          intent,
          fallbackToStream: true,
          validationStatus: 'stream',
          userMessage: "I'll help you with that using my general knowledge."
        };
    }
    
    // Step 8: Handle successful workflow response
    if (workflowResponse?.success) {
      console.log('[Orchestrator] ✅ Workflow completed successfully');
      return {
        intent,
        workflowResponse,
        fallbackToStream: false,
        parentId,
        validationStatus: workflowResponse.enrichment?.status || 'valid',
        enrichmentLog: workflowResponse.enrichment?.debugLog
      };
    }
    
    // Step 9: Handle failed workflow response
    console.log('[Orchestrator] Workflow returned failure, falling back to streaming');
    return {
      intent,
      fallbackToStream: true,
      parentId,
      validationStatus: 'fallback',
      userMessage: generateWorkflowFailureMessage(intent),
      error: 'Workflow execution returned failure'
    };
    
  } catch (error) {
    console.error('[Orchestrator] 💥 Workflow execution error:', error);
    
    // Step 10: Intelligent error categorization and fallback
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    const is422Error = errorMessage.includes('422') || errorMessage.includes('Unprocessable');
    
    if (is422Error) {
      console.warn('[Orchestrator] 🛡️ Caught 422 error - user will not see this!');
      return {
        intent,
        fallbackToStream: true,
        parentId,
        validationStatus: 'fallback',
        userMessage: generate422FallbackMessage(intent),
        error: 'Payload validation failed at API level'
      };
    }
    
    // Default error fallback
    return {
      intent,
      fallbackToStream: true,
      parentId,
      validationStatus: 'fallback',
      userMessage: generateGenericFallbackMessage(intent),
      error: errorMessage
    };
  }
}

/**
 * Generate mock workflow response for development/testing
 */
export function generateMockWorkflowResponse(intent: Intent): WorkflowResponse {
  const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  switch (intent.type) {
    case 'CMA':
      return {
        success: true,
        task_id: taskId,
        message: `CMA report for ${intent.location} is being generated. You'll be notified when it's ready.`,
        data: {
          location: intent.location,
          estimated_completion: '5-10 minutes',
        },
      };
    
    case 'MARKET_REPORT':
      return {
        success: true,
        task_id: taskId,
        message: `Market analysis report for ${intent.location} is being generated.`,
        data: {
          location: intent.location,
          estimated_completion: '3-5 minutes',
        },
      };
    
    case 'SOCIAL_POST':
      return {
        success: true,
        task_id: taskId,
        message: `Social media content about "${intent.topic}" is being created.`,
        data: {
          topic: intent.topic,
          estimated_completion: '1-2 minutes',
        },
      };
    
    case 'BROCHURE':
      const building = intent.building || 'Unknown Building';
      const beds = intent.beds ? `${intent.beds}BR ` : '';
      return {
        success: true,
        task_id: taskId,
        message: `Property brochure for ${beds}${building} is being generated.`,
        data: {
          building: intent.building,
          beds: intent.beds,
          unit: intent.unit,
          estimated_completion: '2-3 minutes',
        },
      };
    
    default:
      return {
        success: false,
        task_id: '',
        message: 'Unknown task type',
      };
  }
}

/**
 * Check if workflow APIs should be used (can toggle for development)
 */
export function shouldUseWorkflowAPIs(): boolean {
  // Check environment variable (future enhancement)
  const useWorkflows = import.meta.env.VITE_USE_WORKFLOW_APIS;
  
  // For now, always attempt workflows and fallback on error
  return useWorkflows !== 'false';
}

// Helper functions for message generation
function generateContextualFallbackMessage(intent: any, missingFields: string[]): string {
  const intentType = intent.category || 'task';
  const fieldsText = missingFields.length > 0 ? ` (missing: ${missingFields.join(', ')})` : '';
  
  return `I need more information to complete your ${intentType} request${fieldsText}. Let me help you with this in a conversation instead.`;
}

function generateWorkflowFailureMessage(intent: any): string {
  const intentType = intent.category || 'task';
  return `I encountered an issue executing the ${intentType} workflow. Let me assist you through a conversation instead.`;
}

function generate422FallbackMessage(intent: any): string {
  const intentType = intent.category || 'task';
  return `The ${intentType} request couldn't be processed as submitted. Let me help you refine this through our conversation.`;
}

function generateGenericFallbackMessage(intent: any): string {
  const intentType = intent.category || 'task';
  return `There was an issue processing your ${intentType} request. Let me assist you through a conversation instead.`;
}

// Helper function for CMA workflow execution
async function executeCMAWorkflow(intent: any, recentTasks: any[], contextHistory: any[], _prompt: string): Promise<any> {
  console.group('[Orchestrator] CMA Workflow Execution');
  console.log('Intent:', intent);
  console.log('Recent tasks count:', recentTasks.length);
  console.log('Context history count:', contextHistory.length);
  
  try {
    const result = await createCMA(intent, recentTasks, contextHistory);
    console.log('CMA workflow completed successfully');
    console.groupEnd();
    return result;
  } catch (error) {
    console.error('CMA workflow execution failed:', error);
    console.groupEnd();
    throw error;
  }
}

// Helper function for Brochure workflow execution
async function executeBrochureWorkflow(prompt: string, intent: Intent): Promise<WorkflowResponse> {
  console.group('[Orchestrator] 📋 Brochure Workflow Execution');
  console.log('Intent:', intent);
  console.log('Original prompt:', prompt);
  
  try {
    // Import API clients dynamically to avoid circular dependencies
    const { search: searchProperties, create: createProperty, buildMinimalProperty } = await import('../features/properties/api/properties');
    const { createDraft, renderDraft } = await import('../features/brochure/api/brochure');
    
    console.log('📍 [Brochure] Step 1: Try to resolve existing property');
    
    let property = null;
    
    // Try to find existing property if we have building info
    if (intent.building) {
      const searchResults = await searchProperties({
        q: prompt,
        building: intent.building,
        unit: intent.unit,
        limit: 1
      });
      
      if (searchResults.length > 0) {
        property = searchResults[0];
        console.log(`✅ [Brochure] Found existing property: ${property.title}`);
      }
    }
    
    // If no property found, create minimal property (idempotent)
    if (!property) {
      console.log('🏠 [Brochure] Step 2: Creating minimal property');
      const propertyPayload = buildMinimalProperty(prompt, intent);
      
      try {
        property = await createProperty(propertyPayload);
        console.log(`✅ [Brochure] Created property: ${property.title}`);
      } catch (error: any) {
        console.error('❌ [Brochure] Property creation failed:', error);
        // Continue without property_id - brochure can still be created
      }
    }
    
    console.log('📋 [Brochure] Step 3: Creating brochure draft');
    
    // Create brochure draft (with property enrichment if available)
    const draftPayload = {
      templateKey: 'clean-minimal',
      property_id: property?.id,
    };
    
    const draft = await createDraft(draftPayload);
    console.log(`✅ [Brochure] Created draft: ${draft.id}`);
    
    console.log('🎨 [Brochure] Step 4: Rendering PDF');
    
    // Render the brochure to PDF
    const renderResult = await renderDraft(draft.id);
    console.log(`✅ [Brochure] PDF rendered: ${renderResult.download_url}`);
    
    console.groupEnd();
    
    // Return successful workflow response
    return {
      success: true,
      task_id: `brochure_${draft.id}`,
      message: `Brochure created successfully! ${property ? `Property: ${property.title}` : 'Ready for download.'}`,
      data: {
        brochureId: draft.id,
        propertyId: property?.id,
        propertyTitle: property?.title,
        downloadUrl: renderResult.download_url,
        building: intent.building,
        beds: intent.beds,
        unit: intent.unit,
      },
    };
    
  } catch (error: any) {
    console.error('❌ [Brochure] Workflow execution failed:', error);
    console.groupEnd();
    
    // Return graceful failure (orchestrator will handle fallback)
    return {
      success: false,
      task_id: '',
      message: 'Brochure creation failed',
      error: error.message || 'Unknown error',
    };
  }
}

/**
 * Command Orchestrator Class
 * Provides a singleton interface for command orchestration
 */
class CommandOrchestrator {
  /**
   * Main orchestration method
   */
  async orchestrate(
    prompt: string, 
    parentId?: string,
    recentTasks: any[] = [],
    contextHistory: string[] = []
  ): Promise<OrchestrationResult> {
    return orchestrateCommand(prompt, parentId, recentTasks, contextHistory);
  }
  
  /**
   * Generate mock workflow response for development/testing
   */
  generateMockResponse(intent: Intent): WorkflowResponse {
    return generateMockWorkflowResponse(intent);
  }
  
  /**
   * Check if workflow APIs should be used (can toggle for development)
   */
  shouldUseWorkflowAPIs(): boolean {
    return shouldUseWorkflowAPIs();
  }
  
  /**
   * Get generated content by ID from template orchestrator
   */
  getGeneratedContent(contentId: string) {
    return templateOrchestrator.getGeneratedContent(contentId);
  }
  
  /**
   * List all generated content from template orchestrator
   */
  listGeneratedContent() {
    return templateOrchestrator.listGeneratedContent();
  }
  
  /**
   * Get template configuration for content type
   */
  getTemplateConfig(contentType: 'CMA' | 'PITCH_DECK' | 'SOCIAL_POST' | 'MARKET_REPORT') {
    return templateOrchestrator.getTemplateConfig(contentType);
  }
}

export default new CommandOrchestrator();
