/**
 * Cross-Tab Session Synchronization Service
 * 
 * Handles multi-tab coordination using BroadcastChannel API to ensure:
 * - Only one active microphone session per browser
 * - Command history sync across tabs
 * - Session handoff between tabs
 * - Duplicate session prevention
 */

import { useCommandStore } from '../store/commandStore';
import type { UnifiedSession } from '../store/commandStore';

export interface CrossTabMessage {
  type: 'MIC_LOCK_REQUEST' | 'MIC_LOCK_ACQUIRED' | 'MIC_LOCK_RELEASED' | 'SESSION_UPDATE' | 
        'SESSION_HANDOFF' | 'HISTORY_SYNC' | 'TAB_PING' | 'TAB_PONG' | 'FORCE_TAKEOVER';
  payload?: any;
  sessionId?: string;
  tabId: string;
  deviceId: string;
  timestamp: number;
}

class CrossTabSyncService {
  private channel: BroadcastChannel | null = null;
  private isInitialized = false;
  private tabId: string;
  private deviceId: string;
  private heartbeatInterval: number | null = null;
  private activeTabs: Set<string> = new Set();
  private lastPing = 0;

  constructor() {
    this.tabId = this.generateTabId();
    this.deviceId = this.getDeviceId();
    this.initialize();
  }

  private generateTabId(): string {
    return `tab_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getDeviceId(): string {
    const stored = localStorage.getItem('aura_device_id');
    if (stored) return stored;
    
    const deviceId = `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('aura_device_id', deviceId);
    return deviceId;
  }

  public initialize(): void {
    if (this.isInitialized || typeof window === 'undefined') return;

    try {
      this.channel = new BroadcastChannel('aura_cross_tab');
      this.setupMessageHandlers();
      this.startHeartbeat();
      this.performTabDiscovery();
      this.isInitialized = true;
      
      console.log('[CrossTab] Service initialized for tab:', this.tabId);
    } catch (error) {
      console.error('[CrossTab] Failed to initialize BroadcastChannel:', error);
    }
  }

  private setupMessageHandlers(): void {
    if (!this.channel) return;

    this.channel.onmessage = (event) => {
      const message: CrossTabMessage = event.data;
      
      // Ignore our own messages
      if (message.tabId === this.tabId) return;
      
      console.log('[CrossTab] Received message:', message.type, 'from:', message.tabId);
      
      switch (message.type) {
        case 'MIC_LOCK_REQUEST':
          this.handleMicLockRequest(message);
          break;
        case 'MIC_LOCK_ACQUIRED':
          this.handleMicLockAcquired(message);
          break;
        case 'MIC_LOCK_RELEASED':
          this.handleMicLockReleased(message);
          break;
        case 'SESSION_UPDATE':
          this.handleSessionUpdate(message);
          break;
        case 'SESSION_HANDOFF':
          this.handleSessionHandoff(message);
          break;
        case 'HISTORY_SYNC':
          this.handleHistorySync(message);
          break;
        case 'TAB_PING':
          this.handleTabPing(message);
          break;
        case 'TAB_PONG':
          this.handleTabPong(message);
          break;
        case 'FORCE_TAKEOVER':
          this.handleForceTakeover(message);
          break;
      }
    };
  }

  private startHeartbeat(): void {
    // Send ping every 10 seconds to detect active tabs
    this.heartbeatInterval = window.setInterval(() => {
      this.sendTabPing();
      this.cleanupInactiveTabs();
    }, 10000);

    // Send initial ping
    this.sendTabPing();
  }

  private performTabDiscovery(): void {
    // Send ping to discover existing tabs
    this.broadcast({
      type: 'TAB_PING',
      tabId: this.tabId,
      deviceId: this.deviceId,
      timestamp: Date.now()
    });
  }

  private sendTabPing(): void {
    this.lastPing = Date.now();
    this.broadcast({
      type: 'TAB_PING',
      tabId: this.tabId,
      deviceId: this.deviceId,
      timestamp: Date.now()
    });
  }

  private handleTabPing(message: CrossTabMessage): void {
    // Add tab to active tabs
    this.activeTabs.add(message.tabId);
    
    // Respond with pong
    this.broadcast({
      type: 'TAB_PONG',
      tabId: this.tabId,
      deviceId: this.deviceId,
      timestamp: Date.now()
    });
    
    console.log('[CrossTab] Active tabs:', this.activeTabs.size + 1); // +1 for current tab
  }

  private handleTabPong(message: CrossTabMessage): void {
    this.activeTabs.add(message.tabId);
  }

