# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

# PropertyPro AI (Aura Real Estate Assistant) — WARP Guide

## Purpose and Scope

PropertyPro AI is a comprehensive AI-powered real estate management platform that combines intelligent automation with intuitive user interfaces to streamline property management, client interactions, and business operations. The platform features a clean architecture with FastAPI backend and is designed for mobile-first experiences with voice-centric interactions.

This guide provides comprehensive instructions for WARP agents working on the PropertyPro AI codebase, including setup, development workflows, architecture understanding, and collaboration patterns between multiple agents.

## Rule Precedence and Agent Collaboration Standards

**CRITICAL Rule Precedence** (in ascending order of priority):
- Personal WARP rules (lowest precedence)  
- Project root WARP.md (this file)
- Subdirectory WARP.md files (highest precedence)

When multiple WARP agents operate in parallel:
- Each agent works on separate branches or feature directories
- Communication occurs via `docs/changelogs/` with timestamped entries
- Agents must read existing changelogs before making changes
- File ownership conflicts are avoided by declaring intent in changelogs first

## Quick Start

### Prerequisites
- **Python 3.11+** - Core backend runtime
- **Node.js 18+** - Frontend tooling (when building React components)
- **PostgreSQL 14+** - Primary database
- **Docker & Docker Compose** - Containerized development
- **PowerShell 5.1+** - Primary shell on Windows

### Fastest Path to Running System

1. **Environment Setup**
   ```powershell
   # Clone and navigate
   git clone <repository-url>
   cd Realtor-assistant

   # Copy environment template  
   copy env.example .env
   # Edit .env with your database credentials and API keys
   ```

2. **Docker Development (Recommended)**
   ```powershell
   # Start core services
   make dev
   # OR manually:
   docker-compose up -d db redis chromadb

   # Wait for services, then start API
   make run-api
   ```

3. **Verify Setup**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Database available on localhost:5432

## Common Development Commands

### Environment Management
```powershell
# Setup Python virtual environment
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt

# Setup with Make (Unix-style commands)
make install           # Full environment setup
make quick-start      # New developer setup
```

### Running Services

#### Backend API
```powershell
# Development server (hot reload)
make run-api
# OR directly:
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

#### Docker Services
```powershell
# Start all services
make up                # docker-compose up -d
make dev               # Start dev environment (DB, Redis, ChromaDB)
make down              # Stop all services
make restart           # Restart all services
make logs              # View all logs
make logs-api          # API logs only
```

### Database Operations
```powershell
# Run migrations
cd backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Database shell
make db-shell

# Reset database (WARNING: destroys data)
make db-reset
```

### Testing
```powershell
# Run all tests
make test
pytest backend/app/tests/ -v

# Backend tests only
make test-backend
pytest backend/app/tests/ -v

# Integration tests
make test-integration

# Performance tests  
pytest -m performance
```

### Code Quality
```powershell
# Format code
make format
black backend/
isort backend/

# Lint code
make lint
flake8 backend/

# Combined quality check
make lint
```

### Utilities
```powershell
# Health check all services
make health

# Show service status
make status

# Clean up Docker resources
make clean

# View logs for specific service
docker-compose logs -f api
docker-compose logs -f worker
```

## High-level Architecture Overview

### System Components

```
┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │
│   React 19 Frontend │◄──►│   FastAPI Backend   │
│   (To Be Rebuilt)   │    │   (Production Ready)│
│                     │    │                     │
└─────────────────────┘    └─────────────────────┘
                           │
                           ▼
                    ┌─────────────────────┐
                    │                     │
                    │  AI Orchestration   │
                    │    & Workflows      │
                    │                     │
                    └─────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ PostgreSQL  │ │   ChromaDB  │ │    Redis    │
    │  Database   │ │ Vector Store│ │ Cache/Queue │
    └─────────────┘ └─────────────┘ └─────────────┘
