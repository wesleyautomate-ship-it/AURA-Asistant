# Services Setup Guide

This guide explains how to set up and wire all external services for the RealtorProAI AURA backend.

## Status Summary

✅ **Gemini API** - Configured and ready  
🟡 **Redis** - Configured but not running  
🟡 **ChromaDB** - Configured but not running  
🟡 **PostgreSQL** - Optional (using SQLite in development)

---

## 1. Gemini API (✅ READY)

### Current Configuration

The Gemini API key is already configured in your `.env` file:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyAVHIS69nuR4NSbm39PMvI3XDhQwQlHn5A
GEMINI_MODEL=gemini-1.5-pro
GEMINI_STT=true
```

**Status**: ✅ **Ready to use!** The backend will use real Gemini AI for content generation.

### Verify It's Working

Start the backend and test the intelligence endpoint:

```powershell
# Start backend
python scripts/start_backend_safe.py

# Test in another terminal
curl http://localhost:8000/api/v1/intelligence/mock-prompts
```

If you need a new API key:
1. Visit: https://makersuite.google.com/app/apikey
2. Create/copy your API key
3. Update `GEMINI_API_KEY` in `.env`

---

## 2. Redis (🟡 NEEDS SETUP)

### Why Redis?

Redis is used for:
- Caching AI responses
- Session storage
- Background task queue (Celery)

### Current Configuration

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis123
REDIS_URL=redis://:redis123@localhost:6379/0
```

### Setup Options

#### Option A: Docker (Recommended)

```powershell
# Start Redis via Docker
docker run -d `
  --name redis `
  -p 6379:6379 `
  redis:latest redis-server --requirepass redis123

# Verify it's running
docker ps | Select-String redis
```

#### Option B: Docker Compose (Full Stack)

```powershell
# Start Redis along with other services
docker-compose up -d redis

# Check logs
docker-compose logs -f redis
```

#### Option C: Windows Install (Not Recommended)

Redis doesn't officially support Windows. Use Docker or WSL2.

### Verify Redis Connection

```powershell
# Test Redis connection
curl http://localhost:8000/health

# Or use redis-cli (if installed)
docker exec -it redis redis-cli -a redis123 ping
# Expected output: PONG
```

### What Happens Without Redis?

The backend will work but:
- ❌ No caching (slower responses)
- ❌ No background tasks
- ⚠️ Warning logs at startup

---

## 3. ChromaDB (🟡 NEEDS SETUP)

### Why ChromaDB?

ChromaDB is used for:
- RAG (Retrieval-Augmented Generation)
- Vector similarity search
- Knowledge base storage

### Current Configuration

```env
CHROMA_HOST=localhost
CHROMA_PORT=8002
```

### Setup Options

#### Option A: Docker (Recommended)

```powershell
# Start ChromaDB via Docker
docker run -d `
  --name chromadb `
  -p 8002:8000 `
  -v chroma-data:/chroma/chroma `
  chromadb/chroma:latest

# Verify it's running
curl http://localhost:8002/api/v1/heartbeat
```

#### Option B: Docker Compose

```powershell
# Start ChromaDB with other services
docker-compose up -d chromadb

# Check logs
docker-compose logs -f chromadb
```

#### Option C: Python Install (Local Development)

```powershell
# Install ChromaDB locally
.venv\Scripts\pip.exe install chromadb

# Start ChromaDB server
.venv\Scripts\python.exe -m chromadb.server --host localhost --port 8002
```

### Verify ChromaDB Connection

```powershell
# Test ChromaDB health
curl http://localhost:8002/api/v1/heartbeat

