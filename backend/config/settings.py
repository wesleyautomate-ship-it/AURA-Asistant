#!/usr/bin/env python3
"""
Centralized settings configuration for the Dubai Real Estate RAG System
"""

import os
from pathlib import Path
from env_loader import load_env

# Load environment variables from centralized loader
load_env()

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:password123@localhost:5432/real_estate_db"
)

# ChromaDB Configuration
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8002"))

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    pass
    # Enforce env-only to avoid accidental leakage/hardcoding
    

# Reelly API removed

# AI Model Configuration
AI_MODEL = os.getenv("AI_MODEL", "gemini-1.5-flash")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8001"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# CORS Configuration
if os.getenv("ENVIRONMENT") == "production":
    ALLOWED_ORIGINS = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ]
elif os.getenv("ENVIRONMENT") == "staging":
    ALLOWED_ORIGINS = [
        "https://staging.yourdomain.com",
        "https://*.ngrok-free.app",  # For testing
    ]
else:  # development
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://192.168.1.241:3001",
        "https://*.ngrok.io",
        "https://*.ngrok-free.app",
        "http://*.ngrok.io",
        "http://*.ngrok-free.app",
    ]

# File Upload Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx', '.xls'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Cache Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}")
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = Path("logs/app.log")
LOG_FILE.parent.mkdir(exist_ok=True)

# Performance Configuration
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ALGORITHM = JWT_ALGORITHM  # Alias for backward compatibility
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
RATE_LIMIT_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
RATE_LIMIT_LOGIN_ATTEMPTS = int(os.getenv("RATE_LIMIT_LOGIN_ATTEMPTS", "5"))

# Production Configuration
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

# Settings class for dependency injection
class Settings:
    def __init__(self):
        self.database_url = DATABASE_URL
        self.chroma_host = CHROMA_HOST
        self.chroma_port = CHROMA_PORT
        self.google_api_key = GOOGLE_API_KEY
        self.ai_model = AI_MODEL
        self.host = HOST
        self.port = PORT
        self.debug = DEBUG
        self.allowed_origins = ALLOWED_ORIGINS
        self.upload_dir = UPLOAD_DIR
        self.allowed_extensions = ALLOWED_EXTENSIONS
        self.max_file_size = MAX_FILE_SIZE
        self.redis_url = REDIS_URL
        self.cache_ttl = CACHE_TTL
        self.log_level = LOG_LEVEL
        self.log_file = LOG_FILE
        self.max_workers = MAX_WORKERS
        self.batch_size = BATCH_SIZE
        self.secret_key = SECRET_KEY
        # Reelly API removed
        self.is_production = IS_PRODUCTION
        self.jwt_algorithm = JWT_ALGORITHM
        self.jwt_refresh_token_expire_days = JWT_REFRESH_TOKEN_EXPIRE_DAYS
        self.bcrypt_rounds = BCRYPT_ROUNDS
        self.rate_limit_requests_per_minute = RATE_LIMIT_REQUESTS_PER_MINUTE
        self.rate_limit_login_attempts = RATE_LIMIT_LOGIN_ATTEMPTS

def get_settings() -> Settings:
    """Get settings instance for dependency injection"""
    return Settings()

# Validation
def validate_settings():
    """Validate critical settings"""
    required_vars = [
        "DATABASE_URL", 
        "CHROMA_HOST", 
        "CHROMA_PORT", 
        "REDIS_URL",
        "GOOGLE_API_KEY"
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        return False
    
    return True

# Export settings
__all__ = [
    'DATABASE_URL', 'CHROMA_HOST', 'CHROMA_PORT', 'GOOGLE_API_KEY',
    'AI_MODEL', 'HOST', 'PORT', 'DEBUG', 'ALLOWED_ORIGINS',
    'UPLOAD_DIR', 'ALLOWED_EXTENSIONS', 'MAX_FILE_SIZE',
    'REDIS_URL', 'CACHE_TTL', 'LOG_LEVEL', 'LOG_FILE',
    'MAX_WORKERS', 'BATCH_SIZE', 'SECRET_KEY', 'IS_PRODUCTION',
    'JWT_ALGORITHM', 'ALGORITHM', 'JWT_REFRESH_TOKEN_EXPIRE_DAYS', 'BCRYPT_ROUNDS',
    'RATE_LIMIT_REQUESTS_PER_MINUTE', 'RATE_LIMIT_LOGIN_ATTEMPTS',
    'validate_settings', 'Settings', 'get_settings'
]
