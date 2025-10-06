# PropertyPro AI - Complete Setup Guide

This guide will help you set up and run the PropertyPro AI application with real task management functionality.

## 🏗️ Architecture Overview

The application consists of:
- **Backend**: FastAPI server with task management endpoints
- **Frontend**: React app with real-time task management via Zustand stores
- **Database**: SQLAlchemy with in-memory storage (can be extended to PostgreSQL)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm/yarn
- Git

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python app/main.py
```

The backend will be available at `http://localhost:8000`

**API Documentation**: Visit `http://localhost:8000/docs` for interactive API docs

### 2. Frontend Setup

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start the frontend development server
cd apps/web
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# Database (optional - defaults to in-memory)
DATABASE_URL=sqlite:///./app.db

# JWT Secret for authentication
JWT_SECRET=your-secret-key-here

# API Keys (optional)
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-api-key
```

#### Frontend (.env.local)
```env
# API Base URL
VITE_API_BASE_URL=http://localhost:8000

# Feature Flags
VITE_REAL_TASKS=true
```

## ✨ Task Management Features

### What's New
- **Real API Integration**: Tasks are now stored and managed via backend API
- **CRUD Operations**: Create, read, update, delete tasks
- **Priority Management**: Low, Medium, High, Urgent priorities
- **Due Date Tracking**: With overdue detection
- **Task Assignment**: Assign tasks to users
- **Drag & Drop Reordering**: Reorder tasks by priority
- **Real-time Updates**: Optimistic updates with error rollback
- **Search & Filtering**: Filter by status, priority, assignee, etc.

### API Endpoints

#### Tasks API (`/api/v1/tasks`)
- `GET /api/v1/tasks` - List tasks with filtering
- `POST /api/v1/tasks` - Create new task  
- `GET /api/v1/tasks/{id}` - Get specific task
- `PATCH /api/v1/tasks/{id}` - Update task
- `PATCH /api/v1/tasks/{id}/complete` - Toggle completion
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/reorder` - Reorder tasks
- `POST /api/v1/tasks/{id}/assign` - Assign task to user
- `DELETE /api/v1/tasks/{id}/assign/{user_id}` - Unassign task

#### Query Parameters for Filtering
- `status`: open, in_progress, completed, archived
- `priority`: low, medium, high, urgent
- `assigned_to`: User ID
- `property_id`: Property ID
- `client_id`: Client ID
- `q`: Search query
- `sort`: Field to sort by (due_date, priority, created_at, etc.)
- `order`: asc or desc
- `page`: Page number
- `page_size`: Items per page

## 🎯 Usage Examples

### Creating a Task

```typescript
import { taskService } from '@propertypro/services';

const newTask = await taskService.createTask({
  title: 'Follow up with client',
  description: 'Call John about the Marina listing',
  due_date: '2025-10-15',
  priority: 'high',
  property_id: 'prop-123'
});
```

### Using the Task Store

```typescript
import { useTaskStore } from '@propertypro/store';

function TaskComponent() {
  const tasks = useTaskStore(selectTasks);
  const { fetchTasks, createTask, updateTask } = useTaskStore();
  
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);
  
  // Component logic...
}
```

## 🛠️ Development

### Project Structure
```
backend/
├── app/
│   ├── api/v1/tasks_router.py    # Task management endpoints
│   ├── main.py                   # FastAPI application
│   └── ...
client/
├── packages/
│   ├── services/src/taskService.ts  # API client
│   └── store/src/taskStore.ts       # Zustand store
├── apps/web/src/components/
│   ├── TasksView.tsx                # Main tasks view
│   └── TaskItem.tsx                 # Individual task component
```

### Key Technologies
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React, TypeScript, Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Fetch API with custom wrapper

### Adding New Features

1. **Backend**: Add endpoints to `tasks_router.py`
2. **Service**: Update `taskService.ts` with new methods
3. **Store**: Add actions to `taskStore.ts`
4. **Components**: Update UI components as needed

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd client
npm run test
```

### Manual Testing
1. Start both backend and frontend
2. Navigate to Tasks view
3. Create, edit, complete, and delete tasks
4. Test filtering and search
5. Verify drag & drop reordering

## 🚨 Troubleshooting

### Common Issues

#### Backend not starting
- Check Python version: `python --version`
- Ensure virtual environment is activated
- Install missing dependencies: `pip install -r requirements.txt`

#### Frontend not connecting to backend
- Verify backend is running on `http://localhost:8000`
- Check CORS settings in backend
- Ensure API_BASE_URL is configured correctly

#### Tasks not loading
- Check browser developer console for errors
- Verify authentication token is valid
- Check network tab for API request/response

#### Database issues
- For development, the app uses in-memory storage
- Data will be lost when backend restarts
- For persistence, configure DATABASE_URL environment variable

### Debug Mode
Add `DEBUG=true` to backend `.env` for verbose logging.

## 📈 Performance Considerations

- **Pagination**: Tasks are paginated (default 50 per page)
- **Caching**: Store implements client-side caching
- **Optimistic Updates**: UI updates immediately, rolls back on error
- **Debounced Search**: Search queries are debounced to reduce API calls

## 🔒 Security

- JWT token authentication (when configured)
- User-scoped data access (users only see their tasks)
- Input validation on all endpoints
- CORS protection

## 🚀 Deployment

### Production Backend
```bash
# Using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Or using Docker
docker build -t propertyproai-backend .
docker run -p 8000:8000 propertyproai-backend
```

### Production Frontend
```bash
# Build for production
npm run build

# Serve static files
npm run preview
```

## 📞 Support

For issues or questions:
1. Check this guide first
2. Look at the API documentation at `/docs`
3. Check the browser console and network tabs
4. Review backend logs for errors

## 🎉 Next Steps

After setup, you can:
1. Create your first task
2. Test drag & drop reordering
3. Try filtering and search
4. Explore API docs for advanced features
5. Extend with custom task types or fields

The task management system is now fully functional with real backend integration!