  private cleanupInactiveTabs(): void {
    const now = Date.now();
    const timeout = 30000; // 30 seconds
    
    // Remove tabs that haven't responded to pings
    this.activeTabs.forEach(tabId => {
      // In a real implementation, we'd track last seen time per tab
      // For now, we'll just clean up after the timeout period
    });
  }

  public requestMicLock(): boolean {
    const store = useCommandStore.getState();
    
    // Check if we already have the lock
    const currentLock = this.getCurrentMicLock();
    if (currentLock && currentLock.tabId === this.tabId) {
      console.log('[CrossTab] Already have mic lock');
      return true;
    }
    
    // Check if another tab has an active lock
    if (currentLock && this.isLockValid(currentLock)) {
      console.warn('[CrossTab] Another tab has active mic lock:', currentLock.tabId);
      
      // Request takeover if current session is more important
      if (this.shouldTakeoverLock(currentLock)) {
        return this.forceTakeover();
      }
      
      return false;
    }
    
    // Acquire the lock
    const lockData = {
      tabId: this.tabId,
      deviceId: this.deviceId,
      sessionId: store.session.id,
      timestamp: Date.now(),
      isRecording: store.session.isRecording
    };
    
    try {
      localStorage.setItem('aura_mic_lock', JSON.stringify(lockData));
      
      this.broadcast({
        type: 'MIC_LOCK_ACQUIRED',
        payload: lockData,
        tabId: this.tabId,
        deviceId: this.deviceId,
        timestamp: Date.now()
      });
      
      console.log('[CrossTab] Acquired mic lock');
      return true;
    } catch (error) {
      console.error('[CrossTab] Failed to acquire mic lock:', error);
      return false;
    }
  }

  public releaseMicLock(): void {
    const currentLock = this.getCurrentMicLock();
    if (!currentLock || currentLock.tabId !== this.tabId) {
      return;
    }
    
    try {
      localStorage.removeItem('aura_mic_lock');
      
      this.broadcast({
        type: 'MIC_LOCK_RELEASED',
        tabId: this.tabId,
        deviceId: this.deviceId,
        timestamp: Date.now()
      });
      
      console.log('[CrossTab] Released mic lock');
    } catch (error) {
      console.error('[CrossTab] Failed to release mic lock:', error);
    }
  }

  private getCurrentMicLock(): any {
    try {
      const lockData = localStorage.getItem('aura_mic_lock');
      return lockData ? JSON.parse(lockData) : null;
    } catch {
      return null;
    }
  }

  private isLockValid(lockData: any): boolean {
    const age = Date.now() - lockData.timestamp;
    const maxAge = 30000; // 30 seconds
    
    return age < maxAge && this.activeTabs.has(lockData.tabId);
  }

  private shouldTakeoverLock(currentLock: any): boolean {
    const store = useCommandStore.getState();
    
    // Takeover if the current lock is stale
    if (!this.isLockValid(currentLock)) {
      return true;
    }
    
    // Takeover if our session is more recent and important
    if (store.session.lastActiveAt > currentLock.timestamp) {
      console.log('[CrossTab] Current session is more recent, requesting takeover');
      return true;
    }
    
    return false;
  }

  private forceTakeover(): boolean {
    console.log('[CrossTab] Forcing mic lock takeover');
    
    this.broadcast({
      type: 'FORCE_TAKEOVER',
      tabId: this.tabId,
      deviceId: this.deviceId,
      timestamp: Date.now()
    });
    
    // Wait a moment for other tabs to respond, then take the lock
    setTimeout(() => {
      const store = useCommandStore.getState();
      const lockData = {
        tabId: this.tabId,
        deviceId: this.deviceId,
        sessionId: store.session.id,
        timestamp: Date.now(),
        isRecording: store.session.isRecording
      };
      
      localStorage.setItem('aura_mic_lock', JSON.stringify(lockData));
      
      this.broadcast({
        type: 'MIC_LOCK_ACQUIRED',
        payload: lockData,
        tabId: this.tabId,
        deviceId: this.deviceId,
        timestamp: Date.now()
      });
    }, 500);
    
    return true;
  }

  private handleMicLockRequest(message: CrossTabMessage): void {
    const store = useCommandStore.getState();
    
    // If we're actively recording, deny the request
    if (store.session.isRecording && !store.session.recordingPaused) {
      console.log('[CrossTab] Denying mic lock request - actively recording');
      return;
    }
    
    // Otherwise, consider handing over the lock
    console.log('[CrossTab] Considering mic lock handover');
  }

  private handleMicLockAcquired(message: CrossTabMessage): void {
    const store = useCommandStore.getState();
    
    // If we were recording, pause it
    if (store.session.isRecording && !store.session.recordingPaused) {
      console.log('[CrossTab] Another tab acquired mic lock - pausing recording');
      store.pauseRecording();
    }
  }

