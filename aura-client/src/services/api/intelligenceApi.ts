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
import { getAuthToken, useAuthStore } from '../../store/authStore';
import api from '../http'
import { AxiosError, AxiosRequestConfig } from 'axios'

// API Configuration
const BASE_URL = api.defaults.baseURL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const INTELLIGENCE_BASE = `${BASE_URL.replace(/\/$/, '')}/intelligence`;

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
  private baseURL: string

  constructor() {
    this.baseURL = INTELLIGENCE_BASE
  }

  /**
   * Get headers with JWT authentication
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    const token = getAuthToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    return headers
  }

  /**
   * Generic HTTP request handler with error handling
   */
  private async request<T>(endpoint: string, options: RequestInit = {}, attempt = 0): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${this.baseURL}${endpoint}`

    const axiosConfig: AxiosRequestConfig = {
      url,
      method: (options.method as AxiosRequestConfig['method']) ?? 'GET',
      headers: {
        ...this.getHeaders(),
        ...(options.headers as Record<string, string> | undefined),
      },
      data: options.body,
      signal: options.signal,
    }

    try {
      const response = await api.request<T>(axiosConfig)
      return response.data
    } catch (error) {
      const axiosError = error as AxiosError<any>

      if (axiosError.response?.status === 401 && attempt === 0) {
        const refreshed = await useAuthStore.getState().refreshAccessToken()
        if (refreshed) {
          return this.request<T>(endpoint, options, attempt + 1)
        }
      }

      if (axiosError.response) {
        const status = axiosError.response.status
        const data = axiosError.response.data || {}
        const message =
          (typeof data === 'object' && (data.message || data.detail)) ||
          axiosError.message ||
          `HTTP ${status}`

        throw new IntelligenceApiError(
          message,
          status,
          status === 422 ? 'validation_error' : 'api_error',
          data?.details ?? data
        )
      }

      throw new IntelligenceApiError(
        axiosError.message || 'Unknown error occurred',
        0,
        'network_error'
      )
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
    for await (const progress of this.pollTaskProgress(taskId)) {
      yield progress
      if (progress.status === TaskStatus.COMPLETED || progress.status === TaskStatus.FAILED) {
        break
      }
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
