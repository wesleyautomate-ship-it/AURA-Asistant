# AURA Real Estate Assistant

An earlier full-stack AI real-estate application exploring voice/text workflows, task orchestration, document generation, CRM-style property and client management, and streaming AI interactions.

This repository documents an earlier stage of the architecture that later evolved into more focused orchestration and data-platform projects.

## What it demonstrates

- React + TypeScript frontend architecture
- FastAPI backend and API routing
- AI content generation and workflow orchestration
- Server-Sent Events for real-time updates
- Authentication and role-based access patterns
- PostgreSQL / SQLite application data models
- CI/CD and automated testing
- Voice/text command workflows
- Document and brochure generation
- Iterative production debugging across frontend and backend

## Architecture

```text
React / TypeScript client
          |
          v
      FastAPI API
      /    |    \
     /     |     \
 Auth   workflows   data APIs
           |
           v
      AI provider
           |
           v
 generated content / tasks / documents

PostgreSQL / SQLite + optional Redis / ChromaDB
```

## Core areas

### Command and workflow layer

The application routes user requests into real-estate workflows such as market analysis, CMA generation, marketing content, tasks and document creation.

### Streaming UI

Longer-running AI requests use Server-Sent Events so the frontend can display progress and completion state without blocking the interface.

### Product workflows

The system includes property, client and task management alongside AI-assisted features rather than treating the model as a standalone chat interface.

### Development and testing

The repository includes CI configuration, endpoint verification, E2E documentation, mock modes for development, and a long commit history showing integration and debugging work over time.

## Stack

**React · TypeScript · Vite · FastAPI · Python · PostgreSQL · Gemini · SSE · GitHub Actions**

## Running locally

```bash
python -m venv .venv
# activate the virtual environment
pip install -r backend/requirements.txt

cd aura-client
npm install
```

Copy example environment values into local ignored `.env` files and supply credentials through a secret manager or deployment environment. Never commit live keys.

## Status

This is a historical/experimental project kept public to show the evolution of the system and the engineering work behind it. Newer repositories contain the cleaner data-infrastructure and orchestration architecture.