  private handleMicLockReleased(message: CrossTabMessage): void {
    console.log('[CrossTab] Mic lock released by another tab');
    
    // Opportunity to acquire the lock if we need it
    const store = useCommandStore.getState();
    if (store.session.recordingPaused) {
      console.log('[CrossTab] Attempting to resume recording after lock release');
      setTimeout(() => {
        if (this.requestMicLock()) {
          store.resumeRecording();
        }
      }, 100);
    }
  }

  private handleSessionUpdate(message: CrossTabMessage): void {
    if (!message.payload) return;
    
    const incomingSession: UnifiedSession = message.payload.session;
    const store = useCommandStore.getState();
    
    // Only sync if the incoming session is more recent
    if (incomingSession.lastActiveAt > store.session.lastActiveAt) {
      console.log('[CrossTab] Syncing newer session from another tab');
      store.handleSessionTakeover(incomingSession);
    }
  }

  private handleSessionHandoff(message: CrossTabMessage): void {
    const store = useCommandStore.getState();
    
    if (message.payload && message.payload.targetTabId === this.tabId) {
      console.log('[CrossTab] Receiving session handoff');
      
      const handoffSession = message.payload.session;
      store.handleSessionTakeover(handoffSession);
      
      // Acquire mic lock if needed
      if (handoffSession.isRecording) {
        this.requestMicLock();
      }
    }
  }

  private handleHistorySync(message: CrossTabMessage): void {
    if (!message.payload) return;
    
    const { history, requests } = message.payload;
    const store = useCommandStore.getState();
    
    // Merge histories (avoid duplicates)
    const currentHistoryIds = new Set(store.history.map(h => `${h.text}_${h.at}`));
    const newHistory = history.filter((h: any) => !currentHistoryIds.has(`${h.text}_${h.at}`));
    
    if (newHistory.length > 0) {
      console.log(`[CrossTab] Syncing ${newHistory.length} new history items`);
      // Would need to implement a batch addHistory method
    }
    
    // Similar logic for requests
    const currentRequestIds = new Set(store.requests.map(r => r.id));
    const newRequests = requests.filter((r: any) => !currentRequestIds.has(r.id));
    
    if (newRequests.length > 0) {
      console.log(`[CrossTab] Syncing ${newRequests.length} new requests`);
      // Would need to implement batch syncTasks
    }
  }

  private handleForceTakeover(message: CrossTabMessage): void {
    const store = useCommandStore.getState();
    
    console.log('[CrossTab] Forced takeover requested by another tab');
    
    // If we're not actively doing something important, allow takeover
    if (!store.session.isRecording || store.session.recordingPaused) {
      console.log('[CrossTab] Allowing forced takeover');
      this.releaseMicLock();
      
      // Pause our session
      store.pauseSession();
    } else {
      console.log('[CrossTab] Refusing forced takeover - actively recording');
    }
  }

  public syncHistoryToOtherTabs(): void {
    const store = useCommandStore.getState();
    
    this.broadcast({
      type: 'HISTORY_SYNC',
      payload: {
        history: store.history,
        requests: store.requests
      },
      tabId: this.tabId,
      deviceId: this.deviceId,
      timestamp: Date.now()
    });
  }

  public handoffSessionToTab(targetTabId: string): void {
    const store = useCommandStore.getState();
    
    console.log('[CrossTab] Handing off session to tab:', targetTabId);
    
    this.broadcast({
      type: 'SESSION_HANDOFF',
      payload: {
        targetTabId,
        session: store.session
      },
      sessionId: store.session.id,
      tabId: this.tabId,
      deviceId: this.deviceId,
      timestamp: Date.now()
    });
    
    // Release our locks and pause session
    this.releaseMicLock();
    store.pauseSession();
  }

  private broadcast(message: CrossTabMessage): void {
    if (!this.channel) return;
    
    try {
      this.channel.postMessage(message);
    } catch (error) {
      console.error('[CrossTab] Failed to broadcast message:', error);
    }
  }

  public getActiveTabCount(): number {
    return this.activeTabs.size + 1; // +1 for current tab
  }

  public getTabId(): string {
    return this.tabId;
  }

  public getDeviceId(): string {
    return this.deviceId;
  }

  public destroy(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    
    if (this.channel) {
      this.releaseMicLock();
      this.channel.close();
      this.channel = null;
    }
    
    this.isInitialized = false;
    console.log('[CrossTab] Service destroyed');
  }
}

// Singleton instance
export const crossTabSync = new CrossTabSyncService();

// Auto-initialize when imported
if (typeof window !== 'undefined') {
  crossTabSync.initialize();
  
  // Cleanup on page unload
  window.addEventListener('beforeunload', () => {
    crossTabSync.destroy();
  });
}