// Workflow API Service
// Handles backend API calls for specific task types (CMA, Market Reports, Social Posts)

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface WorkflowResponse {
  success: boolean;
  task_id: string;
  message: string;
  data?: any;
}

/**
 * Create a CMA (Comparative Market Analysis) report
 */
export async function createCMA(location: string): Promise<WorkflowResponse> {
  console.log(`[Workflow] Creating CMA for ${location}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/cma/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ location }),
    });

    if (!response.ok) {
      throw new Error(`CMA API failed: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('[Workflow] CMA created successfully:', data.task_id);
    return data;
  } catch (error) {
    console.error('[Workflow] CMA creation error:', error);
    throw error;
  }
}

/**
 * Create a market analysis report
 */
export async function createMarketReport(location: string): Promise<WorkflowResponse> {
  console.log(`[Workflow] Creating market report for ${location}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ location }),
    });

    if (!response.ok) {
      throw new Error(`Market Report API failed: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('[Workflow] Market report created successfully:', data.task_id);
    return data;
  } catch (error) {
    console.error('[Workflow] Market report creation error:', error);
    throw error;
  }
}

/**
 * Generate social media content
 */
export async function createSocialPost(topic: string): Promise<WorkflowResponse> {
  console.log(`[Workflow] Generating social post: ${topic}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/social/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ topic }),
    });

    if (!response.ok) {
      throw new Error(`Social Post API failed: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('[Workflow] Social post created successfully:', data.task_id);
    return data;
  } catch (error) {
    console.error('[Workflow] Social post creation error:', error);
    throw error;
  }
}

/**
 * Check workflow task status
 */
export async function checkTaskStatus(taskId: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/tasks/${taskId}/status`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Task status check failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('[Workflow] Task status check error:', error);
    throw error;
  }
}

/**
 * Generate mock CMA report for development/testing
 */
export async function mockCMAReport(location: string): Promise<{ report_url: string; message: string }> {
  console.log(`[Workflow] Generating mock CMA report for ${location}`);
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1200));
  
  const sanitizedLocation = location.replace(/\s+/g, '_');
  return {
    report_url: `/mock-reports/CMA_${sanitizedLocation}_${Date.now()}.pdf`,
    message: `Mock CMA report generated for ${location}`,
  };
}

/**
 * Generate CMA report (real or mock based on environment)
 */
export async function generateCMAReport(location: string): Promise<{ report_url: string | null; message: string }> {
  const useRealAPI = import.meta.env.VITE_USE_REAL_API === 'true';
  
  // Mock mode (default for development)
  if (!useRealAPI) {
    console.log('[Workflow] Using mock CMA generation');
    return await mockCMAReport(location);
  }
  
  // Real API mode
  console.log(`[Workflow] Generating real CMA report for ${location}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/cma/report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ location }),
    });

    if (!response.ok) {
      throw new Error(`CMA Report API failed: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('[Workflow] CMA report generated successfully:', data.report_url);
    return {
      report_url: data.report_url || null,
      message: data.message || `CMA report generated for ${location}`,
    };
  } catch (error) {
    console.error('[Workflow] CMA report generation error:', error);
    // Fallback to mock on error
    console.log('[Workflow] Falling back to mock CMA generation');
    return await mockCMAReport(location);
  }
}
