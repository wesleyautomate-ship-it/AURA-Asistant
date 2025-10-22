import api from './http'

export interface CreateRequestPayload {
  type: 'brochure'
  draftId: string
  pdfUrl?: string
}

export interface CreateRequestResponse {
  id: string
  status: 'Pending' | 'Ready'
}

function fallbackCreateRequest(payload: CreateRequestPayload): CreateRequestResponse {
  const id = typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : 'req_' + Math.random().toString(36).slice(2, 10)

  return {
    id,
    status: payload.pdfUrl ? 'Ready' : 'Pending',
  }
}

const mapRequestType = (payload: CreateRequestPayload): string => {
  switch (payload.type) {
    case 'brochure':
      return 'presentation'
    default:
      return payload.type
  }
}

export async function createRequest(payload: CreateRequestPayload): Promise<CreateRequestResponse> {
  if (!api.enabled) {
    return fallbackCreateRequest(payload)
  }

  try {
    const requestType = mapRequestType(payload)
    const requestContent = payload.pdfUrl
      ? `Final brochure uploaded for draft ${payload.draftId}`
      : `Brochure generation requested for draft ${payload.draftId}`

    const { data } = await api.post<{ request_id: number; status?: string }>(
      '/ai-assistant/requests',
      {
        request_type: requestType,
        request_content: requestContent,
        request_metadata: {
          draft_id: payload.draftId,
          pdf_url: payload.pdfUrl ?? null,
          origin: 'command_center',
        },
        priority: payload.pdfUrl ? 'normal' : 'high',
        output_format: payload.pdfUrl ? 'pdf' : 'text',
      }
    )

    const id = data.request_id ? String(data.request_id) : undefined
    const status: CreateRequestResponse['status'] =
      (data.status ?? '').toLowerCase() === 'completed' ? 'Ready' : 'Pending'

    if (!id) {
      const fallback = fallbackCreateRequest(payload)
      return { ...fallback, status }
    }

    return { id, status }
  } catch (error) {
    console.warn('[RequestsApi] Falling back to local request stub:', error)
    return fallbackCreateRequest(payload)
  }
}
