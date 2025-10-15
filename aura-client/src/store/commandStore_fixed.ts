import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Mode = 'text' | 'voice';
export type Phase = 'idle' | 'listening' | 'paused' | 'stopped' | 'thinking' | 'responding';
export type RequestStatus = 'Pending' | 'Processing' | 'Complete' | 'Error';
export type RequestType = 'CMA' | 'MARKET_REPORT' | 'SOCIAL_POST' | 'CMA_REPORT' | 'PITCH_DECK' | 'GENERIC';
export type ContentType = 'CMA_REPORT' | 'PITCH_DECK' | 'SOCIAL_POST' | 'MARKET_REPORT';

// Intelligence Content v3.3 - Enhanced AI-generated content with memory context
export interface IntelligenceContent {
  contentId: string;
  taskId: string;
  contentType: ContentType;
  title: string;
  enhanced: boolean;
  qualityScore: number;
  memoryContext: {
    relevantMemories: string[];
    contextualInsights: string[];
    brandAlignment: number;
  };
  generatedContent: {
    structured: Record<string, any>;
    narrative: string;
    keyInsights: string[];
    actionableRecommendations: string[];
  };
  metadata: {
    generationTimestamp: string;
    model: string;
    processingTime: number;
    confidenceLevel: number;
    sources: string[];
  };
  exportReady: boolean;
  version: string;
}

export interface CommandHistoryItem {
  id: string;
  timestamp: number;
  command: string;
  response?: string;
  successful: boolean;
}

export interface RequestItem {
  id: string;
  timestamp: number;
  title: string;
  summary?: string;
  type: RequestType;
  status: RequestStatus;
  contentId?: string;
  metadata?: {
    model?: string;
    processingTime?: number;
    tokens?: number;
    content_id?: string;
    task_id?: string;
  };
}

interface CommandStore {
  // UI State
  isOpen: boolean;
  isCollapsed: boolean;
  mode: Mode;
  phase: Phase;
  prefillPrompt: string | null;
  
  // Data
  history: CommandHistoryItem[];
  responses: string[];
  requests: RequestItem[];
  generatedContent: Record<string, any>;
  intelContent: Record<string, IntelligenceContent>;
  
  // Actions
  open: () => void;
  close: () => void;
  toggle: () => void;
  setMode: (mode: Mode) => void;
  setPhase: (phase: Phase) => void;
  setPrefillPrompt: (prompt: string | null) => void;
  addToHistory: (command: string, response: string, successful?: boolean) => void;
  clearHistory: () => void;
  addRequest: (request: Omit<RequestItem, 'id' | 'timestamp'>) => string;
  updateRequest: (id: string, updates: Partial<RequestItem>) => void;
  removeRequest: (id: string) => void;
  clearRequests: () => void;
  
  // Intelligence Content Actions
  addIntelligenceContent: (content: Omit<IntelligenceContent, 'contentId'>) => string;
  getIntelligenceContent: (contentId: string) => IntelligenceContent | undefined;
  getIntelligenceContentByTaskId: (taskId: string) => IntelligenceContent | undefined;
  removeIntelligenceContent: (contentId: string) => void;
  updateIntelligenceContent: (contentId: string, updates: Partial<IntelligenceContent>) => void;
  listIntelligenceContent: () => IntelligenceContent[];
  persistIntelligenceContent: () => void;
  markIntelligenceContentReady: (contentId: string) => void;
}

