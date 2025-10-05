import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { AIRequestService, AIRequestCreatePayload, createRequestFromCommand } from '@propertypro/services';
import { useUIStore } from './uiStore';
import type { Request } from '@propertypro/features';

export interface RequestCounts {
  total: number;
  queued: number;
  processing: number;
  draft_ready: number;
  approved: number;
  failed: number;
}

interface AIRequestState {
  // Data
  byId: Record<number, Request>;
  allIds: number[];
  
  // UI State
  loading: boolean;
  error: string | null;
  streaming: Record<string, () => void>; // requestId -> unsubscribe function
  counts: RequestCounts;
  selectedRequestId: number | null;
  
  // Actions
  fetchAll: (params?: { status?: string; team?: string; limit?: number; offset?: number }) => Promise<void>;
  create: (payload: AIRequestCreatePayload) => Promise<Request>;
  createFromCommand: (content: string, team?: string, priority?: number) => Promise<Request>;
  getOne: (id: string) => Promise<void>;
  approve: (id: number) => Promise<void>;
  revise: (id: number, instructions: string) => Promise<void>;
  subscribeTo: (id: string) => void;
  unsubscribeFrom: (id: string) => void;
  unsubscribeAll: () => void;
  upsert: (request: Request) => void;
  remove: (id: number) => void;
  computeCounts: () => void;
  setSelectedRequest: (id: number | null) => void;
  clearError: () => void;
  reset: () => void;
}

const initialCounts: RequestCounts = {
  total: 0,
  queued: 0,
  processing: 0,
  draft_ready: 0,
  approved: 0,
  failed: 0,
};

const initialState = {
  byId: {},
  allIds: [],
  loading: false,
  error: null,
  streaming: {},
  counts: initialCounts,
  selectedRequestId: null,
};

