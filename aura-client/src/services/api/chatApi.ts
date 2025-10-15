export type ChatEvent =
  | { type: 'thinking'; data: any }
  | { type: 'retrieval'; data: { items: { source: string; snippet: string; score?: number }[] } }
  | { type: 'message'; data: { content: string } }
  | { type: 'tool_invocation'; data: { name: string; task_id: string } }
  | { type: 'tool_result'; data: any }
  | { type: 'final'; data: { done: boolean; thread_id: string } };

export interface StartChatOptions {
  threadId?: string;
  message: string;
  metadata?: Record<string, any>;
  onEvent: (evt: ChatEvent) => void;
}

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

function getAuthHeaders() {
  try {
    const token = localStorage.getItem('authToken') || localStorage.getItem('auth_token') || sessionStorage.getItem('authToken');
    if (token) return { Authorization: `Bearer ${token}` } as Record<string, string>;
  } catch {}
  return {};
}

export function startChat(opts: StartChatOptions) {
  const controller = new AbortController();

  (async () => {
    async function openStream(url: string) {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
        body: JSON.stringify({ thread_id: opts.threadId, message: opts.message, metadata: opts.metadata || { source: 'chat_ui' } }),
        signal: controller.signal,
      });
      if (!res.ok || !res.body) throw new Error(`Failed to start chat stream: ${res.status}`);
      return res.body.getReader();
    }

    let reader: ReadableStreamDefaultReader<Uint8Array>;
    try {
      reader = await openStream(`${API_BASE_URL}/api/v1/intelligence/chat`);
    } catch (e) {
      // Fallback to relative path; useful when Vite proxy is configured
      reader = await openStream(`/api/v1/intelligence/chat`);
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // Split SSE events on double newlines
      let idx;
      while ((idx = buffer.indexOf('\n\n')) !== -1) {
        const raw = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);

        let eventType: string | null = null;
        let dataLine = '';
        for (const line of raw.split('\n')) {
          if (line.startsWith('event:')) eventType = line.slice(6).trim();
          if (line.startsWith('data:')) dataLine += line.slice(5).trim();
        }
        if (!eventType || !dataLine) continue;

        try {
          const data = JSON.parse(dataLine);
          const evt = { type: eventType, data } as ChatEvent;
          // @ts-ignore
          opts.onEvent(evt);
        } catch (_) {
          // ignore malformed chunks
        }
      }
    }
  })().catch(() => {
    // Swallow for now; UI can reflect errors via store
  });

  return {
    cancel: () => controller.abort(),
  };
}
