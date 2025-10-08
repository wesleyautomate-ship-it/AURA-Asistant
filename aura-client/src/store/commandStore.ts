import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Mode = 'text' | 'voice';
export type Phase = 'idle' | 'listening' | 'paused' | 'stopped' | 'thinking' | 'responding';
export type RequestStatus = 'Pending' | 'Processing' | 'Complete' | 'Error';
export type RequestType = 'CMA' | 'MARKET_REPORT' | 'SOCIAL_POST' | 'GENERIC';

export interface CommandHistoryItem {
  text: string;
  mode: Mode;
  at: number;
}

export interface RequestMetadata {
  location?: string;
  topic?: string;
  confidence?: number;
  report_url?: string;
  [key: string]: any;
}

export interface Request {
  id: string;
  title: string;
  status: RequestStatus;
  type: RequestType;
  timestamp: number;
  error?: string;
  metadata?: RequestMetadata;
}

interface CommandStore {
  isOpen: boolean;
  mode: Mode;
  phase: Phase;
  history: CommandHistoryItem[];
  responses: string[];
  requests: Request[];
  open: () => void;
  close: () => void;
  setMode: (mode: Mode) => void;
  setPhase: (phase: Phase) => void;
  togglePause: () => void;
  addHistory: (text: string, mode?: Mode) => void;
  addResponse: (response: string) => void;
  addRequest: (title: string, type?: RequestType, metadata?: Record<string, any>) => string;
  updateRequestStatus: (id: string, status: RequestStatus, error?: string) => void;
  reset: () => void;
}

export const useCommandStore = create<CommandStore>()(persist(
  (set, get) => ({
    isOpen: false,
    mode: 'voice',
    phase: 'idle',
    history: [],
    responses: [],
    requests: [],
  
  open: () => set({ isOpen: true, mode: 'voice', phase: 'idle' }),
  
  close: () => set({ isOpen: false, phase: 'idle' }),
  
  setMode: (mode: Mode) => set({ 
    mode, 
    phase: mode === 'voice' ? 'idle' : get().phase 
  }),
  
  setPhase: (phase: Phase) => set({ phase }),
  
  togglePause: () => set((state) => ({
    phase: state.phase === 'paused' ? 'listening' : 'paused'
  })),
  
  addHistory: (text: string, mode?: Mode) => set((state) => ({
    history: [
      { text, mode: mode || state.mode, at: Date.now() },
      ...state.history.slice(0, 4), // Keep last 5 items
    ],
  })),
  
  addResponse: (response: string) => set((state) => ({
    responses: [response, ...state.responses.slice(0, 4)],
  })),
  
  addRequest: (title: string, type: RequestType = 'GENERIC', metadata?: Record<string, any>) => {
    const id = crypto.randomUUID();
    set((state) => ({
      requests: [
        { id, title, status: 'Pending' as RequestStatus, type, timestamp: Date.now(), metadata },
        ...state.requests,
      ].slice(0, 20), // Keep latest 20 requests
    }));
    return id;
  },
  
  updateRequestStatus: (id: string, status: RequestStatus, error?: string) => set((state) => ({
    requests: state.requests.map((req) =>
      req.id === id ? { ...req, status, error } : req
    ),
  })),
  
  reset: () => set({ phase: 'idle' }),
}),
{
  name: 'aura-command-store',
  partialize: (state) => ({ 
    history: state.history,
    requests: state.requests,
  }),
}
));
