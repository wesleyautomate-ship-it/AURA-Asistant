#!/usr/bin/env python3
"""
PropertyPro AI - Development Backend Startup Script
==================================================

This script initializes and starts the PropertyPro AI backend in development mode.

Features:
- Automatic environment configuration
- Database initialization with SQLite
- Sample data seeding
- CORS configuration for frontend
- Authentication bypass for development
- Single command startup

Usage:
    python start-backend.py

Requirements:
    - Python 3.8+
    - Dependencies installed (see requirements.txt)
    
The script will:
1. Set up development environment variables
2. Initialize SQLite database
3. Seed sample data
4. Start the server on http://localhost:8000
"""

import os
import sys
import logging
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def setup_logging():
    """Configure logging for development"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('propertypro-dev.log')
        ]
    )

def setup_development_environment():
    """Set up environment variables for development"""
    print("🔧 Setting up development environment...")
    
    # Core environment
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("DEBUG", "true")
    
    # Server configuration
    os.environ.setdefault("HOST", "127.0.0.1")
    os.environ.setdefault("PORT", "8000")
    
    # Database - Use SQLite for development
    os.environ.setdefault("DATABASE_URL", "sqlite:///./propertypro_dev.db")
    
    # CORS - Allow frontend development server
    os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    
    # Authentication bypass for development
    os.environ.setdefault("DISABLE_AUTH", "true")
    
    # Security (development defaults)
    os.environ.setdefault("SECRET_KEY", "dev-secret-key-change-in-production")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    
    # Optional integrations - disabled for local dev
    os.environ.setdefault("GOOGLE_API_KEY", "")
    os.environ.setdefault("CHROMA_HOST", "localhost")
    os.environ.setdefault("CHROMA_PORT", "8002")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
    
    # Logging
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    print("✅ Development environment configured")

def initialize_database():
    """Initialize database and seed sample data"""
    print("🗄️  Initializing database...")
    
    try:
        from app.core.database import Base, engine, get_db_context
        from app.services.seed_data import seed_all_data
        
        # Create all tables
        print("   Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Seed sample data
        print("   Seeding sample data...")
        with get_db_context() as db:
            success = seed_all_data(db)
            if success:
                print("✅ Database initialized with sample data")
            else:
                print("⚠️  Database initialized but seeding failed")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("   The server may still start but with limited functionality")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy", 
        "pydantic"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("   Please run: pip install -r requirements.txt")
        return False
    
    return True

def show_startup_info():
    """Display startup information"""
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "8000")
    
    print("\n" + "="*60)
    print("🚀 PropertyPro AI Backend - Development Mode")
    print("="*60)
    print(f"📍 Server URL: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔍 ReDoc: http://{host}:{port}/redoc")
    print(f"💾 Database: SQLite (propertypro_dev.db)")
    print(f"🔐 Authentication: Disabled (development mode)")
    print(f"🌐 CORS Origins: {os.getenv('CORS_ORIGINS', 'localhost:3000')}")
    print("\n🔑 Key Endpoints:")
    print(f"   • Health Check: http://{host}:{port}/health")
    print(f"   • Auth (Dev): http://{host}:{port}/api/v1/auth/login")
    print(f"   • Properties: http://{host}:{port}/api/v1/properties")
    print(f"   • Clients: http://{host}:{port}/api/v1/clients")
    print(f"   • Dashboard: http://{host}:{port}/api/v1/command-center")
    print("\n💡 Sample Login Credentials:")
    print("   • Username: admin@propertypro.ai")
    print("   • Password: Admin123!")
    print("="*60)

def main():
    """Main startup function"""
    print("🏠 Starting PropertyPro AI Backend (Development Mode)")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_development_environment()
    
    # Initialize database
    initialize_database()
    
    # Import after environment setup
    try:
        from app.main import app
    except ImportError as e:
        logger.error(f"Failed to import application: {e}")
        print(f"❌ Failed to import application: {e}")
        sys.exit(1)
    
    # Get server configuration
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    # Show startup information
    show_startup_info()
    
    try:
        # Start the server
        print("\n🔄 Starting server...")
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=False,  # Set to True for auto-reload during development
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()