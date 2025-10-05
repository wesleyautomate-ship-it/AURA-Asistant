# AI Requests Integration

This document outlines the implementation of the AI Requests management feature and Command Center backend integration.

## Overview

This feature replaces mock data with real backend integration for AI request tracking and command processing functionality, providing:

- Real-time AI request management with SSE updates
- Command Center backend integration for request creation
- Complete request lifecycle management (queued → processing → ready for review → approved)
- Dashboard integration with live request counts

## Architecture

### Frontend Components

#### Services Layer (`packages/services/src/aiRequestService.ts`)
- **AIRequestService**: Main service class for API interactions
- **SSE Client**: Real-time updates via Server-Sent Events
- **Mapping Functions**: Transform backend AIRequestResponse to frontend Request interface

Key endpoints:
- `POST /api/requests/` - Create new AI request
- `GET /api/requests/` - List requests with filters
- `GET /api/requests/{id}` - Get single request
- `GET /api/requests/{id}/stream` - SSE stream for real-time updates
- `POST /api/requests/{id}/approve` - Approve request
- `POST /api/requests/{id}/revise` - Request revision

#### State Management (`packages/store/src/aiRequestStore.ts`)
- **useAIRequestStore**: Zustand store for AI request state
- **Real-time subscriptions**: Automatic SSE subscription for in-flight requests
- **Request counts**: Live counts by status (queued, processing, ready for review, etc.)
- **Error handling**: Integrated with UIStore for snackbars and loading states

State structure:
```typescript
{
  byId: Record<number, Request>     // Normalized requests
  allIds: number[]                  // Request IDs in order
  loading: boolean                  // Global loading state
  error: string | null              // Error message
  streaming: Record<string, () => void>  // Active SSE subscriptions
  counts: RequestCounts             // Status counts
  selectedRequestId: number | null  // Selected request
}
```

#### UI Components
- **RequestsView**: Complete request management interface with filtering, search, and actions
- **Command Center Integration**: Real backend request creation from text/voice commands
- **Dashboard Integration**: Live request counts and recent activity

### Backend Integration

The implementation integrates with existing backend endpoints:

#### AI Request Router (`backend/app/api/v1/ai_request_router.py`)
- Request lifecycle management
- SSE streaming support
- Template and brand asset integration
- File serving for deliverables

#### Status Mapping
Backend status → Frontend status:
- `queued` → `Queued` (0% progress)
- `planning` → `Processing` (20% progress)  
- `generating` → `Processing` (60% progress)
- `validating` → `Processing` (85% progress)
- `draft_ready` → `Ready for Review` (95% progress)
- `approved` → `Ready for Review` (100% progress)
- `failed` → `Processing` (with error indicators)

## Features Implemented

### 1. RequestsView Component
- **Filtering**: By status (All, Queued, Processing, Ready for Review)
- **Search**: Full-text search across title, description, and category
- **Actions**: Approve and Revise buttons for ready requests
- **Real-time updates**: Automatic progress and status updates via SSE
- **Loading states**: Skeleton loaders and error handling
- **Empty states**: Helpful messaging when no requests exist

### 2. Command Center Integration
- **Smart team detection**: Automatically categorizes requests based on content
- **Request creation**: Converts text/voice commands to AI requests
- **Success feedback**: Confirmation messages with request details
- **Error handling**: Clear error messages for failed requests

### 3. Dashboard Integration
- **Live counts**: Real request counts replace mock data
- **Recent activity**: Shows latest requests with status
- **Auto-refresh**: Loads requests on mount if not cached
- **Empty states**: Guidance for creating first request

## SSE (Server-Sent Events) Implementation

### Connection Management
- **Retry logic**: Exponential backoff (1s → 2s → 4s → ... → 30s max)
- **Heartbeat timeout**: 45s timeout with automatic reconnection
- **Auth integration**: Bearer token in headers
- **Graceful degradation**: Stops retrying on 401/403 errors

### Event Processing
- **JSON parsing**: Handles `data:` lines with JSON payloads
- **Request updates**: Automatically updates store with new status/progress
- **Terminal states**: Stops streaming when request reaches approved/failed
- **Error handling**: Network errors trigger retry, parse errors are logged

### Subscription Lifecycle
```typescript
// Subscribe to request updates
const unsubscribe = AIRequestService.subscribeToRequestStream(id, {
  onUpdate: (request) => updateStore(request),
  onError: (error) => showError(error),
  onOpen: () => console.log('Connected'),
  onClose: () => console.log('Disconnected')
});

// Cleanup
unsubscribe();
```

## Testing Considerations

### Manual Testing Checklist
- [ ] Create request via Command Center text input
- [ ] Create request via Command Center voice input
- [ ] Verify request appears in RequestsView
- [ ] Test real-time status updates
- [ ] Test approve/revise actions
- [ ] Test search and filtering
- [ ] Test dashboard badge counts
- [ ] Test error scenarios (network issues, auth failures)
- [ ] Test SSE reconnection after network interruption

### Error Scenarios
1. **Network failures**: Should retry with exponential backoff
2. **Auth failures**: Should stop retrying and show auth error
3. **Server errors**: Should retry up to max attempts then show error
4. **Parse errors**: Should log and continue processing other messages

## Environment Setup

### Backend Requirements
- AI request router endpoints must be available
- SSE endpoint `/api/requests/{id}/stream` must support CORS and auth headers
- Request processing pipeline should emit progress updates

### Frontend Configuration
- API base URL configured in `packages/services/src/config.ts`
- Authentication token available in user store
- No additional SSE polyfills required (using fetch-based implementation)

## Performance Considerations

- **Request list virtualization**: Consider for 100+ requests
- **SSE connection limits**: Browser limit ~6 concurrent connections per domain
- **Memory cleanup**: All subscriptions cleaned up on component unmount
- **Debounced search**: Search input debounced to avoid excessive API calls

## Future Enhancements

1. **Bulk operations**: Select multiple requests for batch approve/revise
2. **Request templates**: Pre-defined request templates for common tasks
3. **Advanced filtering**: Filter by date range, team, priority
4. **Request details modal**: Expanded view with deliverables and history
5. **Offline support**: Cache requests for offline viewing
6. **Push notifications**: Browser notifications for completed requests

## Deployment Notes

- All MOCK_REQUESTS references have been removed
- New navigation item "Requests" added to bottom nav
- Store exports added to package index files
- SSE implementation works in development and production
- No breaking changes to existing API contracts