import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { isTaskStale, isRecoverableStatus, getTimeoutErrorMessage } from '../config/taskLifecycle';
import { 
  GeneratedContent, 
  ContentType as SchemaContentType,
  ContentStoreState,
  ExportStatusResponse,
  CONTENT_SCHEMA_VERSION,
  migrateContent,
  validateContentStructure
} from '../types/contentSchemas';

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

// CMA Report Data Structure
export interface CMAData {
  property: {
    address: string;
    sqft?: number;
    bedrooms?: number;
    bathrooms?: number;
    yearBuilt?: number;
    lotSize?: string;
    type?: string;
  };
  marketAnalysis: {
    avgPrice: number;
    medianPrice: number;
    pricePerSqft: number;
    marketTrend: 'up' | 'down' | 'stable';
    daysOnMarket: number;
    inventory: number;
  };
  comparables: Array<{
    address: string;
    price: number;
    sqft: number;
    bedrooms: number;
    bathrooms: number;
    soldDate: string;
    distance: number;
    pricePerSqft: number;
    adjustedPrice?: number;
    adjustments?: Record<string, number>;
  }>;
  valuation: {
    estimatedValue: number;
    confidenceRange: { min: number; max: number };
    methodology: string[];
  };
  insights: string[];
  disclaimers: string[];
  generatedAt: string;
  reportId: string;
}

// Pitch Deck Data Structure
export interface PitchDeckData {
  id: string;
  title: string;
  property: {
    address: string;
    type: 'residential' | 'commercial' | 'mixed';
    sqft?: number;
    lotSize?: string;
    yearBuilt?: number;
  };
  slides: Array<{
    id: string;
    type: 'title' | 'property-overview' | 'market-analysis' | 'financial-projections' | 'investment-highlights' | 'neighborhood' | 'conclusion' | 'custom';
    title: string;
    content: {
      text?: string;
      bullets?: string[];
      data?: Record<string, any>;
      charts?: Array<{
        type: 'bar' | 'line' | 'pie' | 'area';
        title: string;
        data: any[];
      }>;
      images?: Array<{
        url: string;
        alt: string;
        caption?: string;
      }>;
    };
    notes?: string;
  }>;
  theme: {
    primaryColor: string;
    accentColor: string;
    fontFamily: string;
  };
  generatedAt: string;
}

// Legacy Generated Content Storage (kept for backward compatibility)
export interface LegacyGeneratedContent {
  id: string;
  taskId: string;
  type: ContentType;
  title: string;
  data: CMAData | PitchDeckData | Record<string, any>;
  generatedAt: string;
  updatedAt?: string;
}

export interface Request {
  id: string;
  title: string;
  status: RequestStatus;
  type: RequestType;
  timestamp: number;
  error?: string;
  metadata?: RequestMetadata;
  parentId?: string;
  relatedTasks?: string[];
  // Progress tracking (Track 4)
  progress?: number;
  currentStep?: string;
  logs?: string[];
  enrichmentSources?: Record<string, string>;
}

// Unified Session Management v3.0
export interface UnifiedSession {
  id: string;
  mode: Mode;
  phase: Phase;
  startedAt: number;
  resumedAt?: number;
  lastActiveAt: number;
  
  // Recording state
  isRecording: boolean;
  recordingStartTime?: number;
  recordingPaused: boolean;
  audioBlob?: Blob;
  
  // Processing state
  isProcessing: boolean;
  currentTaskId?: string;
  processingStartTime?: number;
  
  // Streaming state
  isStreaming: boolean;
  streamingText?: string;
  streamStartTime?: number;
  
  // Context and continuity
  lastPrompt: string | null;
  contextHistory: string[];
  resumePending: boolean;
  connected: boolean;
  
  // Multi-device awareness
  deviceId: string;
  tabId: string;
  isActive: boolean;
  lastHeartbeat: number;
  
  // Background operation flags
  canResume: boolean;
  backgroundTasks: string[];
  queuedOperations: QueuedOperation[];
}

export interface QueuedOperation {
  id: string;
  type: 'transcribe' | 'orchestrate' | 'stream';
  data: any;
  timestamp: number;
  retryCount: number;
}

// Legacy support - will be phased out
export interface SessionState {
  isRecording: boolean;
  isProcessing: boolean;
  isStreaming: boolean;
  lastPrompt: string | null;
  currentTaskId?: string;
  resumePending?: boolean;
  streamingText?: string;
  recordingStartTime?: number;
}

interface CommandStore {
  // UI State
  isOpen: boolean;
  isCollapsed: boolean;
  mode: Mode;
  phase: Phase;
  
  // Data
  history: CommandHistoryItem[];
  responses: string[];
  requests: Request[];
  generatedContent: Record<string, LegacyGeneratedContent>;
  
  // Content Store v3.2
  contentStore: ContentStoreState;
  exportStatus: Record<string, ExportStatusResponse>;
  
  // Intelligence Content v3.3
  intelContent: Record<string, IntelligenceContent>;
  
  // Unified Session v3.0
  session: UnifiedSession;
  
  // UI Actions
  open: () => void;
  close: () => void;
  collapse: () => void;
  expand: () => void;
  
  // Mode and Phase
  setMode: (mode: Mode) => void;
  setPhase: (phase: Phase) => void;
  togglePause: () => void;
  
