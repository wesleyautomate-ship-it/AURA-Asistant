/**
 * Simple User Service for PropertyPro AI Real Estate Assistant
 * 
 * This service provides simple user and session management without authentication
 * for the voice command system.
 */

class UserService {
  private userId: string;
  private sessionId: string;

  constructor() {
    // Generate simple user and session IDs
    this.userId = 'demo-user-123';
    this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get user ID for API calls
   */
  getUserId(): string {
    return this.userId;
  }

  /**
   * Get session ID for API calls
   */
  getSessionId(): string {
    return this.sessionId;
  }

  /**
   * Generate new session ID
   */
  generateNewSession(): void {
    this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Export singleton instance
export const userService = new UserService();
