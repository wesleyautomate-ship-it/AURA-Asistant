import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Snackbar {
  id: string;
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
}

export type CommandMode = 'audio' | 'text';
export type CommandStatus = 'idle' | 'recording' | 'reviewing' | 'typing' | 'processing';

interface UIState {
  modalId: string | null;
  globalLoading: boolean;
  snackbars: Snackbar[];
  commandCenterOpen: boolean;
  commandMode: CommandMode;
  commandStatus: CommandStatus;
  commandText: string;
  commandTranscript: string;
  commandError: string | null;
  // actions
  openModal: (id: string) => void;
  closeModal: () => void;
  startLoading: () => void;
  stopLoading: () => void;
  pushSnackbar: (snackbar: Snackbar) => void;
  removeSnackbar: (id: string) => void;
  openCommandCenter: (mode?: CommandMode) => void;
  closeCommandCenter: () => void;
  setCommandMode: (mode: CommandMode) => void;
  setCommandStatus: (status: CommandStatus) => void;
  setCommandText: (text: string) => void;
  setCommandTranscript: (transcript: string) => void;
  setCommandError: (error: string | null) => void;
  resetCommandState: () => void;
}

const defaultCommandState = {
  commandMode: 'audio' as CommandMode,
  commandStatus: 'idle' as CommandStatus,
  commandText: '',
  commandTranscript: '',
  commandError: null,
};

export const useUIStore = create<UIState>()(devtools((set, get) => ({
  modalId: null,
  globalLoading: false,
  snackbars: [],
  commandCenterOpen: false,
  ...defaultCommandState,

  openModal: (id) => set({ modalId: id }),
  closeModal: () => set({ modalId: null }),
  startLoading: () => set({ globalLoading: true }),
  stopLoading: () => set({ globalLoading: false }),
  pushSnackbar: (snackbar) => set({ snackbars: [...get().snackbars, snackbar] }),
  removeSnackbar: (id) => set({ snackbars: get().snackbars.filter(s => s.id !== id) }),

  openCommandCenter: (mode) => set((state) => ({
    commandCenterOpen: true,
    commandMode: mode ?? state.commandMode ?? 'audio',
    commandStatus: 'idle',
    commandError: null,
  })),
  closeCommandCenter: () => set({ commandCenterOpen: false }),
  setCommandMode: (mode) => set((state) => ({
    commandMode: mode,
    commandStatus: mode === 'text'
      ? (state.commandText.trim().length > 0 ? 'typing' : 'idle')
      : 'idle',
    commandError: null,
  })),
  setCommandStatus: (status) => set({ commandStatus: status }),
  setCommandText: (text) => set((state) => ({
    commandText: text,
    commandStatus: state.commandMode === 'text'
      ? (text.trim().length > 0 ? 'typing' : 'idle')
      : state.commandStatus,
  })),
  setCommandTranscript: (transcript) => set({ commandTranscript: transcript }),
  setCommandError: (error) => set({ commandError: error }),
  resetCommandState: () => set({
    commandCenterOpen: false,
    ...defaultCommandState,
  }),
})));

// Selectors
export const selectModalId = (s: UIState) => s.modalId;
export const selectGlobalLoading = (s: UIState) => s.globalLoading;
export const selectSnackbars = (s: UIState) => s.snackbars;
export const selectCommandCenterOpen = (s: UIState) => s.commandCenterOpen;
export const selectCommandMode = (s: UIState) => s.commandMode;
export const selectCommandStatus = (s: UIState) => s.commandStatus;
export const selectCommandText = (s: UIState) => s.commandText;
export const selectCommandTranscript = (s: UIState) => s.commandTranscript;
export const selectCommandError = (s: UIState) => s.commandError;