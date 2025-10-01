"""
Authentication models for Dubai Real Estate RAG System
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import Brokerage model to resolve relationship
try:
    from app.domain.listings.brokerage_models import Brokerage
except ImportError:
    # If Brokerage model is not available, define a placeholder
    class Brokerage(Base):
        __tablename__ = "brokerages"
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(255), nullable=False, index=True)
        users = relationship("User", back_populates="brokerage")

# Association tables for many-to-many relationships
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True),
    extend_existing=True
)

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    extend_existing=True
)

class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), default='client')  # client, agent, employee, admin, brokerage_owner
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), unique=True, nullable=True)
    password_reset_token = Column(String(255), unique=True, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    user_roles_rel = relationship("Role", secondary=user_roles, back_populates="users")
    brokerage = relationship("Brokerage", back_populates="users")
    team_performance = relationship("TeamPerformance", back_populates="agent", cascade="all, delete-orphan")
    created_knowledge = relationship("KnowledgeBase", back_populates="creator", cascade="all, delete-orphan")
    created_workflows = relationship("WorkflowAutomation", back_populates="creator", cascade="all, delete-orphan")
    created_nurturing_sequences = relationship("ClientNurturing", back_populates="creator", cascade="all, delete-orphan")
    created_compliance_rules = relationship("ComplianceRule", back_populates="creator", cascade="all, delete-orphan")
    consistency_metrics = relationship("AgentConsistencyMetric", back_populates="agent", cascade="all, delete-orphan")
    activity_analytics = relationship("UserActivityAnalytic", back_populates="user", cascade="all, delete-orphan")
    developer_settings = relationship("DeveloperPanelSetting", back_populates="user", cascade="all, delete-orphan")
    
    # AI Assistant relationships
    ai_requests = relationship("AIRequest", foreign_keys="AIRequest.agent_id", cascade="all, delete-orphan")
    ai_requests_new = relationship("AIRequestNew", foreign_keys="AIRequestNew.user_id", back_populates="user", cascade="all, delete-orphan")
    human_expert_profile = relationship("HumanExpert", back_populates="user", uselist=False, cascade="all, delete-orphan")
    voice_requests = relationship("VoiceRequest", back_populates="agent", cascade="all, delete-orphan")
    task_automations = relationship("TaskAutomation", back_populates="agent", cascade="all, delete-orphan")
    created_nurturing_sequences_ai = relationship("SmartNurturingSequence", back_populates="creator", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

class UserSession(Base):
    """User session model for tracking active sessions"""
    __tablename__ = "user_sessions"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_used = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"
    
    @property
    def is_expired(self):
        return datetime.utcnow() > self.expires_at

class Permission(Base):
    """Permission model for fine-grained access control"""
    __tablename__ = "permissions"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    resource = Column(String(100), nullable=False)  # e.g., 'property', 'user', 'chat'
    action = Column(String(50), nullable=False)     # e.g., 'read', 'write', 'delete'
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"

class Role(Base):
    """Role model for role-based access control"""
    __tablename__ = "roles"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="user_roles_rel")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', is_default={self.is_default})>"
    
    def has_permission(self, resource, action):
        """Check if role has specific permission"""
        for permission in self.permissions:
            if permission.resource == resource and permission.action == action:
                return True
        return False

class AuditLog(Base):
    """Audit log model for security event tracking"""
    __tablename__ = "audit_logs"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(100), nullable=False)  # login, logout, password_change, etc.
    event_data = Column(Text, nullable=True)  # JSON string with event details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', user_id={self.user_id}, success={self.success})>"
