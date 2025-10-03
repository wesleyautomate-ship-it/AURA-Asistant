# PropertyPro AI Stores

This document describes the Zustand state stores for PropertyPro AI. Import hooks from `src/store/index.ts`.

- usePropertyStore: Properties CRUD and selection
- useClientStore: CRM data and communication logs
- useTransactionStore: Transactions, milestones, escrow docs
- useUserStore: Auth and preferences (persisted)
- useUIStore: Global UI state

All stores expose loading/error/success via BaseAsyncSlice where applicable.

## Shared Types
- BaseAsyncSlice: { status: 'idle' | 'loading' | 'success' | 'error'; error: string | null; lastUpdated?: string }
- Id: string

## Property Store
State:
- items: Property[]
- selectedId: Id | null
- fetch/mutate: BaseAsyncSlice
Actions:
- fetchProperties()
- addProperty(payload)
- updateProperty(id, updates)
- deleteProperty(id)
- setSelected(id | null)
Selectors:
- selectProperties
- selectSelectedProperty
- selectPropertyFetchStatus
- selectPropertyMutateStatus

## Client Store
State:
- clients: Client[]
- logs: CommunicationLog[]
- fetch/mutate: BaseAsyncSlice
Actions:
- fetchClients()
- addClient(payload)
- updateClient(id, updates)
- logCommunication(payload)
- setLeadStatus(id, status)
Selectors:
- selectClients
- selectClientById(id)
- selectClientFetchStatus
- selectClientMutateStatus

## Transaction Store
State:
- transactions: Transaction[]
- fetch/mutate: BaseAsyncSlice
Actions:
- fetchTransactions()
- createTransaction(payload)
- updateMilestone(txId, milestoneId, updates)
- uploadDocument(txId, fileUrl)
Selectors:
- selectTransactions
- selectTransactionById(id)
- selectUpcomingDeadlines(daysAhead)
- selectTransactionFetchStatus
- selectTransactionMutateStatus

## User Store (Persisted)
State:
- user: UserProfile | null
- token: string | null
- preferences: { darkMode: boolean; locale: string }
Actions:
- login(user, token)
- logout()
- updatePreferences(updates)
Selectors:
- selectCurrentUser
- selectAuthToken
- selectPreferences

## UI Store
State:
- modalId: string | null
- globalLoading: boolean
- snackbars: Snackbar[]
Actions:
- openModal(id)
- closeModal()
- startLoading()
- stopLoading()
- pushSnackbar(snackbar)
- removeSnackbar(id)
Selectors:
- selectModalId
- selectGlobalLoading
- selectSnackbars

## Integration Notes
- Alpha-2 API endpoints assumed:
  - GET /properties, POST /properties, POST /properties/:id (PATCH via _method)
  - GET /clients, POST /clients, POST /clients/:id
  - GET /transactions, POST /transactions, POST /transactions/:txId/milestones/:milestoneId, POST /transactions/:txId/documents
- Update if backend contracts differ. Endpoints are placeholders until Alpha-2 confirms.