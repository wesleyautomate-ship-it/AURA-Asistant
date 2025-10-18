#!/usr/bin/env python3
"""
Centralized settings configuration for the Dubai Real Estate RAG System
"""

import os
from pathlib import Path
from .env_loader import load_env

# Load environment variables from centralized loader
load_env()


def _get_bool(name: str, default: bool = False) -> bool:
    """Parse boolean env vars (1/0/true/false)."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Database Configuration
# Use SQLite for local development, PostgreSQL for production
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./propertypro_dev.db"
    if os.getenv("ENVIRONMENT", "development") == "development"
    else "postgresql://admin:password123@localhost:5432/real_estate_db",
)

_object_store_path_raw = os.getenv("OBJECT_STORE_PATH")
OBJECT_STORE_PATH = (
    _object_store_path_raw.strip() if _object_store_path_raw else None
)

# ChromaDB Configuration
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8002"))

# Optional Feature Flags
ENABLE_PDF_WEASYPRINT = _get_bool("ENABLE_PDF_WEASYPRINT", False)
ENABLE_VECTOR_CHROMA = _get_bool("ENABLE_VECTOR_CHROMA", False)

# Optional Feature Flags
ENABLE_PDF_WEASYPRINT = _get_bool("ENABLE_PDF_WEASYPRINT", False)
ENABLE_VECTOR_CHROMA = _get_bool("ENABLE_VECTOR_CHROMA", False)

# CORS defaults
_default_cors_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
_cors_origins_env = os.getenv("CORS_ALLOWED_ORIGINS")
if _cors_origins_env:
    CORS_ALLOWED_ORIGINS = [
        origin.strip() for origin in _cors_origins_env.split(",") if origin.strip()
    ]
else:
    CORS_ALLOWED_ORIGINS = _default_cors_origins

# Dev auth toggle (off by default)
DEV_AUTH_ALLOW = _get_bool("DEV_AUTH_ALLOW", False)

# Google AI Configuration
# Support both GEMINI_API_KEY and GOOGLE_API_KEY for backward compatibility
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    # Do not provide any fallback key. In development we warn; in production
    # validation should fail fast via validate_settings().
    print(
        "⚠️  GOOGLE_API_KEY or GEMINI_API_KEY not set. Some AI features will be disabled until configured."
    )

# Reelly API removed

# AI Model Configuration
AI_MODEL = os.getenv("AI_MODEL", "gemini-1.5-flash")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
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
        "http://localhost:5173",  # Vite default port
        "http://localhost:5174",  # Vite alternative port
        "http://127.0.0.1:5173",  # Vite default with 127.0.0.1
        "http://127.0.0.1:5174",  # Vite alternative with 127.0.0.1
        "http://192.168.1.241:3001",
        "https://*.ngrok.io",
        "https://*.ngrok-free.app",
        "http://*.ngrok.io",
        "http://*.ngrok-free.app",
    ]

# File Upload Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".csv",
    ".xlsx",
    ".xls",
}
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
        # Optional features (expose both uppercase + snake_case for convenience)
        self.ENABLE_PDF_WEASYPRINT = ENABLE_PDF_WEASYPRINT
        self.ENABLE_VECTOR_CHROMA = ENABLE_VECTOR_CHROMA
        self.enable_pdf_weasyprint = ENABLE_PDF_WEASYPRINT
        self.enable_vector_chroma = ENABLE_VECTOR_CHROMA
        self.object_store_path = OBJECT_STORE_PATH
        self.OBJECT_STORE_PATH = OBJECT_STORE_PATH
        self.cors_allowed_origins = CORS_ALLOWED_ORIGINS
        self.CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS
        self.dev_auth_allow = DEV_AUTH_ALLOW
        self.DEV_AUTH_ALLOW = DEV_AUTH_ALLOW


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
        "GOOGLE_API_KEY",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        return False

    return True


# Export settings
__all__ = [
    "DATABASE_URL",
    "CHROMA_HOST",
    "CHROMA_PORT",
    "ENABLE_PDF_WEASYPRINT",
    "ENABLE_VECTOR_CHROMA",
    "ENABLE_PDF_WEASYPRINT",
    "ENABLE_VECTOR_CHROMA",
    "GOOGLE_API_KEY",
    "AI_MODEL",
    "HOST",
    "PORT",
    "DEBUG",
    "ALLOWED_ORIGINS",
    "UPLOAD_DIR",
    "ALLOWED_EXTENSIONS",
    "MAX_FILE_SIZE",
    "REDIS_URL",
    "CACHE_TTL",
    "LOG_LEVEL",
    "LOG_FILE",
    "MAX_WORKERS",
    "BATCH_SIZE",
    "SECRET_KEY",
    "IS_PRODUCTION",
    "JWT_ALGORITHM",
    "ALGORITHM",
    "JWT_REFRESH_TOKEN_EXPIRE_DAYS",
    "BCRYPT_ROUNDS",
    "RATE_LIMIT_REQUESTS_PER_MINUTE",
    "RATE_LIMIT_LOGIN_ATTEMPTS",
    "CORS_ALLOWED_ORIGINS",
    "DEV_AUTH_ALLOW",
    "OBJECT_STORE_PATH",
    "ENABLE_PDF_WEASYPRINT",
    "ENABLE_VECTOR_CHROMA",
    "validate_settings",
    "Settings",
    "get_settings",
]