```

### Clean Architecture Structure
The backend follows clean architecture principles:

- **`backend/app/api/`** - REST API endpoints and routers  
- **`backend/app/domain/`** - Business logic and domain models
- **`backend/app/infrastructure/`** - External integrations (DB, AI services, queue)
- **`backend/app/core/`** - Cross-cutting concerns (auth, settings, middleware)
- **`backend/app/services/`** - Application services and use cases

### Services and Ports

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| API | 8000 | http://localhost:8000 | Main FastAPI application |
| Database | 5432 | localhost:5432 | PostgreSQL database |
| Redis | 6379 | localhost:6379 | Caching and message broker |
| ChromaDB | 8002 | http://localhost:8002 | Vector database for AI/RAG |
| Frontend | 3000 | http://localhost:3000 | React application (when built) |

### Key Features by Domain

#### AI & Machine Learning
- **RAG Service**: Enhanced retrieval-augmented generation
- **AI Manager**: LLM orchestration and workflow management  
- **Action Engine**: AI-powered task automation
- **Content Generation**: Marketing materials, reports, social media
- **Property Detection**: Automated property information extraction

#### Real Estate Operations  
- **Property Management**: CRUD operations, valuation, analytics
- **Client Management**: CRM functionality, nurturing campaigns
- **Transaction Processing**: Deal pipeline, document generation
- **Marketing Automation**: Campaign creation, social media scheduling
- **CMA Reports**: Comparative market analysis generation

#### System Infrastructure
- **Authentication**: JWT-based with role-based access control
- **Background Jobs**: Celery-based task queue
- **Monitoring**: Performance metrics and health checks
- **File Processing**: Document upload, parsing, analysis

## Configuration and Environment Variables

### Required Environment Variables

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | None | postgresql://admin:password123@localhost/real_estate_db |
| `REDIS_URL` | Redis connection string | Yes | None | redis://:password@localhost:6379/0 |
| `SECRET_KEY` | JWT signing secret | Yes | None | your-secret-key-here |
| `OPENAI_API_KEY` | OpenAI API key for AI features | Yes* | None | sk-... |
| `GOOGLE_API_KEY` | Google Generative AI key | No | None | AI... |

*Required for AI features

### Optional Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiry | 30 | 60 |
| `DEBUG` | Enable debug mode | false | true |
| `DISABLE_AUTH` | Disable auth for dev | false | true |
| `CHROMA_HOST` | ChromaDB host | chromadb | localhost |
| `CHROMA_PORT` | ChromaDB port | 8000 | 8002 |

### Environment File Setup
```powershell
# Copy template
copy env.example .env

# Required for AI features:
# OPENAI_API_KEY=sk-your-key-here
# GOOGLE_API_KEY=AIza-your-key-here

# Development settings:
# DEBUG=true
# DISABLE_AUTH=true  # For development without authentication
```

## Database, Migrations, and Seeding

### Alembic Migration Commands
```powershell
cd backend

# Initialize database to latest schema
alembic upgrade head

# Create new migration after model changes  
alembic revision --autogenerate -m "Add new feature"

# Downgrade to specific revision
alembic downgrade <revision_id>

# View migration history
alembic history

# View current revision
alembic current
```

### Database Seeding
```powershell
# Seed with sample data
make seed

# Seed demo properties specifically  
make seed-properties
```

### Database Management
```powershell
# Open database shell
make db-shell
# OR
docker-compose exec db psql -U admin -d real_estate_db

# Backup database
make backup

# Restore from backup
make restore BACKUP_FILE=backups/backup_20231201_120000.sql
```

## Vector Store and AI Integration

### ChromaDB Configuration
- **Host**: localhost:8002 (development)  
- **Purpose**: Vector embeddings for RAG (Retrieval-Augmented Generation)
- **Collections**: Property listings, client data, documents

### AI Service Integration
The platform integrates multiple AI providers:
- **OpenAI**: Primary LLM for content generation
- **Google Generative AI**: Alternative LLM provider
- **ChromaDB**: Vector similarity search
- **Embedding Models**: Text-to-vector conversion

### RAG Workflow
1. **Document Ingestion**: PDFs, DOCX files processed and chunked
2. **Embedding Generation**: Text chunks converted to vectors  
3. **Vector Storage**: Stored in ChromaDB with metadata
4. **Query Processing**: User queries embedded and matched
5. **Context Retrieval**: Relevant chunks retrieved for LLM context
6. **Response Generation**: LLM generates response with retrieved context

## Testing Strategy

### Test Structure
```
tests/
├── unit/           # Isolated component tests
├── integration/    # Multi-component interaction tests  
├── e2e/           # End-to-end workflow tests
├── performance/   # Load and performance tests
└── contracts/     # API contract tests
```

### Running Tests
```powershell
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests  
pytest tests/integration/

# Performance tests
pytest -m performance

# With coverage
pytest --cov=backend/app --cov-report=html
```

### Test Configuration
- **pytest.ini**: Test configuration and markers
- **conftest.py**: Shared fixtures and test setup
- **Test markers**: `@pytest.mark.performance` for perf tests

## Docker Development Workflow

### Service Dependencies
```yaml
# Core services for development
db:          # PostgreSQL database
redis:       # Caching and queues  
chromadb:    # Vector database
api:         # FastAPI backend
worker:      # Celery background worker
scheduler:   # Celery beat scheduler
```

### Docker Commands
```powershell
# Build images
docker-compose build --no-cache

# Start core services only  
docker-compose up -d db redis chromadb

# Start full stack
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f api

# Execute commands in containers
docker-compose exec api bash
docker-compose exec db psql -U admin -d real_estate_db
```

### Health Checks
All services include health checks:
```powershell
# Check service health
make health

# Manual health check
curl http://localhost:8000/health
```

## Code Quality and Standards

### Python Code Standards
- **Formatter**: Black with 88 character line length
- **Import Sorting**: isort with Black compatibility  
- **Linting**: Flake8 with custom configuration
- **Type Hints**: Encouraged for all new code

### Code Quality Commands
```powershell
# Format all Python code
black backend/
isort backend/

