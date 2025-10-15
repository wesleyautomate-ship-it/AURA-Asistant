import { create } from 'zustand';
import { startChat, ChatEvent } from '../services/api/chatApi';

export type ChatMessage = { id: string; role: 'user'|'assistant'|'system'; text: string };
export type ChatThread = { id: string; title?: string|null; createdAt?: string };

type State = {
  threads: ChatThread[];
  messagesByThread: Record<string, ChatMessage[]>;
  currentThreadId?: string;
  isStreaming: boolean;
  retrievalItems: { source: string; snippet: string; score?: number }[];
  lastToolEvent?: { name: string; task_id: string };
  startChat: (message: string) => void;
  createThread: () => string;
  setCurrentThread: (id: string) => void;
  receiveEvent: (evt: ChatEvent) => void;
  renameThread: (id: string, title: string) => void;
  loadThreads: () => void;
};

export const useChatStore = create<State>((set, get) => ({
  threads: [],
  messagesByThread: {},
  isStreaming: false,
  retrievalItems: [],
  lastToolEvent: undefined,

  createThread: () => {
    const id = crypto.randomUUID();
    set((s) => ({ threads: [{ id, title: null }, ...s.threads], currentThreadId: id }));
    return id;
  },

  setCurrentThread: (id) => set({ currentThreadId: id }),

  startChat: (message: string) => {
    const state = get();
    let threadId = state.currentThreadId;
    if (!threadId) threadId = get().createThread();

    // push user message
    const umsg: ChatMessage = { id: crypto.randomUUID(), role: 'user', text: message };
    set((s) => ({
      messagesByThread: {
        ...s.messagesByThread,
        [threadId!]: [...(s.messagesByThread[threadId!] || []), umsg],
      },
      isStreaming: true,
      retrievalItems: [],
    }));

    // Kick off SSE
    startChat({ threadId, message, onEvent: get().receiveEvent });
  },

  receiveEvent: (evt: ChatEvent) => {
    const { currentThreadId } = get();
    if (!currentThreadId) return;

    if (evt.type === 'retrieval') {
      set({ retrievalItems: evt.data.items || [] });
    } else if (evt.type === 'message') {
      const chunk = evt.data.content || '';
      set((s) => {
        const existing = s.messagesByThread[currentThreadId] || [];
        const last = existing[existing.length - 1];
        if (last && last.role === 'assistant') {
          const updated = [...existing];
          updated[updated.length - 1] = { ...last, text: (last.text || '') + chunk };
          return { messagesByThread: { ...s.messagesByThread, [currentThreadId]: updated } };
        } else {
          return {
            messagesByThread: {
              ...s.messagesByThread,
              [currentThreadId]: [...existing, { id: crypto.randomUUID(), role: 'assistant', text: chunk }],
            },
          };
        }
      });
    } else if (evt.type === 'tool_invocation') {
      set({ lastToolEvent: { name: evt.data.name, task_id: evt.data.task_id } });
    } else if (evt.type === 'final') {
      set({ isStreaming: false });
      // Set thread title if empty
      set((s) => {
        const threads = s.threads.map((t) => (t.id === s.currentThreadId && !t.title ? { ...t, title: (s.messagesByThread[t.id]?.[0]?.text || '').slice(0, 40) } : t));
        return { threads };
      });
    }
  },

  renameThread: (id, title) => set((s) => ({ threads: s.threads.map((t) => (t.id === id ? { ...t, title } : t)) })),

  loadThreads: () => {
    // Placeholder: would call backend to fetch threads list
  },
}));
