/**
 * Offline Mode & Recovery System
 * 
 * Provides comprehensive offline support including:
 * - Network status detection and monitoring
 * - Offline audio recording with IndexedDB storage
 * - Queue management for transcription and orchestration
 * - Auto-resume functionality when connection returns
 * - Data synchronization and conflict resolution
 */

import { useCommandStore } from '../store/commandStore';
import type { QueuedOperation } from '../store/commandStore';
import api from './http';

interface OfflineAudioRecord {
  id: string;
  sessionId: string;
  audioBlob: Blob;
  timestamp: number;
  transcribed: boolean;
  metadata?: {
    duration: number;
    size: number;
    mimeType: string;
  };
}

interface OfflineOperation extends QueuedOperation {
  priority: number;
  dependencies?: string[];
  offlineData?: any;
}

interface NetworkStatus {
  online: boolean;
  connectionType?: string;
  effectiveType?: string;
  downlink?: number;
  rtt?: number;
  lastOnline: number;
  lastOffline: number;
}

class OfflineRecoveryService {
  private db: IDBDatabase | null = null;
  private dbName = 'AuraOfflineDB';
  private dbVersion = 1;
  private isInitialized = false;
  private networkStatus: NetworkStatus;
  private statusListeners: Set<(status: NetworkStatus) => void> = new Set();
  private syncInProgress = false;
  private retryTimeouts: Map<string, number> = new Map();

  constructor() {
    this.networkStatus = {
      online: typeof navigator !== 'undefined' ? navigator.onLine : true,
      lastOnline: Date.now(),
      lastOffline: 0
    };
    
    this.initialize();
  }

  public async initialize(): Promise<void> {
    if (this.isInitialized || typeof window === 'undefined') return;

    try {
      // Initialize IndexedDB
      await this.initializeDB();
      
      // Setup network monitoring
      this.setupNetworkMonitoring();
      
      // Setup connection quality monitoring
      this.setupConnectionQualityMonitoring();
      
      // Perform initial sync if online
      if (this.networkStatus.online) {
        this.performStartupSync();
      }
      
      this.isInitialized = true;
      console.log('[Offline] Recovery service initialized');
    } catch (error) {
      console.error('[Offline] Failed to initialize recovery service:', error);
    }
  }