export const useCommandStore = create<CommandStore>()(persist(
  (set, get) => ({
    // UI State
    isOpen: false,
    isCollapsed: false,
    mode: 'voice',
    phase: 'idle',
    prefillPrompt: null,
    
    // Data
    history: [],
    responses: [],
    requests: [],
    generatedContent: (() => {
      if (typeof window === 'undefined') return {};
      try {
        const saved = localStorage.getItem('aura_generated_content');
        return saved ? JSON.parse(saved) : {};
      } catch (error) {
        console.warn('[Content] Failed to load persisted content:', error);
        return {};
      }
    })(),
    
    // Intelligence Content v3.3 - Load from local storage or initialize empty
    intelContent: (() => {
      if (typeof window === 'undefined') return {};
      try {
        const saved = localStorage.getItem('aura.intelContent.v1');
        return saved ? JSON.parse(saved) : {};
      } catch (error) {
        console.warn('[IntelContent] Failed to load persisted intelligence content:', error);
        return {};
      }
    })(),
    
    // Actions
    open: () => set({ isOpen: true }),
    close: () => set({ isOpen: false, prefillPrompt: null }),
    toggle: () => set((state) => ({ isOpen: !state.isOpen })),
    setMode: (mode: Mode) => set({ mode }),
    setPhase: (phase: Phase) => set({ phase }),
    setPrefillPrompt: (prompt: string | null) => set({ prefillPrompt: prompt }),
    
    addToHistory: (command: string, response: string, successful = true) => {
      const newItem: CommandHistoryItem = {
        id: crypto.randomUUID(),
        timestamp: Date.now(),
        command,
        response,
        successful
      };
      set((state) => ({
        history: [...state.history, newItem].slice(-100) // Keep last 100 items
      }));
    },
    
    clearHistory: () => set({ history: [] }),
    
    addRequest: (request: Omit<RequestItem, 'id' | 'timestamp'>) => {
      const id = crypto.randomUUID();
      const newRequest: RequestItem = {
        ...request,
        id,
        timestamp: Date.now()
      };
      set((state) => ({
        requests: [newRequest, ...state.requests]
      }));
      return id;
    },
    
    updateRequest: (id: string, updates: Partial<RequestItem>) => {
      set((state) => ({
        requests: state.requests.map(req => 
          req.id === id ? { ...req, ...updates } : req
        )
      }));
    },
    
    removeRequest: (id: string) => {
      set((state) => ({
        requests: state.requests.filter(req => req.id !== id)
      }));
    },
    
    clearRequests: () => set({ requests: [] }),
    
    // Intelligence Content Actions
    addIntelligenceContent: (content: Omit<IntelligenceContent, 'contentId'>) => {
      const contentId = crypto.randomUUID();
      const newContent: IntelligenceContent = {
        ...content,
        contentId,
      };
      
      set((state) => ({
        intelContent: {
          ...state.intelContent,
          [contentId]: newContent
        }
      }));
      
      console.log('[IntelContent] Added new intelligence content:', contentId);
      get().persistIntelligenceContent();
      return contentId;
    },
    
    getIntelligenceContent: (contentId: string) => {
      const state = get();
      return state.intelContent[contentId];
    },
    
    getIntelligenceContentByTaskId: (taskId: string) => {
      const state = get();
      return Object.values(state.intelContent).find(content => content.taskId === taskId);
    },
    
    removeIntelligenceContent: (contentId: string) => {
      set((state) => {
        const updatedContent = { ...state.intelContent };
        delete updatedContent[contentId];
        return { intelContent: updatedContent };
      });
      console.log('[IntelContent] Removed intelligence content:', contentId);
      get().persistIntelligenceContent();
    },
    
    updateIntelligenceContent: (contentId: string, updates: Partial<IntelligenceContent>) => {
      set((state) => {
        const existing = state.intelContent[contentId];
        if (!existing) {
          console.warn('[IntelContent] Cannot update non-existent intelligence content:', contentId);
          return state;
        }
        
        return {
          intelContent: {
            ...state.intelContent,
            [contentId]: {
              ...existing,
              ...updates,
              metadata: {
                ...existing.metadata,
                ...(updates.metadata || {})
              }
            }
          }
        };
      });
      console.log('[IntelContent] Updated intelligence content:', contentId);
      get().persistIntelligenceContent();
    },
    
    listIntelligenceContent: () => {
      const state = get();
      return Object.values(state.intelContent)
        .sort((a, b) => new Date(b.metadata.generationTimestamp).getTime() - 
                         new Date(a.metadata.generationTimestamp).getTime());
    },
    
    persistIntelligenceContent: (() => {
      let timeoutId: NodeJS.Timeout | null = null;
      
      return () => {
        // Debounce: wait 500ms before persisting
        if (timeoutId) {
          clearTimeout(timeoutId);
        }
        
        timeoutId = setTimeout(() => {
          try {
            const state = get();
            const serialized = JSON.stringify(state.intelContent);
            localStorage.setItem('aura.intelContent.v1', serialized);
            console.log('[IntelContent] Persisted intelligence content:', 
                       Object.keys(state.intelContent).length, 'items');
          } catch (error) {
            console.error('[IntelContent] Failed to persist intelligence content:', error);
          }
        }, 500);
      };
    })(),
    
    markIntelligenceContentReady: (contentId: string) => {
      const content = get().intelContent[contentId];
      if (!content) {
        console.warn('[IntelContent] Cannot mark non-existent content as ready:', contentId);
        return;
      }
      
      get().updateIntelligenceContent(contentId, {
        exportReady: true
      });
      console.log('[IntelContent] Marked intelligence content as export-ready:', contentId);
    },
  }),
  {
    name: 'aura-command-store',
    partialize: (state) => ({ 
      history: state.history,
      requests: state.requests,
      generatedContent: state.generatedContent,
      intelContent: state.intelContent,
    }),
  }
));