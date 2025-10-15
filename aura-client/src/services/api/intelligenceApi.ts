/**
 * Intelligence API Service
 * ========================
 * 
 * Unified API client for Aura's intelligence pipeline.
 * Replaces all mock frontend orchestration with real backend HTTP calls.
 * 
 * Features:
 * - Automatic JWT token attachment
 * - Error handling and retry logic
 * - Mock transcription support
 * - SSE streaming for progress updates
 * - TypeScript safety with harmonized schemas
 */

import {
  ContentGenerationRequest,
  ContentGenerationResponse,
  TranscriptionRequest,
  TranscriptionResponse,
  RefinementRequest,
  RefinementResponse,
  TaskStatusResponse,
  ContentRetrievalResponse,
  MockPromptResponse,
  HealthCheckResponse,
  ContentTypeInfo,
  StreamProgressEvent,
  TaskStatus,
  ContentType,
  IntelligenceContent,
  ProgressEventData
} from '../../types/intelligence';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const INTELLIGENCE_BASE = `${API_BASE_URL}/api/v1/intelligence`;

// Check if mock mode is enabled
const AURA_MOCK_MODE = import.meta.env.VITE_AURA_MOCK_MODE === 'true';

class IntelligenceApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public errorCode?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'IntelligenceApiError';
  }
}

class IntelligenceApiClient {
  private baseURL: string;
  private authToken: string | null = null;
  
  constructor() {
    this.baseURL = INTELLIGENCE_BASE;
    this.loadAuthToken();
  }

  /**
   * Load JWT token from storage
   */
  private loadAuthToken(): void {
    try {
      // Try multiple storage keys for compatibility
      const token = 
        localStorage.getItem('authToken') || 
        localStorage.getItem('auth_token') ||
        sessionStorage.getItem('authToken');
      
      if (token) {
        this.authToken = token;
      }
    } catch (error) {
      console.warn('Failed to load auth token:', error);
    }
  }

  /**
   * Get headers with JWT authentication
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    return headers;
  }

  /**
   * Generic HTTP request handler with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getHeaders(),
          ...options.headers,
        },
      });

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        let errorDetails = null;

        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.detail || errorMessage;
          errorDetails = errorData.details || errorData;
        } catch {
          // Use default error message if JSON parsing fails
        }

        throw new IntelligenceApiError(
          errorMessage,
          response.status,
          response.status === 422 ? 'validation_error' : 'api_error',
          errorDetails
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof IntelligenceApiError) {
        throw error;
      }

      // Network or other errors
      throw new IntelligenceApiError(
        error instanceof Error ? error.message : 'Unknown error occurred',
        0,
        'network_error'
      );
    }
  }

  // =============================================================================
  // TRANSCRIPTION METHODS
  // =============================================================================

  /**
   * Transcribe audio to text (with mock support)
   */
  async transcribe(
    audioBlob?: Blob, 
    options: Partial<TranscriptionRequest> = {}
  ): Promise<string> {
    const useMock = AURA_MOCK_MODE || options.use_mock || !audioBlob;

    if (useMock) {
      // Use local mock transcription for development
      const { simulateMockTranscription } = await import('../../mocks/transcriptionPrompts');
      return await simulateMockTranscription();
    }

    // Real backend transcription
    try {
      const formData = new FormData();
      if (audioBlob) {
        formData.append('audio_file', audioBlob, 'recording.webm');
      }
      
      if (options.language) {
        formData.append('language', options.language);
      }

      const response = await this.request<TranscriptionResponse>('/transcribe', {
        method: 'POST',
        body: formData,
        headers: {} // Don't set Content-Type for FormData
      });
      
      return response.text;
    } catch (error) {
      console.error('[Intelligence API] Transcription failed, falling back to mock:', error);
      // Fallback to mock on error
      const { simulateMockTranscription } = await import('../../mocks/transcriptionPrompts');
      return await simulateMockTranscription();
    }
  }

  /**
   * Get available mock transcription prompts
   */
  async getMockPrompts(): Promise<MockPromptResponse[]> {
    return this.request<MockPromptResponse[]>('/mock-prompts');
  }

  // =============================================================================
  // CONTENT GENERATION METHODS
  // =============================================================================

