// API Service for Aura Backend Integration

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface TranscriptionResponse {
  transcript: string;
  confidence?: number;
  language?: string;
}

export interface AIStreamResponse {
  content: string;
  done: boolean;
  error?: string;
}

/**
 * Generate mock transcription for development/testing
 */
function generateMockTranscription(): string {
  const mockTranscriptions = [
    'Generate a comprehensive CMA for Downtown Dubai with pricing trends and market analysis.',
    'Create a marketing campaign for my luxury villa listing in Palm Jumeirah.',
    'Analyze recent sales data for apartments in Dubai Marina.',
    'Prepare a detailed property valuation report for my client.',
    'Generate social media content for this week\'s featured listings.',
    'Create a buyer presentation for first-time homebuyers in Dubai.',
    'Analyze market trends for commercial properties in Business Bay.',
    'Generate an investment analysis report for Dubai real estate.',
  ];
  return mockTranscriptions[Math.floor(Math.random() * mockTranscriptions.length)];
}

/**
 * Transcribe audio blob to text using backend API or mock data
 */
export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const useRealTranscription = import.meta.env.VITE_USE_REAL_TRANSCRIPTION === 'true';
  
  // Mock transcription mode (faster, no API required)
  if (!useRealTranscription) {
    console.log('[Transcription] Using mock mode');
    // Simulate API delay for realistic UX
    await new Promise(resolve => setTimeout(resolve, 800));
    return generateMockTranscription();
  }
  
  // Real transcription mode (requires backend API)
  try {
    console.log('[Transcription] Using real API mode');
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');

    const response = await fetch(`${API_BASE_URL}/api/v1/voice/transcribe`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Transcription failed: ${response.statusText}`);
    }

    const data: TranscriptionResponse = await response.json();
    return data.transcript;
  } catch (error) {
    console.error('[Transcription] API error:', error);
    console.log('[Transcription] Falling back to mock mode');
    // Fallback to mock on API failure
    return generateMockTranscription();
  }
}

/**
 * Stream AI response using Server-Sent Events (SSE)
 */
export function streamAIResponse(
  prompt: string,
  onChunk: (text: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void
): () => void {
  try {
    const encodedPrompt = encodeURIComponent(prompt);
    const eventSource = new EventSource(
      `${API_BASE_URL}/api/v1/ai_request/stream?prompt=${encodedPrompt}`
    );

    let isClosed = false;
    let safetyTimeoutId: number | null = null;

    const cleanup = () => {
      if (isClosed) return;
      isClosed = true;
      
      if (safetyTimeoutId !== null) {
        clearTimeout(safetyTimeoutId);
        safetyTimeoutId = null;
      }
      
      eventSource.close();
      console.log('[SSE] Connection closed and cleaned up');
    };

    eventSource.onmessage = (event) => {
      try {
        const data: AIStreamResponse = JSON.parse(event.data);
        
        if (data.error) {
          console.error('[SSE] Stream error:', data.error);
          onError(new Error(data.error));
          cleanup();
          return;
        }

        if (data.content) {
          onChunk(data.content);
        }

        if (data.done) {
          console.log('[SSE] Stream completed successfully');
          onComplete();
          cleanup();
        }
      } catch (err) {
        console.error('[SSE] Failed to parse stream data:', err);
        onError(new Error('Failed to parse stream data'));
        cleanup();
      }
    };

    eventSource.onerror = (error) => {
      console.error('[SSE] Connection error:', error);
      onError(new Error('Stream connection failed'));
      cleanup();
    };

    // Safety timeout: auto-close after 30 seconds to prevent hanging
    safetyTimeoutId = window.setTimeout(() => {
      console.warn('[SSE] Safety timeout triggered - closing connection');
      cleanup();
      onError(new Error('Stream timeout - no response received'));
    }, 30000);

    // Return cleanup function
    return cleanup;
  } catch (error) {
    console.error('[SSE] Failed to initialize stream:', error);
    onError(error as Error);
    return () => {};
  }
}

/**
 * Fallback: Use fetch with streaming for browsers that don't support SSE well
 */
export async function streamAIResponseFetch(
  prompt: string,
  onChunk: (text: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void
): Promise<() => void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai_request/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error(`AI request failed: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No response body');
    }

    let aborted = false;

    const read = async () => {
      try {
        while (!aborted) {
          const { done, value } = await reader.read();
          
          if (done) {
            onComplete();
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          onChunk(chunk);
        }
      } catch (error) {
        if (!aborted) {
          onError(error as Error);
        }
      }
    };

    read();

    // Return cleanup function
    return () => {
      aborted = true;
      reader.cancel();
    };
  } catch (error) {
    onError(error as Error);
    return () => {};
  }
}

/**
 * Check if backend API is available
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });
    return response.ok;
  } catch (error) {
    console.warn('Backend health check failed:', error);
    return false;
  }
}