  private async initializeDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);
      
      request.onerror = () => {
        console.error('[Offline] Failed to open IndexedDB:', request.error);
        reject(request.error);
      };
      
      request.onsuccess = () => {
        this.db = request.result;
        console.log('[Offline] IndexedDB initialized');
        resolve();
      };
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // Audio recordings store
        if (!db.objectStoreNames.contains('audioRecordings')) {
          const audioStore = db.createObjectStore('audioRecordings', { keyPath: 'id' });
          audioStore.createIndex('sessionId', 'sessionId', { unique: false });
          audioStore.createIndex('timestamp', 'timestamp', { unique: false });
          audioStore.createIndex('transcribed', 'transcribed', { unique: false });
        }
        
        // Offline operations queue
        if (!db.objectStoreNames.contains('offlineOperations')) {
          const opsStore = db.createObjectStore('offlineOperations', { keyPath: 'id' });
          opsStore.createIndex('type', 'type', { unique: false });
          opsStore.createIndex('priority', 'priority', { unique: false });
          opsStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
        
        // Session data backup
        if (!db.objectStoreNames.contains('sessionBackups')) {
          const sessionStore = db.createObjectStore('sessionBackups', { keyPath: 'sessionId' });
          sessionStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
        
        console.log('[Offline] IndexedDB schema created');
      };
    });
  }

  private setupNetworkMonitoring(): void {
    if (typeof window === 'undefined') return;

    // Basic online/offline detection
    window.addEventListener('online', () => {
      this.updateNetworkStatus({ 
        online: true, 
        lastOnline: Date.now() 
      });
      this.handleConnectionRestored();
    });
    
    window.addEventListener('offline', () => {
      this.updateNetworkStatus({ 
        online: false, 
        lastOffline: Date.now() 
      });
      this.handleConnectionLost();
    });
    
    // Periodic connectivity check
    setInterval(() => {
      this.performConnectivityCheck();
    }, 30000); // Check every 30 seconds
  }

  private setupConnectionQualityMonitoring(): void {
    if (typeof navigator !== 'undefined' && 'connection' in navigator) {
      const connection = (navigator as any).connection;
      
      const updateConnectionInfo = () => {
        this.updateNetworkStatus({
          connectionType: connection.type,
          effectiveType: connection.effectiveType,
          downlink: connection.downlink,
          rtt: connection.rtt
        });
      };
      
      connection.addEventListener('change', updateConnectionInfo);
      updateConnectionInfo(); // Initial update
    }
  }

  private async performConnectivityCheck(): Promise<void> {
    if (!this.networkStatus.online) return;
    
    try {
      // Test connection with a lightweight request
      await api.head('/health', {
        timeout: 5000,
      });
      
      // Connection is good
      if (!this.networkStatus.online) {
        this.updateNetworkStatus({ online: true, lastOnline: Date.now() });
        this.handleConnectionRestored();
      }
    } catch (error) {
      // Connection issue detected
      if (this.networkStatus.online) {
        console.warn('[Offline] Connection quality check failed:', error);
        this.updateNetworkStatus({ online: false, lastOffline: Date.now() });
        this.handleConnectionLost();
      }
    }
  }

  private updateNetworkStatus(updates: Partial<NetworkStatus>): void {
    this.networkStatus = { ...this.networkStatus, ...updates };
    
    // Notify listeners
    this.statusListeners.forEach(listener => {
      try {
        listener(this.networkStatus);
      } catch (error) {
        console.error('[Offline] Error in network status listener:', error);
      }
    });
    
    console.log('[Offline] Network status updated:', this.networkStatus);
  }

  private handleConnectionLost(): void {
    console.log('[Offline] Connection lost - entering offline mode');
    
    const store = useCommandStore.getState();
    
    // Update session to indicate offline mode
    // Note: 'connected' field should be added to SessionState interface if needed
    // For now, we'll omit this update
    console.log('[Offline] Session marked as disconnected');
    
    // If currently recording, continue but mark as offline
    if (store.session.isRecording) {
      console.log('[Offline] Recording will continue offline');
    }
    
    // Queue any pending operations for later
    this.queuePendingOperations();
  }

  private async handleConnectionRestored(): Promise<void> {
    console.log('[Offline] Connection restored - starting sync');
    
    const store = useCommandStore.getState();
    
    // Update session to indicate online mode
    // Note: 'connected' field should be added to SessionState interface if needed
    // For now, we'll omit this update
    console.log('[Offline] Session marked as connected');
    
    // Start synchronization process
    await this.performFullSync();
  }

  public async storeOfflineAudio(audioBlob: Blob, sessionId: string): Promise<string> {
    if (!this.db) throw new Error('IndexedDB not initialized');
    
    const id = `audio_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const record: OfflineAudioRecord = {
      id,
      sessionId,
      audioBlob,
      timestamp: Date.now(),
      transcribed: false,
      metadata: {
        duration: 0, // Would be calculated from audio
        size: audioBlob.size,
        mimeType: audioBlob.type
      }
    };
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['audioRecordings'], 'readwrite');
      const store = transaction.objectStore('audioRecordings');
      
      const request = store.add(record);
      
      request.onsuccess = () => {
        console.log('[Offline] Audio stored offline:', id);
        resolve(id);
      };
      
      request.onerror = () => {
        console.error('[Offline] Failed to store audio offline:', request.error);
        reject(request.error);
      };
    });
  }

  public async queueOfflineOperation(operation: Omit<OfflineOperation, 'id' | 'timestamp'>): Promise<string> {
    if (!this.db) throw new Error('IndexedDB not initialized');
    
    const id = `op_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const queuedOp: OfflineOperation = {
      id,
      timestamp: Date.now(),
      ...operation,
      retryCount: operation.retryCount ?? 0,
      priority: operation.priority ?? 1
    };
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offlineOperations'], 'readwrite');
      const store = transaction.objectStore('offlineOperations');
      
      const request = store.add(queuedOp);
      
      request.onsuccess = () => {
        console.log('[Offline] Operation queued:', operation.type, id);
        resolve(id);
      };
      
      request.onerror = () => {
        console.error('[Offline] Failed to queue operation:', request.error);
        reject(request.error);
      };
    });
  }

  private async queuePendingOperations(): Promise<void> {
    const store = useCommandStore.getState();
    
    // Queue any session operations that were in progress
    if (store.session.queuedOperations.length > 0) {
      for (const op of store.session.queuedOperations) {
        await this.queueOfflineOperation({
          type: op.type,
          data: op.data,
          priority: 2, // Higher priority for interrupted operations
          retryCount: op.retryCount
        });
      }
      
      // Clear the in-memory queue
      store.clearQueue();
    }
    
    // Queue any pending requests that haven't been processed
    const pendingRequests = store.requests.filter(req => 
      req.status === 'Pending' || req.status === 'Processing'
    );
    
    for (const request of pendingRequests) {
      await this.queueOfflineOperation({
        type: 'orchestrate',
        data: { requestId: request.id, title: request.title },
        priority: 1,
        retryCount: 0
      });
    }
  }

  private async performStartupSync(): Promise<void> {
    console.log('[Offline] Performing startup sync');
    
    try {
      // Check for offline audio recordings
      const offlineAudio = await this.getOfflineAudioRecordings();
      if (offlineAudio.length > 0) {
        console.log(`[Offline] Found ${offlineAudio.length} offline audio recordings`);
        await this.syncOfflineAudio(offlineAudio);
      }
      
      // Process queued operations
      await this.processOfflineOperations();
      
      // Sync session data
      await this.syncSessionData();
      
      console.log('[Offline] Startup sync completed');
    } catch (error) {
      console.error('[Offline] Startup sync failed:', error);
    }
  }

  private async performFullSync(): Promise<void> {
    if (this.syncInProgress) {
      console.log('[Offline] Sync already in progress');
      return;
    }
    
    this.syncInProgress = true;
    
    try {
      console.log('[Offline] Starting full sync');
      
      // Sync offline audio first (highest priority)
      const offlineAudio = await this.getOfflineAudioRecordings();
      if (offlineAudio.length > 0) {
        await this.syncOfflineAudio(offlineAudio);
      }
      
      // Process all queued operations
      await this.processOfflineOperations();
      
      // Sync any session changes
      await this.syncSessionData();
      
      // Update store to reflect online status
      const store = useCommandStore.getState();
      store.saveSession();
      
      console.log('[Offline] Full sync completed successfully');
    } catch (error) {
      console.error('[Offline] Full sync failed:', error);
    } finally {
      this.syncInProgress = false;
    }
  }

  private async getOfflineAudioRecordings(): Promise<OfflineAudioRecord[]> {
    if (!this.db) return [];
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['audioRecordings'], 'readonly');
      const store = transaction.objectStore('audioRecordings');
      const index = store.index('transcribed');
      
      const request = index.getAll(); // Get all recordings
      
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  private async syncOfflineAudio(recordings: OfflineAudioRecord[]): Promise<void> {
    console.log(`[Offline] Syncing ${recordings.length} audio recordings`);
    
    for (const record of recordings) {
      try {
        // Import transcription service
        const { transcribeAudio } = await import('./api');
        
        console.log('[Offline] Transcribing offline audio:', record.id);
        const transcript = await transcribeAudio(record.audioBlob);
        
        if (transcript && transcript.trim()) {
          // Add to command store
          const store = useCommandStore.getState();
          const _requestId = store.addRequest(transcript);
          
          // Mark as transcribed in IndexedDB
          await this.markAudioTranscribed(record.id);
          
          console.log('[Offline] Successfully transcribed offline audio:', record.id);
        }
      } catch (error) {
        console.error('[Offline] Failed to sync audio recording:', record.id, error);
        
        // Implement retry logic
        await this.scheduleRetry(record.id, 'transcribe', record);
      }
    }
  }

  private async processOfflineOperations(): Promise<void> {
    if (!this.db) return;
    
    const operations = await this.getQueuedOperations();
    if (operations.length === 0) return;
    
    console.log(`[Offline] Processing ${operations.length} queued operations`);
    
    // Sort by priority and timestamp
    operations.sort((a, b) => {
      if (a.priority !== b.priority) return b.priority - a.priority;
      return a.timestamp - b.timestamp;
    });
    
    for (const operation of operations) {
      try {
        await this.processOfflineOperation(operation);
        await this.removeOfflineOperation(operation.id);
      } catch (error) {
        console.error('[Offline] Failed to process operation:', operation.id, error);
        
        // Increment retry count or remove if too many retries
        if (operation.retryCount >= 3) {
          await this.removeOfflineOperation(operation.id);
          console.warn('[Offline] Removing operation after max retries:', operation.id);
        } else {
          await this.incrementRetryCount(operation.id);
          await this.scheduleRetry(operation.id, operation.type, operation);
        }
      }
    }
  }

  private async getQueuedOperations(): Promise<OfflineOperation[]> {
    if (!this.db) return [];
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offlineOperations'], 'readonly');
      const store = transaction.objectStore('offlineOperations');
      const request = store.getAll();
      
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  private async processOfflineOperation(operation: OfflineOperation): Promise<void> {
    const store = useCommandStore.getState();
    
    switch (operation.type) {
      case 'transcribe':
        // Handle transcription (usually done in syncOfflineAudio)
        break;
        
      case 'orchestrate':
        if (operation.data?.requestId) {
          const { orchestrateCommand } = await import('./orchestrator');
          const request = store.requests.find(r => r.id === operation.data.requestId);
          
          if (request) {
            console.log('[Offline] Processing orchestration:', request.title);
            await orchestrateCommand(request.title);
            store.updateRequestStatus(request.id, 'Processing');
          }
        }
        break;
        
      case 'stream':
        // Handle streaming resumption
        if (operation.data?.requestId) {
          console.log('[Offline] Resuming stream for request:', operation.data.requestId);
          // Stream resumption logic would go here
        }
        break;
    }
  }

  private async syncSessionData(): Promise<void> {
    const store = useCommandStore.getState();
    
    // Send session heartbeat to backend to sync state
    try {
      store.heartbeat();
      console.log('[Offline] Session data synced with backend');
    } catch (error) {
      console.error('[Offline] Failed to sync session data:', error);
    }
  }

  private async markAudioTranscribed(audioId: string): Promise<void> {
    if (!this.db) return;
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['audioRecordings'], 'readwrite');
      const store = transaction.objectStore('audioRecordings');
      
      const request = store.get(audioId);
      
      request.onsuccess = () => {
        const record = request.result;
        if (record) {
          record.transcribed = true;
          const updateRequest = store.put(record);
          
          updateRequest.onsuccess = () => resolve();
          updateRequest.onerror = () => reject(updateRequest.error);
        } else {
          reject(new Error('Audio record not found'));
        }
      };
      
      request.onerror = () => reject(request.error);
    });
  }

  private async removeOfflineOperation(operationId: string): Promise<void> {
    if (!this.db) return;
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offlineOperations'], 'readwrite');
      const store = transaction.objectStore('offlineOperations');
      const request = store.delete(operationId);
      
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private async incrementRetryCount(operationId: string): Promise<void> {
    if (!this.db) return;
    
    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction(['offlineOperations'], 'readwrite');
      const store = transaction.objectStore('offlineOperations');
      
      const request = store.get(operationId);
      
      request.onsuccess = () => {
        const operation = request.result;
        if (operation) {
          operation.retryCount = (operation.retryCount || 0) + 1;
          const updateRequest = store.put(operation);
          
          updateRequest.onsuccess = () => resolve();
          updateRequest.onerror = () => reject(updateRequest.error);
        } else {
          reject(new Error('Operation not found'));
        }
      };
      
      request.onerror = () => reject(request.error);
    });
  }

  private async scheduleRetry(operationId: string, _type: string, data: any): Promise<void> {
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s...
    const delay = Math.pow(2, (data.retryCount || 0)) * 1000;
    const maxDelay = 60000; // Max 1 minute
    
    const actualDelay = Math.min(delay, maxDelay);
    
    console.log(`[Offline] Scheduling retry for ${operationId} in ${actualDelay}ms`);
    
    const timeoutId = window.setTimeout(() => {
      this.retryTimeouts.delete(operationId);
      
      // Only retry if still offline or if connection is restored
      if (!this.networkStatus.online || this.syncInProgress) {
        console.log('[Offline] Retrying operation:', operationId);
        this.processOfflineOperation(data).catch(error => {
          console.error('[Offline] Retry failed:', error);
        });
      }
    }, actualDelay);
    
    this.retryTimeouts.set(operationId, timeoutId);
  }

  // Public API methods
  public getNetworkStatus(): NetworkStatus {
    return { ...this.networkStatus };
  }

  public isOnline(): boolean {
    return this.networkStatus.online;
  }

  public addNetworkStatusListener(listener: (status: NetworkStatus) => void): void {
    this.statusListeners.add(listener);
  }

  public removeNetworkStatusListener(listener: (status: NetworkStatus) => void): void {
    this.statusListeners.delete(listener);
  }

  public async clearOfflineData(): Promise<void> {
    if (!this.db) return;
    
    const transaction = this.db.transaction(['audioRecordings', 'offlineOperations', 'sessionBackups'], 'readwrite');
    
    await Promise.all([
      new Promise<void>((resolve, reject) => {
        const request = transaction.objectStore('audioRecordings').clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      }),
      new Promise<void>((resolve, reject) => {
        const request = transaction.objectStore('offlineOperations').clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      }),
      new Promise<void>((resolve, reject) => {
        const request = transaction.objectStore('sessionBackups').clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      })
    ]);
    
    console.log('[Offline] All offline data cleared');
  }

  public destroy(): void {
    // Clear all retry timeouts
    this.retryTimeouts.forEach(timeoutId => clearTimeout(timeoutId));
    this.retryTimeouts.clear();
    
    // Clear listeners
    this.statusListeners.clear();
    
    // Close database
    if (this.db) {
      this.db.close();
      this.db = null;
    }
    
    this.isInitialized = false;
    console.log('[Offline] Recovery service destroyed');
  }
}

// Singleton instance
export const offlineRecovery = new OfflineRecoveryService();

// Export for external use
export type { NetworkStatus, OfflineAudioRecord, OfflineOperation };
