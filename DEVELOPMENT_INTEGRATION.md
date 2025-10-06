# Development Integration Guide

## Overview
The frontend has been successfully configured to integrate with the backend API and bypass authentication for development. This guide provides instructions for testing the integration.

## What Was Changed

### Frontend Changes:
1. **Environment Configuration**: Added `.env.development` with `API_BASE_URL=http://localhost:8000`
2. **Vite Configuration**: Updated to use localhost:8000 proxy and expose `API_` environment variables
3. **Authentication Bypass**: Modified `App.tsx` to skip authentication and auto-login with mock user in development
4. **API Client**: Updated to disable JWT tokens in development mode
5. **TypeScript Support**: Added type declarations for environment variables

## Testing Instructions

### Step 1: Start Backend
```bash
# Navigate to backend directory
cd backend

# Start the backend (requires Python)
python start-backend.py
# OR
py start-backend.py
```

The backend will:
- Run on http://localhost:8000
- Use SQLite database for development
- Have CORS enabled for localhost:3000
- Have authentication disabled (DISABLE_AUTH=true)
- Display available endpoints

### Step 2: Start Frontend
```bash
# In a new terminal, navigate to web app
cd client/apps/web

# Install dependencies (if not done)
npm install
# OR
pnpm install

# Start development server
npm run dev
# OR
pnpm dev
```

The frontend will:
- Run on http://localhost:3000
- Use Vite proxy to route `/api/*` calls to backend
- Skip authentication completely in development
- Auto-login with mock user

### Step 3: Test Integration

1. **Open Application**: Visit http://localhost:3000
   - Should load directly to main dashboard (no login screen)
   - Network tab should show successful API calls

2. **Test Property Management**:
   - Go to Properties section
   - Should see property data from backend
   - Try creating/editing properties

3. **Test Client Management**:
   - Go to Clients section  
   - Should see client data from backend
   - Try creating/editing clients

4. **Verify Network Requests**:
   - Open browser DevTools → Network tab
   - API calls should go to `/api/v1/properties`, `/api/v1/clients`
   - No Authorization headers should be sent
   - All requests should return 200 status

### Expected Results:
✅ Frontend loads without login screen  
✅ Properties and clients load from backend  
✅ CRUD operations work without authentication  
✅ No CORS errors  
✅ No authorization headers in requests  

## Troubleshooting

### Backend Not Starting
- Install Python if not available
- Install dependencies: `pip install -r requirements.txt`
- Check if port 8000 is available

### Frontend Errors
- Ensure backend is running on localhost:8000
- Check that Vite dev server is on port 3000
- Verify `.env.development` file exists

### API Calls Failing
- Check browser Network tab for error details
- Verify backend endpoints are accessible
- Ensure CORS is properly configured

## Development vs Production

### Development Mode (Current Setup):
- No authentication required
- Uses Vite proxy (avoids CORS)
- Mock user auto-login
- All API calls bypass JWT checks

### Production Mode:
- Full authentication required
- Direct API calls to backend URL
- Real user login/session management
- JWT tokens required for API access

## Reverting Changes

To re-enable authentication for testing:

1. Comment out the development bypass in `App.tsx`:
```tsx
// Comment out this section:
// useEffect(() => {
//     if (import.meta.env?.DEV && !authToken) {
//         login({ ... });
//     }
// }, [login, authToken]);

// And change this:
if (!isAuthenticated) { // Remove: && !import.meta.env?.DEV
    return <LoginView />;
}
```

2. Remove the dev token bypass in `services/api.ts`:
```tsx
// Change this line:
const devToken = token; // Remove: typeof import !== 'undefined' && import.meta?.env?.DEV ? null : token;
```

## File Changes Summary

### Created:
- `client/apps/web/.env.development`
- `client/apps/web/src/vite-env.d.ts`

### Modified:
- `client/apps/web/vite.config.ts` - Added envPrefix, updated proxy
- `client/apps/web/App.tsx` - Added development auth bypass
- `client/packages/services/src/config.ts` - Added development API URL logic
- `client/packages/services/src/api.ts` - Added development token bypass

All changes are wrapped in `import.meta.env?.DEV` checks to maintain production behavior.