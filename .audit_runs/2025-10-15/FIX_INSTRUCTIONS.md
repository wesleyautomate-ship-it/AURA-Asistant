# 🔧 Fix Instructions: Router Loading Issue

## Problem Identified
The backend is running with **global Python** instead of the **virtual environment**, causing all routers to fail importing due to missing dependencies (specifically SQLAlchemy).

## Evidence
```
Current Backend Process (PID 23768):
  Python: C:\Python314\python.exe (GLOBAL)
  SQLAlchemy: ❌ NOT INSTALLED

Virtual Environment (.venv):
  Python: C:\Dev\RealtorProAI\Realtor-assistant\.venv\Scripts\python.exe
  SQLAlchemy: ✅ INSTALLED (1.4.46)
```

## Solution Steps

### Step 1: Stop Current Backend
Stop the currently running backend process (PID 23768).

**Option A - Kill from PowerShell:**
```powershell
Stop-Process -Id 23768 -Force
```

**Option B - Find and close the terminal window** running uvicorn

---

### Step 2: Activate Virtual Environment
```powershell
cd C:\Dev\RealtorProAI\Realtor-assistant
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` prefix in your prompt.

---

### Step 3: Start Backend with Correct Python
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**OR** use the venv Python directly:
```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

---

### Step 4: Verify All Routers Load
Watch the console output - you should see messages like:
```
INFO:     Intelligence router loaded
INFO:     Chat sessions router loaded
INFO:     CMA reports router loaded
INFO:     Social media router loaded
... (40+ routers)
```

**No more warnings like**: `"Intelligence router not loaded: <error>"`

---

### Step 5: Test Router Registration
```powershell
# From a NEW PowerShell window:
curl.exe -s "http://localhost:8000/openapi.json" | ConvertFrom-Json | Select-Object -ExpandProperty paths | Get-Member -MemberType NoteProperty | Measure-Object
```

**Expected Result**: Should show **100+ endpoints** instead of just 2

---

### Step 6: Test Intelligence Endpoint
```powershell
curl.exe -X POST "http://localhost:8000/api/v1/intelligence/transcribe" `
  -H "Content-Type: application/json" `
  -d '{\"use_mock\": true}'
```

**Expected Result**: HTTP 200 with mock transcription response

---

### Step 7: Test Chat Endpoint (SSE)
```powershell
# This will stream - press Ctrl+C to stop
curl.exe -N -H "Accept: text/event-stream" `
  -H "Content-Type: application/json" `
  -X POST "http://localhost:8000/api/v1/intelligence/chat" `
  -d '{\"thread_id\": null, \"message\": \"Hello AURA\"}'
```

**Expected Result**: SSE stream with events like:
```
event: thinking
data: {...}

event: message
data: {...}

event: final
data: {...}
```

---

## Verification Checklist

After restart, verify:
- [ ] Backend starts without "router not loaded" warnings
- [ ] `/docs` endpoint shows 100+ API endpoints
- [ ] `/api/v1/intelligence/transcribe` returns 200
- [ ] `/api/v1/intelligence/chat` streams SSE events
- [ ] Frontend chat console can connect to backend
- [ ] No 404 errors when testing endpoints

---

## Alternative: Install SQLAlchemy Globally (NOT RECOMMENDED)
If you prefer not to use venv (not recommended):
```powershell
pip install sqlalchemy==1.4.46
pip install -r backend/requirements.txt
```

Then restart the current backend.

---

## Prevention: Always Use Virtual Environment

**Create a startup script** (`start-backend.ps1`):
```powershell
# Navigate to project
cd C:\Dev\RealtorProAI\Realtor-assistant

# Activate venv
.\.venv\Scripts\Activate.ps1

# Start backend
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Usage:**
```powershell
.\start-backend.ps1
```

---

## Expected Outcome After Fix

### Before Fix:
- 🔴 2 endpoints registered (/, /health)
- 🔴 40 routers = dead code
- 🔴 Chat feature: 404 Not Found
- 🔴 Content generation: 404 Not Found

### After Fix:
- ✅ 100+ endpoints registered
- ✅ All 40 routers working
- ✅ Chat feature: SSE streaming functional
- ✅ Content generation: endpoints accessible
- ✅ Mock mode: 5 test prompts working
- 🟡 AI generation: Still mocked (needs Gemini API config)

---

## Next Steps After Fix

Once routers are loading:
1. ✅ Test chat console UI: http://localhost:3000/chat/console
2. ✅ Test content generation endpoints
3. 🟡 Configure Google Gemini API for real AI
4. 🟡 Populate ChromaDB for RAG functionality
5. 🟡 Complete frontend authentication integration

---

**Estimated Time to Fix**: 5 minutes
**Risk Level**: Zero - just restarting with correct Python
**Impact**: Unlocks 95% of system functionality immediately