# Lint code
flake8 backend/

# Combined formatting and linting
make format
make lint
```

### Pre-commit Hooks (if used)
```powershell
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Warp Agent Workflows

### Parallel Agent Coordination

When multiple WARP agents work simultaneously on this codebase:

#### Changelog Protocol
1. **Before starting work**: Create entry in `docs/changelogs/{branch}-{timestamp}.md`
2. **Required changelog fields**:
   ```markdown
   # Changelog: {branch-name} - {date}
   
   **Agent ID**: {agent-identifier}
   **Context**: Brief description of the task
   **Intent**: What you plan to accomplish  
   **Files to Touch**: List of files you plan to modify
   **Dependencies**: Other agents or services you depend on
   **Constraints**: Any limitations or requirements
   **Status**: started | in_progress | blocked | completed
   **Handoffs**: Any work passed to other agents
   ```

3. **During work**: Update status and note any blockers
4. **Upon completion**: Mark as completed and note deliverables

#### File Ownership Protocol
- Declare intent to modify files in changelog BEFORE editing
- If conflict detected, coordinate via changelog comments
- Use feature branches for significant changes
- Prefer smaller, focused changes over large modifications

#### Agent Role Specialization
- **Backend Agent**: API endpoints, business logic, database
- **Frontend Agent**: UI components, user experience  
- **Infrastructure Agent**: Docker, deployments, CI/CD
- **Documentation Agent**: Documentation, guides, specs
- **QA Agent**: Testing, quality assurance, performance

### Dependency Awareness

Before making changes, agents MUST review:
1. This WARP.md file (current section)
2. Existing changelogs in `docs/changelogs/`
3. Current environment variables and configuration
4. Recent commit history for context

### Communication Examples

**Starting Work Example:**
```markdown
# Changelog: feature/add-property-valuation - 2024-01-15

**Agent ID**: backend-agent-001
**Context**: Implementing automated property valuation API
**Intent**: Add new endpoint `/api/v1/properties/{id}/valuation` with ML model integration
**Files to Touch**: 
- backend/app/api/v1/property_management.py
- backend/app/services/property_valuation.py  
- backend/app/tests/test_property_valuation.py
**Dependencies**: None identified
**Constraints**: Must maintain existing API compatibility
**Status**: started
```

**Handoff Example:**  
```markdown
**Status**: completed
**Handoffs**: 
- Frontend Agent: New valuation endpoint available at `/api/v1/properties/{id}/valuation`
- QA Agent: Unit tests added, please add integration tests
- Docs Agent: API endpoint needs documentation in OpenAPI schema
```

## Troubleshooting and FAQs

### Common Issues

#### Database Connection Errors
```powershell
# Check if PostgreSQL is running
docker-compose ps db

# Check logs
docker-compose logs db

# Reset database connection
docker-compose restart db
```

#### AI Features Not Working
```powershell
# Verify API keys are set
echo $OPENAI_API_KEY

# Check if AI features are enabled
curl http://localhost:8000/health
```

#### Port Conflicts
```powershell  
# Check what's using port 8000
netstat -tulpn | grep 8000

# Kill process on port
taskkill /F /PID <process_id>
```

#### ChromaDB Connection Issues
```powershell
# Restart ChromaDB
docker-compose restart chromadb

# Check ChromaDB health
curl http://localhost:8002/api/v2
```

### Performance Issues

#### Slow Database Queries
1. Check database indexes
2. Review query patterns in logs
3. Consider connection pooling
4. Monitor with `make monitor`

#### Memory Usage
1. Check container resource usage: `docker stats`
2. Review memory-intensive operations
3. Consider Redis cache optimization

### Development Environment Issues

#### Python Dependencies
```powershell
# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall

# Clear Python cache
python -m pip cache purge
```

#### Docker Issues
```powershell
# Clean Docker system
make clean

# Rebuild images
docker-compose build --no-cache
```

## Maintenance and Upgrades

### Regular Maintenance Tasks

#### Weekly
- Review and update dependencies
- Check for security vulnerabilities  
- Review error logs and performance metrics
- Update documentation as needed

#### Monthly  
- Database performance review
- Backup verification
- Security audit of environment variables
- Review and clean up old Docker images

### Dependency Updates
```powershell
# Check outdated Python packages
pip list --outdated

# Update packages
pip install -U package_name

# Update all packages (carefully)
pip install -U -r backend/requirements.txt
```

### Database Maintenance
```powershell
# Database backup
make backup

# Analyze database performance
make db-shell
# Then run ANALYZE; in psql

# Vacuum database  
make db-shell  
# Then run VACUUM ANALYZE; in psql
```

---

**Note for WARP Agents**: Always validate your understanding of the codebase by running health checks and examining recent commits before making significant changes. When in doubt, create a changelog entry asking for clarification from other agents or team members.