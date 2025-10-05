import { apiGet, apiPost } from './api';
import { CONFIG } from './config';
import { useUserStore } from '@propertypro/store';

// Backend API types based on ai_request_router.py
export interface AIRequestResponse {
  id: string;
  team: string;
  title: string;
  description: string;
  status: string;
  eta: string | null;
  priority: number;
  created_at: string;
  updated_at: string;
  steps: Array<{
    step: string;
    status: string;
    progress: number;
    started_at?: string;
    finished_at?: string;
  }>;
  deliverables: Array<{
    id: string;
    type: string;
    name: string;
    url: string;
    preview_url?: string;
    status: string;
  }>;
}

export interface AIRequestCreatePayload {
  team: string;
  content: string;
  template_id?: string;
  brand_context?: Record<string, any>;
  priority?: number;
}

// Frontend types from features package
export interface Request {
  id: number;
  category: 'Marketing' | 'Sync' | 'Campaign' | 'Data Analysis';
  title: string;
  description: string;
  eta: string;
  status: 'Queued' | 'Processing' | 'Ready for Review';
  progress: number;
  assignees: { id: string; avatarUrl?: string }[];
  image?: string;
  tags?: { text: string; color: string }[];
}

// Status mapping from backend to frontend
const STATUS_MAPPING: Record<string, Request['status']> = {
  'queued': 'Queued',
  'planning': 'Processing',
  'generating': 'Processing',
  'validating': 'Processing',
  'draft_ready': 'Ready for Review',
  'approved': 'Ready for Review',
  'failed': 'Processing', // We'll handle failed state with error indicators
};

// Progress mapping based on status
const PROGRESS_MAPPING: Record<string, number> = {
  'queued': 0,
  'planning': 20,
  'generating': 60,
  'validating': 85,
  'draft_ready': 95,
  'approved': 100,
  'failed': 100,
};

// Team to category mapping
const TEAM_CATEGORY_MAPPING: Record<string, Request['category']> = {
  'marketing': 'Marketing',
  'analytics': 'Data Analysis',
  'social': 'Campaign',
  'strategy': 'Data Analysis',
  'packages': 'Campaign',
  'transactions': 'Sync',
};

/**
 * Maps backend AIRequestResponse to frontend Request interface
 */
export function mapAIResponseToRequest(apiResponse: AIRequestResponse): Request {
  // Calculate overall progress from steps
  let calculatedProgress = PROGRESS_MAPPING[apiResponse.status] || 0;
  
  // If we have steps, calculate progress based on completed steps
  if (apiResponse.steps && apiResponse.steps.length > 0) {
    const completedSteps = apiResponse.steps.filter(step => step.status === 'completed');
    const totalSteps = apiResponse.steps.length;
    calculatedProgress = Math.round((completedSteps.length / totalSteps) * 100);
  }

  // Format ETA
  let formattedEta = '~5 min'; // default
  if (apiResponse.eta) {
    const etaDate = new Date(apiResponse.eta);
    const now = new Date();
    const diffMinutes = Math.max(1, Math.round((etaDate.getTime() - now.getTime()) / (1000 * 60)));
    formattedEta = `~${diffMinutes} min`;
  }

  return {
    id: parseInt(apiResponse.id, 10) || Date.now(), // Convert UUID to number for compatibility
    category: TEAM_CATEGORY_MAPPING[apiResponse.team] || 'Data Analysis',
    title: apiResponse.title,
    description: apiResponse.description,
    eta: formattedEta,
    status: STATUS_MAPPING[apiResponse.status] || 'Queued',
    progress: calculatedProgress,
    assignees: [{ id: 'ai' }], // Always assigned to AI
    // Add tags based on priority and status
    tags: [
      ...(apiResponse.priority > 7 ? [{ text: 'High Priority', color: 'bg-red-100 text-red-800' }] : []),
      ...(apiResponse.status === 'failed' ? [{ text: 'Failed', color: 'bg-red-100 text-red-800' }] : []),
      ...(apiResponse.deliverables.length > 0 ? [{ text: 'Has Deliverables', color: 'bg-green-100 text-green-800' }] : []),
    ],
  };
}

/**
 * Check if a request is currently processing
 */
export function isRequestProcessing(status: string): boolean {
  return ['planning', 'generating', 'validating'].includes(status);
}

// SSE Client for real-time updates
export interface SSEOptions {
  maxRetries?: number;
  initialRetryDelay?: number;
  maxRetryDelay?: number;
  heartbeatTimeout?: number;
}

export interface SSEHandlers {
  onUpdate: (request: Request) => void;
  onError: (error: Error) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

class SSEClient {
  private abortController: AbortController | null = null;
  private retryCount = 0;
  private retryTimeout: NodeJS.Timeout | null = null;
  private heartbeatTimeout: NodeJS.Timeout | null = null;
  private isTerminated = false;

  constructor(
    private requestId: string,
    private handlers: SSEHandlers,
    private options: SSEOptions = {}
  ) {
    this.options = {
      maxRetries: 5,
      initialRetryDelay: 1000,
      maxRetryDelay: 30000,
      heartbeatTimeout: 45000,
      ...options,
    };
  }

