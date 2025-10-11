/**
 * AI Follow-up Agent
 * ===================
 * 
 * Analyzes completed tasks and generates intelligent follow-up suggestions
 * to create contextual task chains and improve user productivity.
 */

// import { detectIntent } from './intentParser'; // TODO: Implement when needed

export interface FollowUpSuggestion {
  message: string;
  intent: string;
  confidence: number;
  parentId: string;
  actionData?: Record<string, any>;
}

/**
 * Generate contextual follow-up suggestions based on completed task
 */
export async function generateFollowUp(previousTask: any): Promise<FollowUpSuggestion | null> {
  try {
    console.log('[FollowUpAgent] Analyzing task:', previousTask.title);

    const { type, metadata, title, id } = previousTask;

    let suggestion = '';
    let intentType = '';
    let actionData: Record<string, any> = {};
    let confidence = 0.85;

    // Contextual analysis based on task type
    switch (type) {
      case 'CMA':
        suggestion = `Would you like me to create a social media post to promote your CMA report for ${metadata?.location || 'this area'}?`;
        intentType = 'SOCIAL_POST';
        actionData = {
          topic: `CMA Report - ${metadata?.location || 'Property Analysis'}`,
          context: `Promote completed CMA analysis for ${metadata?.location}`,
          linkedTo: id
        };
        break;

      case 'MARKET_REPORT':
        suggestion = `Would you like me to generate a detailed CMA based on the market analysis for ${metadata?.location || 'this region'}?`;
        intentType = 'CMA';
        actionData = {
          location: metadata?.location || 'Dubai',
          context: `CMA based on market report insights for ${metadata?.location}`,
          linkedTo: id
        };
        break;

      case 'SOCIAL_POST':
        // Check if it's about a property or general marketing
        if (metadata?.topic?.toLowerCase().includes('cma') || metadata?.topic?.toLowerCase().includes('report')) {
          suggestion = `Would you like me to create a marketing email campaign based on this social media post?`;
          intentType = 'MARKETING_ASSET';
        } else {
          suggestion = `Would you like me to create a market analysis for the area mentioned in this social post?`;
          intentType = 'MARKET_REPORT';
        }
        actionData = {
          originalTopic: metadata?.topic,
          context: 'Follow-up from social media content',
          linkedTo: id
        };
        break;

      case 'GENERIC':
        // Analyze the title to provide contextual suggestions
        if (title.toLowerCase().includes('dubai') || title.toLowerCase().includes('marina') || title.toLowerCase().includes('downtown')) {
          suggestion = `Would you like me to generate a market report for this area?`;
          intentType = 'MARKET_REPORT';
          actionData = {
            location: extractLocationFromTitle(title),
            linkedTo: id
          };
        } else {
          suggestion = `Would you like me to perform a related analysis or create supporting content?`;
          intentType = 'GENERIC';
          confidence = 0.6; // Lower confidence for generic suggestions
        }
        break;

      default:
        console.log('[FollowUpAgent] No specific follow-up logic for task type:', type);
        return null;
    }

    // Additional context-aware enhancements
    if (metadata?.location) {
      actionData.inferredLocation = metadata.location;
    }

    if (metadata?.property_type) {
      actionData.inferredPropertyType = metadata.property_type;
    }

    const followUpSuggestion: FollowUpSuggestion = {
      message: suggestion,
      intent: intentType,
      confidence,
      parentId: id,
      actionData
    };

    console.log('[FollowUpAgent] Generated suggestion:', followUpSuggestion);
    return followUpSuggestion;

  } catch (err) {
    console.error('[FollowUpAgent] Error generating follow-up:', err);
    return null;
  }
}

/**
 * Extract location from task title using simple pattern matching
 */
function extractLocationFromTitle(title: string): string {
  const locationPatterns = [
    /(?:in|for|at)\s+([A-Z][A-Za-z\s]+?)(?:\s+with|$|[,.])/i,
    /(Dubai Marina|Downtown Dubai|Palm Jumeirah|Business Bay|JLT|DIFC)/i,
    /([A-Z][A-Za-z\s]+?)\s+(?:market|area|region|district)/i,
  ];

  for (const pattern of locationPatterns) {
    const match = title.match(pattern);
    if (match && match[1]) {
      return match[1].trim();
    }
  }

  // Default fallback locations
  if (title.toLowerCase().includes('downtown')) return 'Downtown Dubai';
  if (title.toLowerCase().includes('marina')) return 'Dubai Marina';
  if (title.toLowerCase().includes('palm')) return 'Palm Jumeirah';
  if (title.toLowerCase().includes('business bay')) return 'Business Bay';

  return 'Dubai'; // Final fallback
}

/**
 * Generate follow-up command text for orchestration
 */
export function generateFollowUpCommand(suggestion: FollowUpSuggestion): string {
  const { intent, actionData } = suggestion;

  switch (intent) {
    case 'CMA':
      return `Generate a comprehensive CMA for ${actionData?.inferredLocation || actionData?.location || 'Dubai'}`;
      
    case 'MARKET_REPORT':
      return `Create a detailed market analysis report for ${actionData?.inferredLocation || actionData?.location || 'Dubai'}`;
      
    case 'SOCIAL_POST':
      return `Create a social media post about ${actionData?.topic || 'property marketing'}`;
      
    case 'MARKETING_ASSET':
      return `Generate marketing materials based on ${actionData?.originalTopic || 'recent content'}`;
      
    default:
      return `Perform follow-up analysis related to the previous task`;
  }
}

/**
 * Check if a task should trigger follow-up suggestions
 */
export function shouldGenerateFollowUp(task: any): boolean {
  // Only generate follow-ups for completed tasks
  if (task.status !== 'Complete') {
    return false;
  }

  // Skip if task already has follow-ups to avoid infinite loops
  if (task.relatedTasks && task.relatedTasks.length > 0) {
    console.log('[FollowUpAgent] Task already has follow-ups, skipping');
    return false;
  }

  // Skip if task is itself a follow-up (to prevent deep nesting initially)
  if (task.parentId) {
    console.log('[FollowUpAgent] Task is already a follow-up, skipping to prevent deep nesting');
    return false;
  }
  
  // Additional check: Skip if task title contains follow-up keywords
  const followUpKeywords = ['follow-up', 'followup', 'related to', 'based on', 'continue'];
  if (followUpKeywords.some(keyword => task.title?.toLowerCase()?.includes(keyword))) {
    console.log('[FollowUpAgent] Task appears to be a follow-up based on title, skipping');
    return false;
  }

  // Generate follow-ups for main task types
  const supportedTypes = ['CMA', 'MARKET_REPORT', 'SOCIAL_POST', 'GENERIC'];
  return supportedTypes.includes(task.type);
}

/**
 * Get follow-up history for a task chain
 */
export function getTaskChain(taskId: string, allTasks: any[]): any[] {
  const chain: any[] = [];
  
  // Find the root task
  let currentTask = allTasks.find(t => t.id === taskId);
  if (!currentTask) return chain;

  // Build chain from root to leaves
  const visited = new Set<string>();
  const buildChain = (task: any) => {
    if (visited.has(task.id)) return;
    visited.add(task.id);
    
    chain.push(task);
    
    // Add related tasks
    if (task.relatedTasks) {
      task.relatedTasks.forEach((relatedId: string) => {
        const relatedTask = allTasks.find(t => t.id === relatedId);
        if (relatedTask) {
          buildChain(relatedTask);
        }
      });
    }
  };

  buildChain(currentTask);
  return chain;
}

// Export types for use in other modules
