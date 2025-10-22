// API Service utilities for transcription and streaming

import api from './http'
import { getAuthToken } from '../store/authStore'

const API_BASE_URL = api.defaults.baseURL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export interface TranscriptionResponse {
  transcript: string
  confidence?: number
  language?: string
}

export interface AIStreamResponse {
  content: string
  done: boolean
  error?: string
}

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
  ]
  return mockTranscriptions[Math.floor(Math.random() * mockTranscriptions.length)]
}

export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const auraMockMode = import.meta.env.VITE_AURA_MOCK_MODE === 'true'
  const legacyMockMode = import.meta.env.VITE_USE_REAL_TRANSCRIPTION !== 'true'
  const useMock = auraMockMode || legacyMockMode

  if (useMock) {
    console.log('[Transcription] Using mock mode')
    if (auraMockMode) {
      try {
        const { simulateMockTranscription } = await import('../mocks/transcriptionPrompts')
        return await simulateMockTranscription()
      } catch (error) {
        console.warn('[Transcription] Mock transcription import failed, using fallback:', error)
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 800))
    return generateMockTranscription()
  }

  try {
    const formData = new FormData()
    formData.append('file', audioBlob, 'recording.webm')
    const { data } = await api.post<TranscriptionResponse>('/voice/transcribe', formData)
    return data.transcript
  } catch (error) {
    console.error('[Transcription] API error:', error)
    return generateMockTranscription()
  }
}

export function streamAIResponse(
  prompt: string,
  onChunk: (text: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void
): () => void {
  const token = getAuthToken()

  if (token) {
    let cancelled = false
    let cleanup: (() => void) | null = null

    ;(async () => {
      try {
        const fn = await streamAIResponseFetch(prompt, onChunk, onComplete, onError, token)
        if (cancelled) {
          fn()
        } else {
          cleanup = fn
        }
      } catch (error) {
        onError(error as Error)
      }
    })()

    return () => {
      cancelled = true
      if (cleanup) cleanup()
    }
  }

  try {
    const encodedPrompt = encodeURIComponent(prompt)
    const eventSource = new EventSource(`${API_BASE_URL}/ai_request/stream?prompt=${encodedPrompt}`)
    let isClosed = false
    let safetyTimeoutId: number | null = null

    const cleanup = () => {
      if (isClosed) return
      isClosed = true
      if (safetyTimeoutId !== null) {
        clearTimeout(safetyTimeoutId)
        safetyTimeoutId = null
      }
      eventSource.close()
      console.log('[SSE] Connection closed and cleaned up')
    }

    eventSource.onmessage = (event) => {
      try {
        const data: AIStreamResponse = JSON.parse(event.data)
        if (data.error) {
          onError(new Error(data.error))
          cleanup()
          return
        }
        if (data.content) onChunk(data.content)
        if (data.done) {
          onComplete()
          cleanup()
        }
      } catch (err) {
        onError(new Error('Failed to parse stream data'))
        cleanup()
      }
    }

    eventSource.onerror = (error) => {
      console.error('[SSE] Connection error:', error)
      onError(new Error('Stream connection failed'))
      cleanup()
    }

    safetyTimeoutId = window.setTimeout(() => {
      console.warn('[SSE] Safety timeout triggered - closing connection')
      cleanup()
      onError(new Error('Stream timeout - no response received'))
    }, 30000)

    return cleanup
  } catch (error) {
    onError(error as Error)
    return () => {}
  }
}

export async function streamAIResponseFetch(
  prompt: string,
  onChunk: (text: string) => void,
  onComplete: () => void,
  onError: (error: Error) => void,
  token?: string
): Promise<() => void> {
  try {
    const { data } = await api.post<string>(
      '/ai_request/stream',
      { prompt },
      {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        responseType: 'text',
        transformResponse: [(value) => value],
      }
    )

    if (typeof data === 'string') {
      onChunk(data)
    }
    onComplete()
  } catch (error) {
    onError(error as Error)
  }

  return () => {}
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    await api.get('/health', { timeout: 5000 })
    return true
  } catch (error) {
    console.warn('Backend health check failed:', error)
    return false
  }
}
