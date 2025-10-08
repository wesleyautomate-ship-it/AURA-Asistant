// Orchestration Layer
// Connects intent detection with appropriate workflow APIs

import { detectIntent, Intent } from './intentParser';
import { createMarketReport, createSocialPost, generateCMAReport, WorkflowResponse } from './workflowApi';

export interface OrchestrationResult {
  intent: Intent;
  workflowResponse?: WorkflowResponse;
  fallbackToStream: boolean;
  error?: string;
}

/**
 * Orchestrate command execution based on detected intent
 * Returns workflow response or indicates fallback to generic AI streaming
 */
export async function orchestrateCommand(prompt: string): Promise<OrchestrationResult> {
  // Detect user intent
  const intent = detectIntent(prompt);
  console.log('[Orchestrator] Intent:', intent);
  
  // If generic or low confidence, fallback to AI streaming
  if (intent.type === 'GENERIC' || intent.confidence < 0.6) {
    console.log('[Orchestrator] Using AI streaming fallback');
    return {
      intent,
      fallbackToStream: true,
    };
  }
  
  // Route to appropriate workflow based on intent type
  try {
    let workflowResponse: WorkflowResponse | undefined;
    
    switch (intent.type) {
      case 'CMA':
        if (intent.location) {
          // Generate CMA report and get download link
          const cmaReport = await generateCMAReport(intent.location);
          console.log('[Orchestrator] CMA report generated:', cmaReport);
          
          // Create workflow response with report URL
          workflowResponse = {
            success: true,
            task_id: `cma_${Date.now()}`,
            message: cmaReport.message,
            data: {
              location: intent.location,
              report_url: cmaReport.report_url,
            },
          };
        }
        break;
      
      case 'MARKET_REPORT':
        if (intent.location) {
          workflowResponse = await createMarketReport(intent.location);
        }
        break;
      
      case 'SOCIAL_POST':
        if (intent.topic) {
          workflowResponse = await createSocialPost(intent.topic);
        }
        break;
      
      default:
        console.log('[Orchestrator] Unknown intent type, falling back to streaming');
        return {
          intent,
          fallbackToStream: true,
        };
    }
    
    if (workflowResponse && workflowResponse.success) {
      console.log('[Orchestrator] Workflow completed successfully');
      return {
        intent,
        workflowResponse,
        fallbackToStream: false,
      };
    }
    
    // If workflow failed, fallback to streaming
    console.log('[Orchestrator] Workflow failed, falling back to streaming');
    return {
      intent,
      fallbackToStream: true,
      error: 'Workflow execution failed',
    };
    
  } catch (error) {
    console.error('[Orchestrator] Workflow error:', error);
    // On error, fallback to AI streaming
    return {
      intent,
      fallbackToStream: true,
      error: error instanceof Error ? error.message : 'Unknown error',
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
