# Aura Real Estate Assistant

**AI-Powered Real Estate Command Center**

Aura is a modern real estate management platform that combines intelligent automation with intuitive user interfaces to streamline property management, client interactions, and business operations.

## 🏗️ Architecture Overview

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
```

### Current Status
- ✅ **Backend**: FastAPI-based REST API with authentication, data models, and AI workflow orchestration
- 🔄 **Frontend**: Clean slate - ready for React 19 rebuild
- 📊 **Database**: PostgreSQL with comprehensive data models
- 🤖 **AI**: Integration-ready workflow engine and content generation

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup
1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd Realtor-assistant
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your database and API keys
   ```

4. **Initialize database:**
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Run development server:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at `http://localhost:8000`
   
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

### Environment Configuration

Key environment variables in `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://username:password@localhost/aura_db

# Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Development
DISABLE_AUTH=false  # Set to true for development without auth
DEBUG=true

# AI Services (Optional)
OPENAI_API_KEY=your-openai-key
```

## 📋 Development Roadmap

### Phase 1: Frontend Foundation (Current)
- [ ] Set up React 19 project with Vite
- [ ] Implement modern UI component library
- [ ] Create responsive layout system
- [ ] Establish state management architecture

### Phase 2: Core Features
- [ ] Authentication flow
- [ ] Dashboard with real-time data
- [ ] Property management interface
- [ ] Client management system

### Phase 3: AI Integration
- [ ] Command center interface
- [ ] Workflow automation UI
- [ ] Content generation tools
- [ ] Analytics and reporting

### Phase 4: Advanced Features
- [ ] Mobile optimization
- [ ] Offline capabilities
- [ ] Advanced integrations
- [ ] Performance optimization

## 🏃‍♂️ Available Scripts

### Backend
```bash
# Run development server
python -m uvicorn app.main:app --reload

# Run tests
pytest

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Code formatting
black .
isort .
```

## 📊 API Endpoints

The backend provides a comprehensive REST API:

- **Authentication**: `/api/v1/auth/*`
- **Properties**: `/api/v1/properties/*`
- **Clients**: `/api/v1/clients/*`
- **Tasks**: `/api/v1/tasks/*`
- **AI Requests**: `/api/v1/ai-requests/*`
- **Workflows**: `/api/v1/workflows/*`

Full API documentation is available at `/docs` when running the development server.

## 🔧 Technology Stack

### Backend
- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with custom user management
- **Testing**: pytest with async support
- **Documentation**: Automatic OpenAPI/Swagger

### Frontend (Planned)
- **Framework**: React 19 with concurrent features
- **Build Tool**: Vite for fast development
- **Styling**: Tailwind CSS for utility-first design
- **State Management**: Zustand for simple state management
- **HTTP Client**: Fetch API with custom hooks

## 📁 Project Structure

```
aura-real-estate-assistant/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Database models
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   └── tests/             # Backend tests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── README.md             # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions and support, please reach out through the project's issue tracker.

---

**Ready to build the future of real estate management? Let's get started! 🏠✨**