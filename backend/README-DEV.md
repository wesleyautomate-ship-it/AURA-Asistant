# PropertyPro AI Backend - Development Setup

## 🚀 Quick Start

Get the PropertyPro AI backend running in development mode with a single command:

```powershell
# From the backend directory
python start-backend.py
```

The server will be available at **http://localhost:8000** with authentication disabled for development.

## 📋 Prerequisites

- **Python 3.8+**
- **Windows PowerShell** (for environment setup)
- **Git** (for version control)

## 🛠️ Development Setup

### 1. Clone and Navigate

```powershell
cd C:\Dev\RealtorProAI\Realtor-assistant\backend
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Start Development Server

```powershell
python start-backend.py
```

That's it! The script will:
- ✅ Configure development environment variables
- ✅ Initialize SQLite database
- ✅ Seed sample data (users, properties, clients)
- ✅ Start the server with CORS enabled
- ✅ Disable authentication for easy testing

## 🎯 Key Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `GET /health` | Health check | `curl http://localhost:8000/health` |
| `GET /docs` | Interactive API documentation | Open in browser |
| `POST /api/v1/auth/login` | Login (bypassed in dev) | Returns mock token |
| `GET /api/v1/properties` | List all properties | Returns property list |
| `GET /api/v1/clients` | List all clients | Returns client list |
| `GET /api/v1/command-center` | Dashboard metrics | Returns aggregated data |

## 🔐 Development Authentication

Authentication is **disabled** in development mode for easier testing:

- **Username**: `admin@propertypro.ai`
- **Password**: `Admin123!`
- **Login Response**: Always returns a development token

All API endpoints can be accessed without authentication headers.

## 🗄️ Database

The development setup uses **SQLite** for simplicity:

- **Database File**: `propertypro_dev.db` (created automatically)
- **Location**: Backend root directory
- **Sample Data**: Automatically seeded on first run

### Sample Data Includes:
- **3 Users**: Admin, Agent, Manager
- **5 Properties**: Various types and locations in Dubai
- **5 Clients**: Different buyer/seller profiles

## 🧪 Testing Endpoints

Run the comprehensive test suite:

```powershell
python test_endpoints.py
```

This tests all critical endpoints and provides detailed feedback.

### Manual Testing with curl:

```powershell
# Health check
curl http://localhost:8000/health

# Login (development bypass)
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"username\":\"admin@propertypro.ai\",\"password\":\"Admin123!\"}"

# List properties
curl http://localhost:8000/api/v1/properties

# List clients  
curl http://localhost:8000/api/v1/clients

# Command center dashboard
curl http://localhost:8000/api/v1/command-center
```

## 🔧 Configuration

### Environment Variables

The startup script sets these automatically:

```bash
APP_ENV=development
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./propertypro_dev.db
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
DISABLE_AUTH=true
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Custom Configuration

Create `.env.development` to override defaults:

```bash
# Custom port
PORT=8080

# Enable authentication
DISABLE_AUTH=false

# Different database
DATABASE_URL=postgresql://user:pass@localhost:5432/propdb
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/v1/           # API route handlers
│   ├── core/             # Core functionality (auth, db, settings)
│   ├── domain/           # Business logic and models
│   ├── services/         # Business services
│   └── main.py           # FastAPI application
├── start-backend.py      # Development startup script
├── test_endpoints.py     # Endpoint testing script
├── requirements.txt      # Python dependencies
├── .env.development      # Development configuration
└── propertypro_dev.db    # SQLite database (auto-created)
```

## 🌐 CORS Configuration

The server is configured to accept requests from:
- `http://localhost:3000` (main frontend)
- `http://localhost:3001` (alternative frontend port)

Additional origins can be added via the `CORS_ORIGINS` environment variable.

## 🔍 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Find and kill process using port 8000
netstat -ano | findstr :8000
Stop-Process -Id <PID>
```

### Import Errors
```powershell
# Ensure you're in the backend directory
cd C:\Dev\RealtorProAI\Realtor-assistant\backend
python start-backend.py
```

### Database Issues
```powershell
# Delete database to reset
Remove-Item propertypro_dev.db
python start-backend.py
```

### PowerShell Execution Policy
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 📊 Sample Data Details

### Users
- **admin@propertypro.ai**: Admin user with full access
- **agent@propertypro.ai**: Real estate agent
- **manager@propertypro.ai**: Property manager

### Properties
- Luxury Downtown Apartment (850K AED)
- Spacious Family Villa (2.4M AED)
- Beachfront Studio (650K AED)
- Modern Office Space (180K AED)
- Cozy 1BR Apartment (520K AED)

### Clients
- Ahmed Al-Rashid (Buyer, 500K-1.2M budget)
- Sarah Johnson (Investor, 800K-2M budget)
- Mohammed Hassan (Seller, villa)
- Emma Wilson (First-time buyer)
- David Chen (Luxury buyer, 1.5M-3.5M budget)

## 🚀 Production Deployment

For production deployment:

1. **Set Environment Variables**:
   ```bash
   ENVIRONMENT=production
   DISABLE_AUTH=false
   DATABASE_URL=postgresql://...
   SECRET_KEY=secure-random-key
   ```

2. **Use Production Database**: PostgreSQL instead of SQLite

3. **Enable Authentication**: Set `DISABLE_AUTH=false`

4. **Configure CORS**: Set specific allowed origins

5. **Use Process Manager**: PM2, systemd, or container orchestration

## 🤝 Development Workflow

1. **Start Server**: `python start-backend.py`
2. **Test Changes**: `python test_endpoints.py`
3. **View Logs**: Check console output or `propertypro-dev.log`
4. **Reset Database**: Delete `propertypro_dev.db` and restart
5. **API Testing**: Use `/docs` for interactive testing

## 📝 Logging

Development logs are written to:
- **Console**: Structured logging with colors
- **File**: `propertypro-dev.log` (detailed logs)

Log levels: INFO, WARNING, ERROR

## 🔄 Auto-Reload

For development with auto-reload on file changes, modify `start-backend.py`:

```python
uvicorn.run(
    "app.main:app",
    host=host,
    port=port,
    reload=True,  # Enable auto-reload
    log_level="info",
    access_log=True
)
```

---

## 📞 Support

For development issues:
1. Check the troubleshooting section above
2. Run `python test_endpoints.py` to diagnose
3. Review logs in `propertypro-dev.log`
4. Ensure all prerequisites are installed

**Happy coding! 🏠✨**