import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { Id, WithTimestamps } from './types';

export interface UserProfile extends WithTimestamps<{
  id: Id;
  name: string;
  email: string;
  role?: 'agent' | 'admin' | 'manager' | string;
}> {}

export interface Preferences {
  darkMode: boolean;
  locale: string;
}

interface LoginPayload {
  user: UserProfile;
  accessToken: string;
  refreshToken?: string | null;
  expiresAt?: number | null;
}

interface UserState {
  user: UserProfile | null;
  token: string | null;
  refreshToken: string | null;
  tokenExpiresAt: number | null;
  preferences: Preferences;
  // actions
  login: (payload: LoginPayload) => void;
  logout: () => void;
  updatePreferences: (updates: Partial<Preferences>) => void;
}

export const useUserStore = create<UserState>()(persist(devtools((set) => ({
  user: null,
  token: null,
  refreshToken: null,
  tokenExpiresAt: null,
  preferences: { darkMode: false, locale: 'en-US' },

  login: ({ user, accessToken, refreshToken, expiresAt }) => set({
    user,
    token: accessToken,
    refreshToken: refreshToken ?? null,
    tokenExpiresAt: expiresAt ?? null,
  }),

  logout: () => set({ user: null, token: null, refreshToken: null, tokenExpiresAt: null }),

  updatePreferences: (updates) => set((s) => ({ preferences: { ...s.preferences, ...updates } })),
})), {
  name: 'ppai-user-store',
}));

// Selectors
export const selectCurrentUser = (s: UserState) => s.user;
export const selectAuthToken = (s: UserState) => s.token;
export const selectPreferences = (s: UserState) => s.preferences;
export const selectSession = (s: UserState) => ({
  token: s.token,
  refreshToken: s.refreshToken,
  expiresAt: s.tokenExpiresAt,
});