# Expected output: {"nanosecond heartbeat": ...}
```

### What Happens Without ChromaDB?

The backend will start but:
- ❌ No RAG functionality
- ❌ No intelligent property search
- ⚠️ Warning: "Running without ChromaDB in development mode"

---

## 4. PostgreSQL (Optional)

### Current Configuration

Development uses SQLite by default:

```env
DATABASE_URL=sqlite:///./aura_dev.db
```

For production, switch to PostgreSQL:

```env
DATABASE_URL=postgresql://admin:password123@localhost:5432/real_estate_db
```

### Setup PostgreSQL (Production Only)

```powershell
# Start PostgreSQL via Docker
docker-compose up -d db

# Run migrations
docker-compose exec api python -m alembic upgrade head
```

---

## Quick Start: All Services at Once

### Using Docker Compose (Recommended)

```powershell
# Start all services (Redis, ChromaDB, PostgreSQL)
docker-compose up -d redis chromadb

# Wait for services to be ready
timeout /t 10

# Start backend
python scripts/start_backend_safe.py
```

### Verify All Services

```powershell
# Check Redis
docker exec -it redis redis-cli -a redis123 ping

# Check ChromaDB
curl http://localhost:8002/api/v1/heartbeat

# Check Backend
curl http://localhost:8000/health
```

---

## Environment Variables Quick Reference

### Required for Production

```env
# AI
GEMINI_API_KEY=your_actual_key_here
GEMINI_MODEL=gemini-1.5-pro

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8002
```

### Development (Current Setup)

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyAVHIS69nuR4NSbm39PMvI3XDhQwQlHn5A
DATABASE_URL=sqlite:///./aura_dev.db
REDIS_URL=redis://localhost:6379
CHROMA_HOST=localhost
CHROMA_PORT=8002
DISABLE_AUTH=true
DEBUG=true
```

---

## Troubleshooting

### Backend Won't Start

```powershell
# Use the safe startup script
python scripts/start_backend_safe.py

# This will:
# 1. Validate Python environment
# 2. Check dependencies
# 3. Show helpful error messages
```

### Redis Connection Failed

```powershell
# Check if Redis is running
docker ps | Select-String redis

# If not running, start it
docker start redis

# Or recreate it
docker run -d --name redis -p 6379:6379 redis:latest
```

### ChromaDB Connection Failed

```powershell
# Check if ChromaDB is running
curl http://localhost:8002/api/v1/heartbeat

# If not running, start it
docker start chromadb

# Or recreate it
docker run -d --name chromadb -p 8002:8000 chromadb/chroma:latest
```

### Port Already in Use

```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Restart backend
python scripts/start_backend_safe.py
```

---

## Next Steps

1. ✅ **Gemini API** is already working - test content generation
2. 🚀 **Start Redis**: `docker run -d --name redis -p 6379:6379 redis:latest`
3. 🚀 **Start ChromaDB**: `docker run -d --name chromadb -p 8002:8000 chromadb/chroma:latest`
4. ✅ **Test backend**: `python scripts/start_backend_safe.py`
5. 🎉 **Try the chat**: http://localhost:3000/chat/console

---

## Service Status Dashboard

| Service | Status | Port | Container | Required |
|---------|--------|------|-----------|----------|
| Backend | ✅ Running | 8000 | - | ✅ Yes |
| Gemini AI | ✅ Configured | - | - | ✅ Yes |
| Redis | 🟡 Not Running | 6379 | redis | 🟡 Optional |
| ChromaDB | 🟡 Not Running | 8002 | chromadb | 🟡 Optional |
| PostgreSQL | ⚪ Not Used | 5432 | db | ⚪ Optional |
| Frontend | ✅ Running | 3000 | - | ✅ Yes |

**Legend:**
- ✅ = Working
- 🟡 = Configured but not running (optional)
- ⚪ = Not needed in development
- ❌ = Problem

---

## Contact & Support

If you encounter issues:

1. Check backend logs
2. Use `python scripts/start_backend_safe.py` to validate environment
3. Verify services are running: `docker ps`
4. Check `.env` configuration
5. Review backend startup logs for specific errors

**The backend will work without Redis and ChromaDB, but with limited functionality.**