  // Data Management
  addHistory: (text: string, mode?: Mode) => void;
  addResponse: (response: string) => void;
  addRequest: (title: string, type?: RequestType, metadata?: Record<string, any>, parentId?: string) => string;
  updateRequestStatus: (id: string, status: RequestStatus, error?: string) => void;
  syncTasks: (tasks: any[]) => void;
  linkTasks: (parentId: string, childId: string) => void;
  
  // Progress tracking (Track 4)
  updateRequestProgress: (requestId: string, progress: number, step: string) => void;
  addRequestLogs: (requestId: string, logs: string[]) => void;
  
  // Task Lifecycle v2.9.5
  checkStaleTasks: () => { updated: number; staleTaskIds: string[] };
  retryTask: (taskId: string) => Promise<void>;
  clearStuckTasks: () => void;
  
  // Unified Session Management v3.0
  createSession: (mode?: Mode) => void;
  resumeSession: () => void;
  pauseSession: () => void;
  endSession: () => void;
  saveSession: () => void;
  loadSession: () => boolean;
  heartbeat: () => void;
  
  // Recording Management
  startRecording: () => void;
  stopRecording: () => void;
  pauseRecording: () => void;
  resumeRecording: () => void;
  storeAudioBlob: (blob: Blob) => void;
  
  // Background Operations
  queueOperation: (op: Omit<QueuedOperation, 'id' | 'timestamp'>) => void;
  processQueue: () => Promise<void>;
  clearQueue: () => void;
  
  // Cross-tab Coordination
  acquireMicLock: () => boolean;
  releaseMicLock: () => void;
  broadcastSessionUpdate: () => void;
  handleSessionTakeover: (sessionData: UnifiedSession) => void;
  
  // Context Management
  addContext: (text: string) => void;
  getRecentContext: () => string[];
  clearOldContext: () => void;
  
  // Generated Content Management (Legacy)
  saveGeneratedContent: (content: Omit<LegacyGeneratedContent, 'id' | 'generatedAt'>) => string;
  getGeneratedContent: (taskId: string) => LegacyGeneratedContent | undefined;
  removeGeneratedContent: (taskId: string) => void;
  updateGeneratedContent: (taskId: string, updates: Partial<LegacyGeneratedContent>) => void;
  listContentByType: (type: ContentType) => LegacyGeneratedContent[];
  
  // Content Store v3.2
  saveContent: (content: GeneratedContent) => void;
  getContent: (taskId: string) => GeneratedContent | undefined;
  removeContent: (taskId: string) => void;
  updateContent: (taskId: string, updates: Partial<GeneratedContent>) => void;
  listContent: () => GeneratedContent[];
  listContentByContentType: (type: SchemaContentType) => GeneratedContent[];
  hydrateFromStorage: () => void;
  persistToStorage: () => void;
  
  // Intelligence Content v3.3
  saveIntelligenceContent: (content: IntelligenceContent) => void;
  getIntelligenceContent: (contentId: string) => IntelligenceContent | undefined;
  getIntelligenceContentByTaskId: (taskId: string) => IntelligenceContent | undefined;
  removeIntelligenceContent: (contentId: string) => void;
  updateIntelligenceContent: (contentId: string, updates: Partial<IntelligenceContent>) => void;
  listIntelligenceContent: () => IntelligenceContent[];
  persistIntelligenceContent: () => void;
  
  // Export Status Management
  markExported: (taskId: string, format: 'pdf' | 'html', exportedAt?: string) => void;
  getExportStatus: (taskId: string) => ExportStatusResponse | undefined;
  clearExportStatus: (taskId: string) => void;
  
  // Intelligence Content Export
  markIntelligenceContentReady: (contentId: string) => void;
  
  // Legacy Support (will be deprecated)
  sessionState: SessionState;
  setRecording: (recording: boolean) => void;
  setProcessing: (processing: boolean) => void;
  setStreaming: (streaming: boolean, text?: string) => void;
  cacheSession: () => void;
  restoreSession: () => void;
  clearSession: () => void;
  updateSession: (updates: Partial<SessionState>) => void;
  reset: () => void;
}

