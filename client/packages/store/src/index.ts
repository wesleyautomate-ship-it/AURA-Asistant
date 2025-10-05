export { usePropertyStore, selectProperties, selectSelectedProperty, selectPropertyFetchStatus, selectPropertyMutateStatus } from './propertyStore';
export { useClientStore, selectClients, selectClientById, selectClientFetchStatus, selectClientMutateStatus } from './clientStore';
export { useTransactionStore, selectTransactions, selectTransactionById, selectUpcomingDeadlines, selectTransactionFetchStatus, selectTransactionMutateStatus } from './transactionStore';
export { useUserStore, selectCurrentUser, selectAuthToken, selectPreferences } from './userStore';
export {
  useUIStore,
  selectModalId,
  selectGlobalLoading,
  selectSnackbars,
  selectCommandCenterOpen,
  selectCommandMode,
  selectCommandStatus,
  selectCommandText,
  selectCommandTranscript,
  selectCommandError,
} from './uiStore';

// AI Request Store
export {
  useAIRequestStore,
  selectAllRequests,
  selectRequestById,
  selectRequestsByStatus,
  selectProcessingRequests,
  selectCounts,
  selectLoading,
  selectError,
  selectSelectedRequest,
  selectIsStreaming,
} from './aiRequestStore';
export type { RequestCounts } from './aiRequestStore';

export type { Property } from './propertyStore';
export type { Client, CommunicationLog } from './clientStore';
export type { Transaction, Milestone } from './transactionStore';
export { 
  useTaskStore, 
  selectTasks, 
  selectTasksLoading, 
  selectTasksError, 
  selectSelectedTask, 
  selectIsModalOpen, 
  selectModalMode 
} from './taskStore';
export type { TaskStore, FetchStatus } from './taskStore';
