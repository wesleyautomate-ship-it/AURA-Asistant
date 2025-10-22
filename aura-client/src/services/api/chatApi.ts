import api from '../http';
import type { AxiosProgressEvent } from 'axios';

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

export function startChat(opts: StartChatOptions) {
  const controller = new AbortController();
  let buffer = '';
  let processedLength = 0;

  const flushBuffer = () => {
    let idx: number;
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
      } catch {
        // ignore malformed chunks
      }
    }
  };

  api
    .post(
      '/intelligence/chat',
      {
        thread_id: opts.threadId,
        message: opts.message,
        metadata: opts.metadata || { source: 'chat_ui' },
      },
      {
        signal: controller.signal,
        responseType: 'text',
        onDownloadProgress: (event: AxiosProgressEvent) => {
          const xhr: any = (event as any).event?.target || (event as any).target;
          if (!xhr || typeof xhr.responseText !== 'string') {
            return;
          }
          const current: string = xhr.responseText;
          const nextChunk = current.substring(processedLength);
          processedLength = current.length;
          if (nextChunk) {
            buffer += nextChunk;
            flushBuffer();
          }
        },
      }
    )
    .then((response) => {
      if (typeof response.data === 'string' && response.data.length > processedLength) {
        buffer += response.data.substring(processedLength);
        flushBuffer();
      }
    })
    .catch(() => {
      // Swallow for now; UI can reflect errors via store
    });

  return {
    cancel: () => controller.abort(),
  };
}