// Utility functions for session management
const generateSessionId = () => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
const generateDeviceId = () => {
  const stored = localStorage.getItem('aura_device_id');
  if (stored) return stored;
  const deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  localStorage.setItem('aura_device_id', deviceId);
  return deviceId;
};
const generateTabId = () => `tab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

// BroadcastChannel for cross-tab communication
const sessionChannel = typeof window !== 'undefined' ? new BroadcastChannel('aura_session') : null;

export const useCommandStore = create<CommandStore>()(persist(
  (set, get) => ({
    // UI State
    isOpen: false,
    isCollapsed: false,
    mode: 'voice',
    phase: 'idle',
    
    // Data
    history: [],
    responses: [],
    requests: [],
    generatedContent: (() => {
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
      try {
        const saved = localStorage.getItem('aura.intelContent.v1');
        return saved ? JSON.parse(saved) : {};
      } catch (error) {
        console.warn('[IntelContent] Failed to load persisted intelligence content:', error);
        return {};
      }
    })(),
    
    // Content Store v3.2
    contentStore: (() => {
      try {
        const saved = localStorage.getItem('aura.content.v1');
        if (!saved) {
          return {
            version: CONTENT_SCHEMA_VERSION,
            content: {},
            exportStatus: {},
          };
        }
        
        const parsed = JSON.parse(saved);
        
        // Migrate content if needed
        const migratedContent: Record<string, GeneratedContent> = {};
        for (const [taskId, content] of Object.entries(parsed.content || {})) {
          try {
            if (validateContentStructure(content)) {
              migratedContent[taskId] = migrateContent(content);
            } else {
              console.warn('[Content] Invalid content structure for task:', taskId);
            }
          } catch (error) {
            console.warn('[Content] Failed to migrate content for task:', taskId, error);
          }
        }
        
        return {
          version: CONTENT_SCHEMA_VERSION,
          content: migratedContent,
          exportStatus: parsed.exportStatus || {},
          lastSync: parsed.lastSync,
        };
      } catch (error) {
        console.warn('[Content] Failed to load content store, initializing fresh:', error);
        return {
          version: CONTENT_SCHEMA_VERSION,
          content: {},
          exportStatus: {},
        };
      }
    })(),
    
    exportStatus: {},
    
    // Unified Session v3.0
    session: {
      id: generateSessionId(),
      mode: 'voice',
      phase: 'idle',
      startedAt: Date.now(),
      lastActiveAt: Date.now(),
      
      // Recording state
      isRecording: false,
      recordingPaused: false,
      
      // Processing state
      isProcessing: false,
      
      // Streaming state
      isStreaming: false,
      
      // Context
      lastPrompt: null,
      contextHistory: [],
      resumePending: false,
      connected: typeof navigator !== 'undefined' ? navigator.onLine : true,
      
      // Multi-device
      deviceId: generateDeviceId(),
      tabId: generateTabId(),
      isActive: true,
      lastHeartbeat: Date.now(),
      
      // Background operations
      canResume: false,
      backgroundTasks: [],
      queuedOperations: []
    },
    
    // Legacy session state for backward compatibility
    sessionState: {
      isRecording: false,
      isProcessing: false,
      isStreaming: false,
      lastPrompt: null,
      currentTaskId: undefined,
      resumePending: false,
      streamingText: undefined,
      recordingStartTime: undefined
    },
  
  // UI Actions v3.0
  open: () => set((state) => ({ 
    isOpen: true, 
    isCollapsed: false,
    session: { ...state.session, lastActiveAt: Date.now() }
  })),
  
  close: () => set((state) => {
    // End session when closing
    const actions = get();
    actions.endSession();
    return { isOpen: false, isCollapsed: false };
  }),
  
  collapse: () => set((state) => {
    // Pause recording when collapsing, keep other operations running
    const updatedSession = { ...state.session };
    if (state.session.isRecording && !state.session.recordingPaused) {
      updatedSession.recordingPaused = true;
      console.log('[Session] Recording paused due to collapse');
    }
    
    return { 
      isCollapsed: true,
      session: { ...updatedSession, lastActiveAt: Date.now() }
    };
  }),
  
  expand: () => set((state) => {
    // Resume recording if it was paused
    const updatedSession = { ...state.session };
    if (state.session.isRecording && state.session.recordingPaused) {
      updatedSession.recordingPaused = false;
      updatedSession.resumedAt = Date.now();
      console.log('[Session] Recording resumed after expand');
    }
    
    return { 
      isCollapsed: false,
      session: { ...updatedSession, lastActiveAt: Date.now() }
    };
  }),
  
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
  
  addRequest: (title: string, type: RequestType = 'GENERIC', metadata?: Record<string, any>, parentId?: string) => {
    const id = crypto.randomUUID();
    set((state) => ({
      requests: [
        { 
          id, 
          title, 
          status: 'Pending' as RequestStatus, 
          type, 
          timestamp: Date.now(), 
          metadata,
          parentId,
          relatedTasks: []
        },
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
  
  syncTasks: (tasks) => set((state) => {
    // Convert backend tasks to our Request format
    const syncedRequests = tasks.map((task) => {
      // Check if we already have this task locally
      const existing = state.requests.find(req => req.id === task.id);
      
      return {
        id: task.id,
        title: task.title || task.command || 'Untitled Task',
        status: (task.status || 'Processing') as RequestStatus,
        type: (task.type || 'GENERIC') as RequestType,
        timestamp: existing?.timestamp || new Date(task.created_at || Date.now()).getTime(),
        metadata: task.metadata || existing?.metadata,
        error: existing?.error,
      };
    });
    
    // Merge with existing requests, prioritizing synced data for status updates
    const mergedRequests = [...syncedRequests];
    
    // Add any local-only requests that weren't in the sync response
    state.requests.forEach(localReq => {
      if (!syncedRequests.find(syncReq => syncReq.id === localReq.id)) {
        mergedRequests.push({
          ...localReq,
          metadata: localReq.metadata || {},
          error: localReq.error || undefined
        });
      }
    });
    
    // Sort by timestamp (most recent first) and limit to 20 items
    const sortedRequests = mergedRequests
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, 20);
    
    return { requests: sortedRequests };
  }),
  
  linkTasks: (parentId: string, childId: string) => set((state) => ({
    requests: state.requests.map((req) => {
      if (req.id === parentId) {
        // Add child to parent's relatedTasks
        return {
          ...req,
          relatedTasks: [...(req.relatedTasks || []), childId]
        };
      } else if (req.id === childId) {
        // Set parent reference on child
        return {
          ...req,
          parentId
        };
      }
      return req;
    })
  })),
  
  // Progress tracking (Track 4)
  updateRequestProgress: (requestId: string, progress: number, step: string) => set((state) => ({
    requests: state.requests.map((req) =>
      req.id === requestId
        ? { ...req, progress, currentStep: step }
        : req
    ),
  })),

  addRequestLogs: (requestId: string, logs: string[]) => set((state) => ({
    requests: state.requests.map((req) =>
      req.id === requestId
        ? { ...req, logs: [...(req.logs || []), ...logs] }
        : req
    ),
  })),

  // Task Lifecycle Management Functions
  checkStaleTasks: () => {
    let updatedCount = 0;
    const staleTaskIds: string[] = [];
    
    set((state) => {
      const now = Date.now();
      const updatedRequests = state.requests.map((task) => {
        if (isRecoverableStatus(task.status) && isTaskStale(task.timestamp, task.status)) {
          console.warn(`[TaskLifecycle] Auto-resolving stale task: ${task.title} (${task.status} for ${Math.round((now - task.timestamp) / 60000)} min)`);
          updatedCount++;
          staleTaskIds.push(task.id);
          return {
            ...task,
            status: 'Error' as RequestStatus,
            error: getTimeoutErrorMessage(task.status)
          };
        }
        return task;
      });
      
      return { requests: updatedRequests };
    });
    
    return { updated: updatedCount, staleTaskIds };
  },

  retryTask: async (taskId: string) => {
    const task = get().requests.find(r => r.id === taskId);
    if (!task) {
      console.error('[TaskLifecycle] Task not found for retry:', taskId);
      return;
    }

    console.log(`[TaskLifecycle] Retrying task: ${task.title}`);
    
    // Reset task status to Pending
    get().updateRequestStatus(taskId, 'Pending');
    
    try {
      // Import orchestrator dynamically to avoid circular dependencies
      const { orchestrateCommand } = await import('../services/orchestrator');
      await orchestrateCommand(task.title, task.parentId);
    } catch (error) {
      console.error('[TaskLifecycle] Retry failed:', error);
      get().updateRequestStatus(taskId, 'Error', 'Retry attempt failed');
    }
  },

  clearStuckTasks: () => set((state) => ({
    requests: state.requests.filter(task => 
      !(isRecoverableStatus(task.status) && isTaskStale(task.timestamp, task.status))
    )
  })),

  // Unified Session Management v3.0
  createSession: (mode = 'voice') => set((state) => {
    const newSession: UnifiedSession = {
      id: generateSessionId(),
      mode,
      phase: 'idle',
      startedAt: Date.now(),
      lastActiveAt: Date.now(),
      
      // Recording state
      isRecording: false,
      recordingPaused: false,
      
      // Processing state
      isProcessing: false,
      
      // Streaming state
      isStreaming: false,
      
      // Context
      lastPrompt: null,
      contextHistory: [...state.session.contextHistory], // Preserve context
      resumePending: false,
      connected: typeof navigator !== 'undefined' ? navigator.onLine : true,
      
      // Multi-device
      deviceId: state.session.deviceId, // Keep same device
      tabId: generateTabId(), // New tab ID
      isActive: true,
      lastHeartbeat: Date.now(),
      
      // Background operations
      canResume: false,
      backgroundTasks: [],
      queuedOperations: []
    };
    
    console.log('[Session] Created new session:', newSession.id);
    return { 
      session: newSession,
      mode,
      phase: 'idle'
    };
  }),

  resumeSession: () => set((state) => {
    if (!state.session.canResume) {
      console.warn('[Session] Cannot resume - session not resumable');
      return state;
    }
    
    const resumedSession = {
      ...state.session,
      resumedAt: Date.now(),
      lastActiveAt: Date.now(),
      resumePending: false,
      isActive: true
    };
    
    console.log('[Session] Resumed session:', resumedSession.id);
    return { session: resumedSession };
  }),

  pauseSession: () => set((state) => {
    const pausedSession = {
      ...state.session,
      lastActiveAt: Date.now(),
      recordingPaused: state.session.isRecording ? true : state.session.recordingPaused,
      canResume: true
    };
    
    console.log('[Session] Paused session:', pausedSession.id);
    return { session: pausedSession };
  }),

  endSession: () => set((state) => {
    // Process any queued operations before ending
    const actions = get();
    if (state.session.queuedOperations.length > 0) {
      console.log('[Session] Processing queued operations before ending session');
      actions.processQueue();
    }
    
    // Release mic lock
    actions.releaseMicLock();
    
    const endedSession = {
      ...state.session,
      lastActiveAt: Date.now(),
      isActive: false,
      isRecording: false,
      recordingPaused: false,
      isProcessing: false,
      isStreaming: false,
      canResume: false
    };
    
    console.log('[Session] Ended session:', endedSession.id);
    return { 
      session: endedSession,
      phase: 'idle' as Phase
    };
  }),

  saveSession: () => {
    const state = get();
    const sessionData = {
      ...state.session,
      timestamp: Date.now()
    };
    
    try {
      localStorage.setItem('aura_unified_session', JSON.stringify(sessionData));
      localStorage.setItem('aura_session_requests', JSON.stringify(state.requests));
      console.log('[Session] Saved to localStorage:', sessionData.id);
      
      // Also send heartbeat to backend if connected
      if (state.session.connected) {
        get().heartbeat();
      }
    } catch (error) {
      console.warn('[Session] Failed to save session:', error);
    }
  },

  loadSession: () => {
    try {
      const sessionData = localStorage.getItem('aura_unified_session');
      const requestsData = localStorage.getItem('aura_session_requests');
      
      if (!sessionData) {
        console.log('[Session] No saved session found');
        return false;
      }
      
      const session = JSON.parse(sessionData);
      const age = Date.now() - (session.timestamp || 0);
      
      // Only restore if session is less than 2 hours old
      if (age > 2 * 60 * 60 * 1000) {
        console.log('[Session] Saved session too old, creating new');
        localStorage.removeItem('aura_unified_session');
        localStorage.removeItem('aura_session_requests');
        return false;
      }
      
      // Restore session
      const restoredSession = {
        ...session,
        tabId: generateTabId(), // New tab ID
        lastActiveAt: Date.now(),
        lastHeartbeat: Date.now(),
        resumePending: session.isRecording || session.isProcessing || session.isStreaming,
        canResume: true
      };
      
      const requests = requestsData ? JSON.parse(requestsData) : [];
      
      set({ 
        session: restoredSession,
        requests,
        mode: restoredSession.mode,
        phase: restoredSession.phase
      });
      
      console.log('[Session] Restored session:', restoredSession.id);
      return true;
    } catch (error) {
      console.warn('[Session] Failed to load session:', error);
      return false;
    }
  },

  heartbeat: () => {
    const state = get();
    const heartbeatData = {
      sessionId: state.session.id,
      deviceId: state.session.deviceId,
      tabId: state.session.tabId,
      timestamp: Date.now(),
      isActive: state.session.isActive,
      phase: state.session.phase,
      backgroundTasks: state.session.backgroundTasks
    };
    
    // Update local heartbeat
    set((state) => ({
      session: { ...state.session, lastHeartbeat: Date.now() }
    }));
    
    // Send to backend (implementation would depend on API)
    // fetch('/api/v1/command-center/session/heartbeat', {
    //   method: 'POST',
    //   body: JSON.stringify(heartbeatData)
    // }).catch(err => console.warn('[Session] Heartbeat failed:', err));
  },

  // Recording Management v3.0
  startRecording: () => set((state) => {
    // Check mic lock first
    const actions = get();
    if (!actions.acquireMicLock()) {
      console.warn('[Recording] Cannot start - mic locked by another tab');
      return state;
    }
    
    const updatedSession = {
      ...state.session,
      isRecording: true,
      recordingStartTime: Date.now(),
      recordingPaused: false,
      phase: 'listening' as Phase,
      lastActiveAt: Date.now()
    };
    
    console.log('[Recording] Started recording in session:', updatedSession.id);
    actions.broadcastSessionUpdate();
    
    return { 
      session: updatedSession,
      phase: 'listening' as Phase
    };
  }),

  stopRecording: () => set((state) => {
    const updatedSession = {
      ...state.session,
      isRecording: false,
      recordingPaused: false,
      phase: 'stopped' as Phase,
      lastActiveAt: Date.now()
    };
    
    console.log('[Recording] Stopped recording in session:', updatedSession.id);
    get().broadcastSessionUpdate();
    
    return { 
      session: updatedSession,
      phase: 'stopped' as Phase
    };
  }),

  pauseRecording: () => set((state) => {
    const updatedSession = {
      ...state.session,
      recordingPaused: true,
      phase: 'paused' as Phase,
      lastActiveAt: Date.now()
    };
    
    console.log('[Recording] Paused recording in session:', updatedSession.id);
    get().broadcastSessionUpdate();
    
    return { 
      session: updatedSession,
      phase: 'paused' as Phase
    };
  }),

  resumeRecording: () => set((state) => {
    const updatedSession = {
      ...state.session,
      recordingPaused: false,
      phase: 'listening' as Phase,
      resumedAt: Date.now(),
      lastActiveAt: Date.now()
    };
    
    console.log('[Recording] Resumed recording in session:', updatedSession.id);
    get().broadcastSessionUpdate();
    
    return { 
      session: updatedSession,
      phase: 'listening' as Phase
    };
  }),

  storeAudioBlob: (blob: Blob) => set((state) => {
    const updatedSession = {
      ...state.session,
      audioBlob: blob,
      lastActiveAt: Date.now()
    };
    
    console.log('[Recording] Stored audio blob, size:', blob.size);
    return { session: updatedSession };
  }),

  // Background Operations v3.0
  queueOperation: (op) => set((state) => {
    const operation: QueuedOperation = {
      id: `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ...op,
      timestamp: Date.now(),
      retryCount: 0
    };
    
    const updatedSession = {
      ...state.session,
      queuedOperations: [...state.session.queuedOperations, operation]
    };
    
    console.log('[Queue] Added operation:', operation.type, operation.id);
    return { session: updatedSession };
  }),

  processQueue: async () => {
    const state = get();
    const operations = [...state.session.queuedOperations];
    
    if (operations.length === 0) {
      console.log('[Queue] No operations to process');
      return;
    }
    
    console.log(`[Queue] Processing ${operations.length} operations`);
    
    for (const op of operations) {
      try {
        console.log('[Queue] Processing operation:', op.type, op.id);
        
        // Process based on operation type
        switch (op.type) {
          case 'transcribe':
            // Handle transcription
            break;
          case 'orchestrate':
            // Handle orchestration
            break;
          case 'stream':
            // Handle streaming
            break;
        }
        
        // Remove completed operation
        set((state) => ({
          session: {
            ...state.session,
            queuedOperations: state.session.queuedOperations.filter(qop => qop.id !== op.id)
          }
        }));
        
      } catch (error) {
        console.error('[Queue] Operation failed:', op.id, error);
        
        // Retry logic
        if (op.retryCount < 3) {
          set((state) => ({
            session: {
              ...state.session,
              queuedOperations: state.session.queuedOperations.map(qop => 
                qop.id === op.id ? { ...qop, retryCount: qop.retryCount + 1 } : qop
              )
            }
          }));
        } else {
          // Remove failed operation after max retries
          set((state) => ({
            session: {
              ...state.session,
              queuedOperations: state.session.queuedOperations.filter(qop => qop.id !== op.id)
            }
          }));
        }
      }
    }
  },

  clearQueue: () => set((state) => ({
    session: { ...state.session, queuedOperations: [] }
  })),

  // Cross-tab Coordination v3.0
  acquireMicLock: () => {
    try {
      const lockKey = 'aura_mic_lock';
      const lockData = {
        tabId: get().session.tabId,
        deviceId: get().session.deviceId,
        timestamp: Date.now()
      };
      
      const existingLock = localStorage.getItem(lockKey);
      if (existingLock) {
        const lock = JSON.parse(existingLock);
        const age = Date.now() - lock.timestamp;
        
        // Lock expires after 30 seconds of inactivity
        if (age < 30000 && lock.tabId !== get().session.tabId) {
          console.warn('[MicLock] Mic already locked by another tab');
          return false;
        }
      }
      
      localStorage.setItem(lockKey, JSON.stringify(lockData));
      console.log('[MicLock] Acquired mic lock for tab:', lockData.tabId);
      
      // Broadcast lock acquisition
      sessionChannel?.postMessage({
        type: 'MIC_LOCK_ACQUIRED',
        tabId: lockData.tabId,
        deviceId: lockData.deviceId,
        timestamp: Date.now()
      });
      
      return true;
    } catch (error) {
      console.error('[MicLock] Failed to acquire mic lock:', error);
      return false;
    }
  },

  releaseMicLock: () => {
    try {
      const lockKey = 'aura_mic_lock';
      const existingLock = localStorage.getItem(lockKey);
      
      if (existingLock) {
        const lock = JSON.parse(existingLock);
        if (lock.tabId === get().session.tabId) {
          localStorage.removeItem(lockKey);
          console.log('[MicLock] Released mic lock for tab:', lock.tabId);
          
          // Broadcast lock release
          sessionChannel?.postMessage({
            type: 'MIC_LOCK_RELEASED',
            tabId: lock.tabId,
            timestamp: Date.now()
          });
        }
      }
    } catch (error) {
      console.error('[MicLock] Failed to release mic lock:', error);
    }
  },

  broadcastSessionUpdate: () => {
    const state = get();
    sessionChannel?.postMessage({
      type: 'SESSION_UPDATE',
      session: state.session,
      timestamp: Date.now()
    });
  },

  handleSessionTakeover: (sessionData) => {
    console.log('[Session] Handling session takeover from another tab');
    
    // If the incoming session is more recent and active, take it over
    const currentSession = get().session;
    if (sessionData.lastActiveAt > currentSession.lastActiveAt && sessionData.isActive) {
      set((state) => ({
        session: {
          ...sessionData,
          tabId: state.session.tabId, // Keep current tab ID
          lastActiveAt: Date.now()
        },
        mode: sessionData.mode,
        phase: sessionData.phase
      }));
      
      console.log('[Session] Took over session:', sessionData.id);
    }
  },

  // Context Management v3.0
  addContext: (text: string) => set((state) => {
    const maxContextItems = 3;
    const updatedHistory = [text, ...state.session.contextHistory].slice(0, maxContextItems);
    
    const updatedSession = {
      ...state.session,
      contextHistory: updatedHistory,
      lastActiveAt: Date.now()
    };
    
    console.log('[Context] Added context item:', text.substring(0, 50) + '...');
    return { session: updatedSession };
  }),

  getRecentContext: () => {
    return get().session.contextHistory;
  },

  clearOldContext: () => set((state) => {
    const maxAge = 60 * 60 * 1000; // 1 hour
    const now = Date.now();
    
    // In a real implementation, we'd have timestamps for each context item
    // For now, just keep the most recent 3 items
    const updatedSession = {
      ...state.session,
      contextHistory: state.session.contextHistory.slice(0, 3)
    };
    
    console.log('[Context] Cleared old context items');
    return { session: updatedSession };
  }),

  // Generated Content Management (Legacy - kept for backward compatibility)
  saveGeneratedContent: (content: Omit<LegacyGeneratedContent, 'id' | 'generatedAt'>) => {
    const id = crypto.randomUUID();
    const generatedContent: LegacyGeneratedContent = {
      ...content,
      id,
      generatedAt: new Date().toISOString()
    };
    
    set((state) => {
      const updatedContent = {
        ...state.generatedContent,
        [content.taskId]: generatedContent
      };
      
      console.log('[Content:Legacy] Saved generated content for task:', content.taskId, content.type);
      return { generatedContent: updatedContent };
    });
    
    // Persist to localStorage
    try {
      const state = get();
      localStorage.setItem('aura_generated_content', JSON.stringify(state.generatedContent));
    } catch (error) {
      console.warn('[Content:Legacy] Failed to persist generated content:', error);
    }
    
    return id;
  },
  
  getGeneratedContent: (taskId: string) => {
    const state = get();
    return state.generatedContent[taskId];
  },
  
  removeGeneratedContent: (taskId: string) => {
    set((state) => {
      const updatedContent = { ...state.generatedContent };
      delete updatedContent[taskId];
      
      console.log('[Content:Legacy] Removed generated content for task:', taskId);
      return { generatedContent: updatedContent };
    });
    
    // Update localStorage
    try {
      const state = get();
      localStorage.setItem('aura_generated_content', JSON.stringify(state.generatedContent));
    } catch (error) {
      console.warn('[Content:Legacy] Failed to persist content removal:', error);
    }
  },
  
  updateGeneratedContent: (taskId: string, updates: Partial<LegacyGeneratedContent>) => {
    set((state) => {
      const existing = state.generatedContent[taskId];
      if (!existing) {
        console.warn('[Content:Legacy] Cannot update non-existent content for task:', taskId);
        return state;
      }
      
      const updatedContent = {
        ...state.generatedContent,
        [taskId]: {
          ...existing,
          ...updates,
          updatedAt: new Date().toISOString()
        }
      };
      
      console.log('[Content:Legacy] Updated generated content for task:', taskId);
      return { generatedContent: updatedContent };
    });
    
    // Persist to localStorage
    try {
      const state = get();
      localStorage.setItem('aura_generated_content', JSON.stringify(state.generatedContent));
    } catch (error) {
      console.warn('[Content:Legacy] Failed to persist content update:', error);
    }
  },
  
  listContentByType: (type: ContentType) => {
    const state = get();
    return Object.values(state.generatedContent)
      .filter(content => content.type === type)
      .sort((a, b) => new Date(b.generatedAt).getTime() - new Date(a.generatedAt).getTime());
  },
  
  // Content Store v3.2 - New Schema Implementation
  saveContent: (content: GeneratedContent) => {
    set((state) => {
      const updatedContentStore: ContentStoreState = {
        ...state.contentStore,
        content: {
          ...state.contentStore.content,
          [content.taskId]: {
            ...content,
            updatedAt: new Date().toISOString(),
            version: CONTENT_SCHEMA_VERSION,
          },
        },
      };
      
      console.log('[ContentStore] Saved content for task:', content.taskId, content.type);
      return { contentStore: updatedContentStore };
    });
    
    // Debounced persist
    get().persistToStorage();
  },
  
  getContent: (taskId: string) => {
    const state = get();
    return state.contentStore.content[taskId];
  },
  
  removeContent: (taskId: string) => {
    set((state) => {
      const updatedContent = { ...state.contentStore.content };
      delete updatedContent[taskId];
      
      console.log('[ContentStore] Removed content for task:', taskId);
      return {
        contentStore: {
          ...state.contentStore,
          content: updatedContent,
        },
      };
    });
    
    // Also remove export status
    get().clearExportStatus(taskId);
    get().persistToStorage();
  },
  
  updateContent: (taskId: string, updates: Partial<GeneratedContent>) => {
    set((state) => {
      const existing = state.contentStore.content[taskId];
      if (!existing) {
        console.warn('[ContentStore] Cannot update non-existent content for task:', taskId);
        return state;
      }
      
      const updatedContentStore: ContentStoreState = {
        ...state.contentStore,
        content: {
          ...state.contentStore.content,
          [taskId]: {
            ...existing,
            ...updates,
            updatedAt: new Date().toISOString(),
          },
        },
      };
      
      console.log('[ContentStore] Updated content for task:', taskId);
      return { contentStore: updatedContentStore };
    });
    
    get().persistToStorage();
  },
  
  listContent: () => {
    const state = get();
    return Object.values(state.contentStore.content)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  },
  
  listContentByContentType: (type: SchemaContentType) => {
    const state = get();
    return Object.values(state.contentStore.content)
      .filter(content => content.type === type)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  },
  
  hydrateFromStorage: () => {
    try {
      const saved = localStorage.getItem('aura.content.v1');
      if (!saved) {
        console.log('[ContentStore] No persisted content found');
        return;
      }
      
      const parsed = JSON.parse(saved);
      
      // Validate and migrate content
      const migratedContent: Record<string, GeneratedContent> = {};
      for (const [taskId, content] of Object.entries(parsed.content || {})) {
        try {
          if (validateContentStructure(content)) {
            migratedContent[taskId] = migrateContent(content);
          } else {
            console.warn('[ContentStore] Invalid content structure for task:', taskId);
          }
        } catch (error) {
          console.warn('[ContentStore] Failed to migrate content for task:', taskId, error);
        }
      }
      
      set((state) => ({
        contentStore: {
          version: CONTENT_SCHEMA_VERSION,
          content: migratedContent,
          exportStatus: parsed.exportStatus || {},
          lastSync: parsed.lastSync,
        },
      }));
      
      console.log('[ContentStore] Hydrated', Object.keys(migratedContent).length, 'content items from storage');
    } catch (error) {
      console.error('[ContentStore] Failed to hydrate from storage:', error);
    }
  },
  
  persistToStorage: (() => {
    let timeoutId: NodeJS.Timeout | null = null;
    
    return () => {
      // Debounce: wait 500ms before persisting
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      timeoutId = setTimeout(() => {
        try {
          const state = get();
          const serialized = JSON.stringify(state.contentStore);
          localStorage.setItem('aura.content.v1', serialized);
          
          // Also persist intelligence content while we're at it
          const intelSerialized = JSON.stringify(state.intelContent);
          localStorage.setItem('aura.intelContent.v1', intelSerialized);
          console.log('[ContentStore] Persisted', Object.keys(state.contentStore.content).length, 'content items');
        } catch (error) {
          console.error('[ContentStore] Failed to persist to storage:', error);
        }
      }, 500);
    };
  })(),
  
  // Export Status Management
  markExported: (taskId: string, format: 'pdf' | 'html', exportedAt?: string) => {
    set((state) => {
      const existing = state.contentStore.exportStatus[taskId] || {
        task_id: taskId,
        exported: false,
        export_count: 0,
        formats_available: [],
      };
      
      const updatedExportStatus: ExportStatusResponse = {
        ...existing,
        exported: true,
        export_count: existing.export_count + 1,
        last_export: exportedAt || new Date().toISOString(),
        formats_available: Array.from(new Set([...existing.formats_available, format])),
      };
      
      console.log('[Export] Marked content as exported:', taskId, format);
      
      return {
        contentStore: {
          ...state.contentStore,
          exportStatus: {
            ...state.contentStore.exportStatus,
            [taskId]: updatedExportStatus,
          },
        },
      };
    });
    
    // Also update the content's exportedAt field
    const content = get().getContent(taskId);
    if (content) {
      get().updateContent(taskId, {
        exportedAt: exportedAt || new Date().toISOString(),
        exportFormats: Array.from(new Set([...(content.exportFormats || []), format])),
      });
    }
    
    get().persistToStorage();
  },
  
  getExportStatus: (taskId: string) => {
    const state = get();
    return state.contentStore.exportStatus[taskId];
  },
  
  clearExportStatus: (taskId: string) => {
    set((state) => {
      const updatedExportStatus = { ...state.contentStore.exportStatus };
      delete updatedExportStatus[taskId];
      
      console.log('[Export] Cleared export status for task:', taskId);
      
      return {
        contentStore: {
          ...state.contentStore,
          exportStatus: updatedExportStatus,
        },
      };
    });
    
    get().persistToStorage();
  },

  // Session persistence methods
  setRecording: (recording: boolean) => set((state) => ({
    sessionState: { ...state.sessionState, isRecording: recording, recordingStartTime: recording ? Date.now() : undefined }
  })),

  setProcessing: (processing: boolean) => set((state) => ({
    sessionState: { ...state.sessionState, isProcessing: processing }
  })),

  setStreaming: (streaming: boolean, text?: string) => set((state) => ({
    sessionState: { ...state.sessionState, isStreaming: streaming, streamingText: streaming ? text : undefined }
  })),

  updateSession: (updates: Partial<SessionState>) => set((state) => ({
    sessionState: { ...state.sessionState, ...updates }
  })),

  cacheSession: () => {
    const state = get();
    const sessionData = {
      ...state.sessionState,
      timestamp: Date.now()
    };
    
    try {
      localStorage.setItem('aura_session', JSON.stringify(sessionData));
      console.log('[SessionPersist] Session cached:', sessionData);
    } catch (error) {
      console.warn('[SessionPersist] Failed to cache session:', error);
    }
  },

  restoreSession: () => {
    try {
      const data = localStorage.getItem('aura_session');
      if (!data) {
        console.log('[SessionPersist] No cached session found');
        return;
      }

      const sessionData = JSON.parse(data);
      const age = Date.now() - (sessionData.timestamp || 0);
      
      // Only restore if session is less than 30 minutes old
      if (age > 30 * 60 * 1000) {
        console.log('[SessionPersist] Cached session too old, clearing');
        get().clearSession();
        return;
      }

      // Restore session state
      set((state) => ({
        sessionState: {
          ...state.sessionState,
          isRecording: sessionData.isRecording || false,
          isProcessing: sessionData.isProcessing || false,
          isStreaming: sessionData.isStreaming || false,
          lastPrompt: sessionData.lastPrompt || null,
          currentTaskId: sessionData.currentTaskId,
          resumePending: sessionData.isProcessing || sessionData.isStreaming,
          streamingText: sessionData.streamingText,
          recordingStartTime: sessionData.recordingStartTime
        }
      }));
      
      console.log('[SessionPersist] Session restored:', sessionData);
    } catch (error) {
      console.warn('[SessionPersist] Failed to restore session:', error);
      get().clearSession();
    }
  },

  clearSession: () => {
    try {
      localStorage.removeItem('aura_session');
      console.log('[SessionPersist] Session cleared');
    } catch (error) {
      console.warn('[SessionPersist] Failed to clear session:', error);
    }
    
    set((state) => ({
      sessionState: {
        isRecording: false,
        isProcessing: false,
        isStreaming: false,
        lastPrompt: null,
        currentTaskId: undefined,
        resumePending: false,
        streamingText: undefined,
        recordingStartTime: undefined
      }
    }));
  },
  
  reset: () => set({ phase: 'idle' }),
  
  // Intelligence Content v3.3 Methods
  saveIntelligenceContent: (content: IntelligenceContent) => {
    set((state) => ({
      intelContent: {
        ...state.intelContent,
        [content.contentId]: content,
      }
    }));
    console.log('[IntelContent] Saved intelligence content:', content.contentId, content.contentType);
    
    // Persist to storage
    get().persistIntelligenceContent();
    
    // Also update any related request status to indicate intelligence is available
    if (content.taskId) {
      const request = get().requests.find(req => req.id === content.taskId);
      if (request && request.status === 'Processing') {
        get().updateRequestStatus(content.taskId, 'Complete');
      }
    }
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
    
    // Persist to storage
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
    
    // Persist to storage
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
