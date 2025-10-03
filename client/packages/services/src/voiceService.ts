/**
 * Voice Service for PropertyPro AI Real Estate Assistant
 * 
 * This service handles voice processing, content generation, and integration
 * with the backend voice processing endpoints.
 */

export interface VoiceProcessingRequest {
  user_id: string;
  session_id?: string;
  transcript?: string;
}

export interface VoiceProcessingResponse {
  request_id: string;
  transcript: string;
  intent: string;
  entities: Record<string, any>;
  processing_type: string;
  status: string;
  response?: Record<string, any>;
  eta?: string;
}

export interface ContentGenerationRequest {
  template_type: string;
  property_data: Record<string, any>;
  user_preferences: Record<string, any>;
}

export interface ContentGenerationResponse {
  content_id: string;
  template_type: string;
  status: string;
  approval_status: string;
  created_at: string;
}

export interface VoiceRequestStatus {
  request_id: string;
  status: string;
  transcript: string;
  intent: string;
  processing_type: string;
  ai_status?: string;
  result_data?: Record<string, any>;
  created_at: string;
  completed_at?: string;
}

export interface PendingApproval {
  content_id: string;
  template_type: string;
  template_name: string;
  content_data: Record<string, any>;
  property_data: Record<string, any>;
  created_at: string;
}

class VoiceService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = 'http://localhost:8001/voice';
  }

  /**
   * Process voice request from audio file
   */
  async processVoiceRequest(
    audioFile: File,
    userId: string,
    sessionId?: string
  ): Promise<VoiceProcessingResponse> {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      formData.append('user_id', userId);
      if (sessionId) {
        formData.append('session_id', sessionId);
      }

      const response = await fetch(`${this.baseUrl}/process`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Voice processing failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error processing voice request:', error);
      throw error;
    }
  }

  /**
   * Process voice request from text transcript (for testing)
   */
  async processVoiceText(
    request: VoiceProcessingRequest
  ): Promise<VoiceProcessingResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/process-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Voice text processing failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error processing voice text:', error);
      throw error;
    }
  }

  /**
   * Get status of voice request
   */
  async getVoiceRequestStatus(requestId: string): Promise<VoiceRequestStatus> {
    try {
      const response = await fetch(`${this.baseUrl}/status/${requestId}`);

      if (!response.ok) {
        throw new Error(`Failed to get voice request status: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting voice request status:', error);
      throw error;
    }
  }

  /**
   * Generate content using specified template
   */
  async generateContent(
    request: ContentGenerationRequest,
    userId: string
  ): Promise<ContentGenerationResponse> {
    try {
      const formData = new FormData();
      formData.append('template_type', request.template_type);
      formData.append('property_data', JSON.stringify(request.property_data));
      formData.append('user_preferences', JSON.stringify(request.user_preferences));
      formData.append('user_id', userId);

      const response = await fetch(`${this.baseUrl}/content/generate`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Content generation failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error generating content:', error);
      throw error;
    }
  }

  /**
   * Approve generated content
   */
  async approveContent(contentId: string, userId: string): Promise<{ status: string }> {
    try {
      const formData = new FormData();
      formData.append('user_id', userId);

      const response = await fetch(`${this.baseUrl}/content/approve/${contentId}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Content approval failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error approving content:', error);
      throw error;
    }
  }

  /**
   * Get pending content approvals for user
   */
  async getPendingApprovals(userId: string): Promise<{ pending_approvals: PendingApproval[] }> {
    try {
      const response = await fetch(`${this.baseUrl}/content/pending/${userId}`);

      if (!response.ok) {
        throw new Error(`Failed to get pending approvals: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting pending approvals:', error);
      throw error;
    }
  }

  /**
   * Get available content templates
   */
  async getAvailableTemplates(): Promise<{ templates: Array<{ type: string; name: string; description: string }> }> {
    try {
      const response = await fetch(`${this.baseUrl}/templates`);

      if (!response.ok) {
        throw new Error(`Failed to get templates: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting templates:', error);
      throw error;
    }
  }

  /**
   * Health check for voice service
   */
  async healthCheck(): Promise<{ status: string; service: string; timestamp: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking voice service health:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const voiceService = new VoiceService();

// Export types for use in components
export type {
  VoiceProcessingRequest,
  VoiceProcessingResponse,
  ContentGenerationRequest,
  ContentGenerationResponse,
  VoiceRequestStatus,
  PendingApproval,
};