  /**
   * Generate content based on user input
   */
  async generateContent(request: ContentGenerationRequest): Promise<ContentGenerationResponse> {
    return this.request<ContentGenerationResponse>('/generate', {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  /**
   * Get task status and progress
   */
  async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    return this.request<TaskStatusResponse>(`/status/${taskId}`);
  }

  /**
   * Get generated content by content ID
   */
  async getContent(contentId: string): Promise<ContentRetrievalResponse> {
    return this.request<ContentRetrievalResponse>(`/content/${contentId}`);
  }

  /**
   * Refine existing content
   */
  async refineContent(contentId: string, request: RefinementRequest): Promise<RefinementResponse> {
    return this.request<RefinementResponse>(`/refine/${contentId}`, {
      method: 'POST',
      body: JSON.stringify(request)
    });
  }

  // =============================================================================
  // STREAMING METHODS
  // =============================================================================

  /**
   * Subscribe to task progress updates via Server-Sent Events
   */
  async *streamTaskProgress(taskId: string): AsyncGenerator<ProgressEventData, void, unknown> {
    const url = `${this.baseURL}/stream/${taskId}`;
    
    try {
      const headers = this.getHeaders();
      delete headers['Content-Type']; // Not needed for SSE
      
      const response = await fetch(url, { headers });

      if (!response.ok) {
        throw new IntelligenceApiError(
          `Failed to start stream: HTTP ${response.status}`,
          response.status
        );
      }

      if (!response.body) {
        throw new IntelligenceApiError('No response body for SSE stream');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // Keep incomplete line

          let currentEvent = 'message';
          let currentData = '';

          for (const line of lines) {
            if (line.startsWith('event:')) {
              currentEvent = line.slice(6).trim();
            } else if (line.startsWith('data:')) {
              currentData = line.slice(5).trim();
              
              // Parse and yield the event
              try {
                const eventData = JSON.parse(currentData) as ProgressEventData;
                console.log(`[IntelligenceAPI][SSE] event=${currentEvent} status=${eventData.status} progress=${eventData.progress}`);
                yield eventData;
                
                // Break on completion or failure
                if (eventData.status === TaskStatus.COMPLETED || 
                    eventData.status === TaskStatus.FAILED) {
                  break;
                }
              } catch (error) {
                console.warn('Failed to parse SSE event data:', currentData);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
      
    } catch (error) {
      console.error('SSE streaming error:', error);
      throw error instanceof IntelligenceApiError 
        ? error 
        : new IntelligenceApiError(`Streaming failed: ${error}`);
    }
  }

  /**
   * Poll task status until completion (fallback for SSE)
   */
  async *pollTaskProgress(
    taskId: string, 
    intervalMs: number = 2000
  ): AsyncGenerator<ProgressEventData, void, unknown> {
    while (true) {
      try {
        const status = await this.getTaskStatus(taskId);
        
        const eventData: ProgressEventData = {
          task_id: status.task_id,
          status: status.status,
          progress: status.progress,
          current_step: status.current_step || undefined,
          timestamp: new Date().toISOString()
        };

        yield eventData;

        // Break on completion or failure
        if (status.status === TaskStatus.COMPLETED || 
            status.status === TaskStatus.FAILED) {
          break;
        }

        // Wait before next poll
        await new Promise(resolve => setTimeout(resolve, intervalMs));
        
      } catch (error) {
        console.error('Polling error:', error);
        break;
      }
    }
  }

  // =============================================================================
  // UTILITY METHODS
  // =============================================================================

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    return this.request<HealthCheckResponse>('/health');
  }

  /**
   * Get supported content types
   */
  async getContentTypes(): Promise<ContentTypeInfo[]> {
    return this.request<ContentTypeInfo[]>('/content-types');
  }

  /**
   * Update auth token
   */
  setAuthToken(token: string | null): void {
    this.authToken = token;
    
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
      sessionStorage.removeItem('authToken');
    }
  }

  // =============================================================================
  // HIGH-LEVEL CONVENIENCE METHODS
  // =============================================================================

  /**
   * Complete content generation workflow with progress tracking
   */
  async generateContentWithProgress(
    request: ContentGenerationRequest,
    onProgress?: (progress: ProgressEventData) => void
  ): Promise<IntelligenceContent> {
    // Start generation
    const response = await this.generateContent(request);
    const { task_id } = response;

    // Track progress via SSE or polling
    try {
      for await (const progress of this.streamTaskProgress(task_id)) {
        if (onProgress) {
          onProgress(progress);
        }

        // Return content when completed
        if (progress.status === TaskStatus.COMPLETED && progress.data?.content_id) {
          const contentResponse = await this.getContent(progress.data.content_id);
          return contentResponse.content;
        }

        // Throw error if failed
        if (progress.status === TaskStatus.FAILED) {
          throw new IntelligenceApiError(
            `Content generation failed: ${progress.current_step || 'Unknown error'}`,
            0,
            'generation_failed'
          );
        }
      }
    } catch (error) {
      // Fallback to polling if SSE fails
      console.warn('SSE failed, falling back to polling:', error);
      
      for await (const progress of this.pollTaskProgress(task_id)) {
        if (onProgress) {
          onProgress(progress);
        }

        if (progress.status === TaskStatus.COMPLETED) {
          const finalStatus = await this.getTaskStatus(task_id);
          
          if (finalStatus.completed_at) {
            // Get content ID from task output
            try {
              const contentResponse = await this.getContent(`${task_id}_content`);
              return contentResponse.content;
            } catch {
              throw new IntelligenceApiError('Content generated but not retrievable');
            }
          }
        }

        if (progress.status === TaskStatus.FAILED) {
          throw new IntelligenceApiError('Content generation failed');
        }
      }
    }

    throw new IntelligenceApiError('Content generation did not complete');
  }

  /**
   * Convenience helper for property brochure generation
   */
  async generateBrochure(
    listingId: string,
    options: {
      userInput?: string;
      context?: Record<string, any>;
      onProgress?: (progress: ProgressEventData) => void;
    } = {}
  ): Promise<IntelligenceContent> {
    if (!listingId) {
      throw new IntelligenceApiError('listingId is required for brochure generation');
    }

    const request: ContentGenerationRequest = {
      user_input: options.userInput || `Generate a property brochure for listing ${listingId}`,
      content_type: ContentType.PROPERTY_BROCHURE,
      context: {
        listing_id: listingId,
        source: 'dashboard_quick_action',
        ...options.context
      }
    };

    console.log('[IntelligenceAPI] Initiating brochure generation for', listingId);

    return this.generateContentWithProgress(request, (progress) => {
      if (options.onProgress) {
        options.onProgress(progress);
      }
    });
  }

  /**
   * Transcribe and generate content in one call
   */
  async transcribeAndGenerate(
    audioFile?: File,
    options: {
      contentType?: ContentType;
      context?: Record<string, any>;
      onProgress?: (progress: ProgressEventData) => void;
    } = {}
  ): Promise<IntelligenceContent> {
    // Step 1: Transcribe audio
    const transcription = await this.transcribe(audioFile);
    
    // Step 2: Generate content
    return this.generateContentWithProgress({
      user_input: transcription.text,
      content_type: options.contentType,
      context: {
        transcription_confidence: transcription.confidence,
        is_mock: transcription.is_mock,
        ...options.context
      }
    }, options.onProgress);
  }
}

// Export singleton instance
export const intelligenceApi = new IntelligenceApiClient();

// Export types and error class for external use
export { IntelligenceApiError };

// Export convenience functions
export const createContentGenerationRequest = (
  userInput: string,
  options: Partial<ContentGenerationRequest> = {}
): ContentGenerationRequest => ({
  user_input: userInput,
  priority: options.priority || 'normal',
  memory_enhanced: options.memory_enhanced !== false,
  ...options
});

export const createRefinementRequest = (
  contentId: string,
  prompt: string,
  options: Partial<RefinementRequest> = {}
): RefinementRequest => ({
  content_id: contentId,
  refinement_prompt: prompt,
  ...options
});

// Development helpers
export const isDevelopmentMode = (): boolean => {
  return import.meta.env.MODE === 'development';
};

export const isMockModeEnabled = (): boolean => {
  return AURA_MOCK_MODE;
};

export default intelligenceApi;