export const useAIRequestStore = create<AIRequestState>()(devtools((set, get) => ({
  ...initialState,

  fetchAll: async (params) => {
    const { startLoading, stopLoading, pushSnackbar } = useUIStore.getState();
    
    set({ loading: true, error: null });
    startLoading();

    try {
      const requests = await AIRequestService.listRequests(params);
      
      const byId: Record<number, Request> = {};
      const allIds: number[] = [];
      
      requests.forEach(request => {
        byId[request.id] = request;
        allIds.push(request.id);
      });
      
      set({ byId, allIds, loading: false });
      get().computeCounts();
      
      // Subscribe to any in-flight requests
      requests
        .filter(r => ['Queued', 'Processing'].includes(r.status))
        .forEach(request => {
          // Convert number id back to string for API calls
          get().subscribeTo(request.id.toString());
        });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch requests';
      set({ error: errorMessage, loading: false });
      pushSnackbar({
        id: `fetch-error-${Date.now()}`,
        message: `Error loading requests: ${errorMessage}`,
        type: 'error',
      });
    } finally {
      stopLoading();
    }
  },

  create: async (payload) => {
    const { startLoading, stopLoading, pushSnackbar } = useUIStore.getState();
    
    set({ error: null });
    startLoading();

    try {
      const request = await AIRequestService.createRequest(payload);
      
      get().upsert(request);
      get().computeCounts();
      
      // Subscribe to updates for the new request
      get().subscribeTo(request.id.toString());
      
      pushSnackbar({
        id: `request-created-${request.id}`,
        message: `AI request created: ${request.title.slice(0, 50)}${request.title.length > 50 ? '...' : ''}`,
        type: 'success',
      });

      return request;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create request';
      set({ error: errorMessage });
      pushSnackbar({
        id: `create-error-${Date.now()}`,
        message: `Error creating request: ${errorMessage}`,
        type: 'error',
      });
      throw error;
    } finally {
      stopLoading();
    }
  },

  createFromCommand: async (content, team = 'marketing', priority = 5) => {
    return get().create({ team, content, priority });
  },

  getOne: async (id) => {
    const { pushSnackbar } = useUIStore.getState();
    
    set({ error: null });

    try {
      const request = await AIRequestService.getRequest(id);
      get().upsert(request);
      get().computeCounts();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch request';
      set({ error: errorMessage });
      pushSnackbar({
        id: `get-error-${Date.now()}`,
        message: `Error loading request: ${errorMessage}`,
        type: 'error',
      });
    }
  },

  approve: async (id) => {
    const { pushSnackbar } = useUIStore.getState();
    const state = get();
    const request = state.byId[id];
    
    if (!request) return;

    set({ error: null });

    try {
      await AIRequestService.approveRequest(id.toString());
      
      // Update the request status
      const updatedRequest = { 
        ...request, 
        status: 'Ready for Review' as const,
        progress: 100 
      };
      
      get().upsert(updatedRequest);
      get().computeCounts();
      
      // Stop streaming for this request
      get().unsubscribeFrom(id.toString());
      
      pushSnackbar({
        id: `approve-success-${id}`,
        message: 'Request approved successfully',
        type: 'success',
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to approve request';
      set({ error: errorMessage });
      pushSnackbar({
        id: `approve-error-${Date.now()}`,
        message: `Error approving request: ${errorMessage}`,
        type: 'error',
      });
    }
  },

  revise: async (id, instructions) => {
    const { pushSnackbar } = useUIStore.getState();
    const state = get();
    const request = state.byId[id];
    
    if (!request) return;

    set({ error: null });

    try {
      await AIRequestService.reviseRequest(id.toString(), instructions);
      
      // Update the request status
      const updatedRequest = { 
        ...request, 
        status: 'Processing' as const,
        progress: 0 
      };
      
      get().upsert(updatedRequest);
      get().computeCounts();
      
      // Re-subscribe to updates
      get().subscribeTo(id.toString());
      
      pushSnackbar({
        id: `revise-success-${id}`,
        message: 'Revision requested successfully',
        type: 'success',
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to request revision';
      set({ error: errorMessage });
      pushSnackbar({
        id: `revise-error-${Date.now()}`,
        message: `Error requesting revision: ${errorMessage}`,
        type: 'error',
      });
    }
  },

  subscribeTo: (id) => {
    const state = get();
    
    // Guard against double subscription
    if (state.streaming[id]) {
      return;
    }

    const unsubscribe = AIRequestService.subscribeToRequestStream(
      id,
      {
        onUpdate: (request) => {
          console.debug(`[SSE] Request ${id} updated:`, request.status, `${request.progress}%`);
          get().upsert(request);
          get().computeCounts();
        },
        onError: (error) => {
          console.error(`[SSE] Error for request ${id}:`, error);
          const { pushSnackbar } = useUIStore.getState();
          pushSnackbar({
            id: `sse-error-${id}`,
            message: `Connection error for request updates: ${error.message}`,
            type: 'error',
          });
          
          // Remove from streaming
          set(state => {
            const newStreaming = { ...state.streaming };
            delete newStreaming[id];
            return { streaming: newStreaming };
          });
        },
        onOpen: () => {
          console.debug(`[SSE] Connected to request ${id}`);
        },
        onClose: () => {
          console.debug(`[SSE] Disconnected from request ${id}`);
          // Remove from streaming
          set(state => {
            const newStreaming = { ...state.streaming };
            delete newStreaming[id];
            return { streaming: newStreaming };
          });
        },
      }
    );

    set(state => ({
      streaming: { ...state.streaming, [id]: unsubscribe }
    }));
  },

  unsubscribeFrom: (id) => {
    const state = get();
    const unsubscribe = state.streaming[id];
    
    if (unsubscribe) {
      unsubscribe();
      
      set(state => {
        const newStreaming = { ...state.streaming };
        delete newStreaming[id];
        return { streaming: newStreaming };
      });
    }
  },

  unsubscribeAll: () => {
    const state = get();
    
    Object.values(state.streaming).forEach(unsubscribe => {
      unsubscribe();
    });
    
    set({ streaming: {} });
  },

  upsert: (request) => {
    set(state => {
      const newById = { ...state.byId, [request.id]: request };
      const newAllIds = state.allIds.includes(request.id) 
        ? state.allIds 
        : [...state.allIds, request.id];
      
      return { byId: newById, allIds: newAllIds };
    });
  },

  remove: (id) => {
    set(state => {
      const newById = { ...state.byId };
      delete newById[id];
      
      const newAllIds = state.allIds.filter(existingId => existingId !== id);
      
      return { byId: newById, allIds: newAllIds };
    });
    
    // Unsubscribe from streaming
    get().unsubscribeFrom(id.toString());
  },

  computeCounts: () => {
    const state = get();
    const requests = Object.values(state.byId);
    
    const counts: RequestCounts = {
      total: requests.length,
      queued: requests.filter(r => r.status === 'Queued').length,
      processing: requests.filter(r => r.status === 'Processing').length,
      draft_ready: requests.filter(r => r.status === 'Ready for Review' && r.progress < 100).length,
      approved: requests.filter(r => r.status === 'Ready for Review' && r.progress === 100).length,
      failed: requests.filter(r => r.tags?.some(tag => tag.text === 'Failed')).length,
    };
    
    set({ counts });
  },

  setSelectedRequest: (id) => {
    set({ selectedRequestId: id });
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    // Unsubscribe from all streams
    get().unsubscribeAll();
    
    // Reset state
    set(initialState);
  },
}), {
  name: 'ai-request-store',
}));

// Selectors
export const selectAllRequests = (state: AIRequestState) => 
  state.allIds.map(id => state.byId[id]);

export const selectRequestById = (id: number) => (state: AIRequestState) => 
  state.byId[id];

export const selectRequestsByStatus = (status: Request['status']) => (state: AIRequestState) =>
  state.allIds.map(id => state.byId[id]).filter(request => request.status === status);

export const selectProcessingRequests = (state: AIRequestState) =>
  state.allIds.map(id => state.byId[id]).filter(request => request.status === 'Processing');

export const selectCounts = (state: AIRequestState) => state.counts;

export const selectLoading = (state: AIRequestState) => state.loading;

export const selectError = (state: AIRequestState) => state.error;

export const selectSelectedRequest = (state: AIRequestState) => 
  state.selectedRequestId ? state.byId[state.selectedRequestId] : null;

export const selectIsStreaming = (id: string) => (state: AIRequestState) => 
  Boolean(state.streaming[id]);

// Window unload cleanup
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    useAIRequestStore.getState().unsubscribeAll();
  });
}