export interface CreateRequestPayload {
  type: 'brochure';
  draftId: string;
  pdfUrl?: string;
}

export interface CreateRequestResponse {
  id: string;
  status: 'Pending' | 'Ready';
}

function makeId() {
  try {
    return crypto.randomUUID();
  } catch {
    return 'req_' + Math.random().toString(36).slice(2, 10);
  }
}

// Stubbed POST to backend; replace with real fetch later
export async function createRequest(payload: CreateRequestPayload): Promise<CreateRequestResponse> {
  // simulate network
  await new Promise((r) => setTimeout(r, 250));
  const id = makeId();
  const status: 'Pending' | 'Ready' = payload.pdfUrl ? 'Ready' : 'Pending';
  return { id, status };
}

