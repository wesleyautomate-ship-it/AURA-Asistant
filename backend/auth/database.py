from app.core.models import Base
"""
Database connection and session management for authentication
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from typing import Generator
from config.settings import DATABASE_URL

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine with better connection management
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    """
    db = None
    try:
        db = SessionLocal()
        yield db
        db.commit()
    except Exception as e:
        if db:
            try:
                db.rollback()
            except Exception as rollback_error:
                logger.error(f"Database rollback error: {rollback_error}")
        logger.error(f"Database error: {e}")
        raise
    finally:
        if db:
            try:
                db.close()
            except Exception as close_error:
                logger.error(f"Database close error: {close_error}")

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Database session context manager (for non-FastAPI usage)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    """
    from app.core.models import Base
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize default data
        init_default_data()
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def init_default_data():
    """
    Initialize default roles and permissions
    """
    from .models import Role, Permission, User
    from .utils import hash_password
    from datetime import datetime
    
    db = SessionLocal()
    try:
        # Check if default data already exists
        if db.query(Role).first():
            logger.info("Default data already exists, skipping initialization")
            return
        
        # Create default permissions
        permissions = [
            # Property permissions
            Permission(name="property_read", description="Read property information", resource="property", action="read"),
            Permission(name="property_write", description="Create and update properties", resource="property", action="write"),
            Permission(name="property_delete", description="Delete properties", resource="property", action="delete"),
            
            # Chat permissions
            Permission(name="chat_read", description="Read chat messages", resource="chat", action="read"),
            Permission(name="chat_write", description="Send chat messages", resource="chat", action="write"),
            
            # User permissions
            Permission(name="user_read", description="Read user information", resource="user", action="read"),
            Permission(name="user_write", description="Create and update users", resource="user", action="write"),
            Permission(name="user_delete", description="Delete users", resource="user", action="delete"),
            
            # Admin permissions
            Permission(name="admin_access", description="Full administrative access", resource="admin", action="all"),
        ]
        
        for permission in permissions:
            db.add(permission)
        
        # Create default roles
        agent_role = Role(
            name="agent",
            description="Real estate agents and brokers",
            is_default=True
        )
        
        employee_role = Role(
            name="employee",
            description="Company staff and employees"
        )
        
        admin_role = Role(
            name="admin",
            description="System administrators and managers"
        )
        
        db.add_all([agent_role, employee_role, admin_role])
        db.flush()  # Flush to get IDs
        
        # Assign permissions to roles
        # Agent permissions
        agent_permissions = db.query(Permission).filter(
            Permission.name.in_(["property_read", "property_write", "chat_read", "chat_write", "user_read"])
        ).all()
        agent_role.permissions = agent_permissions
        
        # Employee permissions
        employee_permissions = db.query(Permission).filter(
            Permission.name.in_(["property_read", "property_write", "chat_read", "chat_write", "user_read", "user_write"])
        ).all()
        employee_role.permissions = employee_permissions
        
        # Admin permissions
        admin_permissions = db.query(Permission).all()
        admin_role.permissions = admin_permissions
        
        # Create default admin user
        admin_user = User(
            email="admin@dubai-estate.com",
            password_hash=hash_password("Admin123!"),
            first_name="System",
            last_name="Administrator",
            role="admin",
            is_active=True,
            email_verified=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        
        logger.info("Default roles, permissions, and admin user created successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to initialize default data: {e}")
        raise
    finally:
        db.close()

def check_db_connection():
    """
    Check database connection
    """
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