  async connect() {
    if (this.isTerminated) return;

    this.abortController = new AbortController();
    const { token } = useUserStore.getState();

    try {
      const response = await fetch(
        `${CONFIG.apiBaseUrl}/api/requests/${this.requestId}/stream`,
        {
          method: 'GET',
          headers: {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
            ...(token && { 'Authorization': `Bearer ${token}` }),
          },
          signal: this.abortController.signal,
        }
      );

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          throw new Error('Authentication failed');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('No response body available for streaming');
      }

      this.handlers.onOpen?.();
      this.retryCount = 0; // Reset on successful connection
      this.resetHeartbeat();

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (!this.isTerminated) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (this.isTerminated) break;
          
          this.resetHeartbeat();
          await this.processSSELine(line);
        }
      }

    } catch (error) {
      if (this.isTerminated) return;

      console.debug('[SSE] Connection error:', error);
      
      // Don't retry on auth errors
      if (error instanceof Error && error.message.includes('Authentication failed')) {
        this.handlers.onError(error);
        return;
      }

      // Retry with exponential backoff
      if (this.retryCount < (this.options.maxRetries || 5)) {
        const delay = Math.min(
          (this.options.initialRetryDelay || 1000) * Math.pow(2, this.retryCount),
          this.options.maxRetryDelay || 30000
        );
        
        // Add jitter to avoid thundering herd
        const jitter = Math.random() * 1000;
        
        console.debug(`[SSE] Retrying in ${delay + jitter}ms (attempt ${this.retryCount + 1})`);
        
        this.retryTimeout = setTimeout(() => {
          this.retryCount++;
          this.connect();
        }, delay + jitter);
      } else {
        this.handlers.onError(error as Error);
      }
    }
  }

  private async processSSELine(line: string) {
    if (!line.trim()) return;

    if (line.startsWith('data: ')) {
      const data = line.slice(6);
      
      if (data === '[DONE]') {
        this.terminate();
        return;
      }

      try {
        const parsed = JSON.parse(data);
        
        if (parsed.type === 'update' && parsed.data) {
          // Assume the backend sends the full AIRequestResponse
          const request = mapAIResponseToRequest(parsed.data);
          this.handlers.onUpdate(request);
          
          // Stop streaming if request reached terminal state
          if (['approved', 'failed'].includes(parsed.data.status)) {
            this.terminate();
          }
        }
      } catch (error) {
        console.debug('[SSE] Failed to parse data:', data, error);
      }
    }
  }

  private resetHeartbeat() {
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
    }

    this.heartbeatTimeout = setTimeout(() => {
      if (!this.isTerminated) {
        console.debug('[SSE] Heartbeat timeout, reconnecting...');
        this.disconnect();
        this.connect();
      }
    }, this.options.heartbeatTimeout || 45000);
  }

  private disconnect() {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }

    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
      this.retryTimeout = null;
    }

    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout);
      this.heartbeatTimeout = null;
    }
  }

  terminate() {
    if (this.isTerminated) return;
    
    this.isTerminated = true;
    this.disconnect();
    this.handlers.onClose?.();
  }
}

// Main service class
export class AIRequestService {
  /**
   * Create a new AI request
   */
  static async createRequest(payload: AIRequestCreatePayload): Promise<Request> {
    const response = await apiPost<AIRequestResponse>('/api/requests/', payload);
    return mapAIResponseToRequest(response);
  }

  /**
   * List AI requests with optional filters
   */
  static async listRequests(params?: {
    status?: string;
    team?: string;
    limit?: number;
    offset?: number;
  }): Promise<Request[]> {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.team) queryParams.append('team', params.team);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());

    const url = '/api/requests/' + (queryParams.toString() ? `?${queryParams.toString()}` : '');
    const responses = await apiGet<AIRequestResponse[]>(url);
    
    return responses.map(mapAIResponseToRequest);
  }

  /**
   * Get a specific AI request
   */
  static async getRequest(id: string): Promise<Request> {
    const response = await apiGet<AIRequestResponse>(`/api/requests/${id}`);
    return mapAIResponseToRequest(response);
  }

  /**
   * Approve a request
   */
  static async approveRequest(id: string): Promise<{ status: string; completed_at: string }> {
    return await apiPost(`/api/requests/${id}/approve`);
  }

  /**
   * Request a revision
   */
  static async reviseRequest(id: string, instructions: string): Promise<{ status: string }> {
    return await apiPost(`/api/requests/${id}/revise`, { instructions });
  }

  /**
   * Subscribe to real-time updates for a request
   * Returns an unsubscribe function
   */
  static subscribeToRequestStream(
    id: string,
    handlers: SSEHandlers,
    options?: SSEOptions
  ): () => void {
    const client = new SSEClient(id, handlers, options);
    client.connect();

    return () => {
      client.terminate();
    };
  }

  /**
   * Get available templates for a team
   */
  static async getTemplates(team?: string): Promise<any[]> {
    const url = '/api/requests/templates' + (team ? `?team=${team}` : '');
    return await apiGet(url);
  }

  /**
   * Get brand assets for the user's brokerage
   */
  static async getBrandAssets(): Promise<any[]> {
    return await apiGet('/api/requests/brand-kit');
  }
}

// Convenience function for command center integration
export async function createRequestFromCommand(
  content: string,
  team: string = 'marketing',
  priority: number = 5
): Promise<Request> {
  return AIRequestService.createRequest({
    team,
    content,
    priority,
  });
}

export default AIRequestService;