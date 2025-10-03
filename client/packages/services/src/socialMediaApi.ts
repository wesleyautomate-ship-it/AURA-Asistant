// Lightweight API layer for social platforms (stubs/mocks)
// Real integrations should securely handle OAuth and tokens on the backend.

export type Platform = 'facebook' | 'instagram' | 'linkedin';

export interface PlatformConnection {
  platform: Platform;
  connected: boolean;
  accountName?: string;
}

export interface ScheduledPost {
  id: string;
  caption: string;
  imageUrl?: string;
  platforms: Platform[];
  scheduledAt: string; // ISO
}


import { apiGet, apiPost } from "./api";

export const socialMediaApi = {
  async getConnections(): Promise<PlatformConnection[]> {
    return apiGet<PlatformConnection[]>("/api/v1/social/connections");
  },
  async connect(platform: Platform): Promise<PlatformConnection> {
    return apiPost<PlatformConnection>("/api/v1/social/connect", { platform });
  },
  async disconnect(platform: Platform): Promise<PlatformConnection> {
    return apiPost<PlatformConnection>("/api/v1/social/disconnect", { platform });
  },
  async postNow(payload: { caption: string; imageUrl?: string; platforms: Platform[] }): Promise<{ id: string }> {
    return apiPost<{ id: string }>("/api/v1/social/post", payload);
  },
  async schedule(payload: { caption: string; imageUrl?: string; platforms: Platform[]; scheduledAt: string }): Promise<ScheduledPost> {
    return apiPost<ScheduledPost>("/api/v1/social/schedule", payload);
  },
  async listScheduled(): Promise<ScheduledPost[]> {
    return apiGet<ScheduledPost[]>("/api/v1/social/scheduled");
  },
};

