"""
Authentication models for Dubai Real Estate RAG System
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Table,
    JSON,
    Float,
    Numeric,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import json
import uuid

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Brokerage(Base):
    """Core brokerage entity shared across the platform."""

    __tablename__ = "brokerages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    license_number = Column(String(100), unique=True, nullable=True, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    branding_config = Column(Text, default="{}")
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Primary relationships
    users = relationship(
        "User", back_populates="brokerage", cascade="all, delete-orphan"
    )

    # Extended relationships (kept for downstream domain modules)
    team_performance = relationship(
        "TeamPerformance", back_populates="brokerage", cascade="all, delete-orphan"
    )
    knowledge_base = relationship(
        "KnowledgeBase", back_populates="brokerage", cascade="all, delete-orphan"
    )
    brand_assets = relationship(
        "BrandAsset", back_populates="brokerage", cascade="all, delete-orphan"
    )
    ai_brand_assets = relationship(
        "AIBrandAsset", back_populates="brokerage", cascade="all, delete-orphan"
    )
    workflow_automation = relationship(
        "WorkflowAutomation", back_populates="brokerage", cascade="all, delete-orphan"
    )
    client_nurturing = relationship(
        "ClientNurturing", back_populates="brokerage", cascade="all, delete-orphan"
    )
    compliance_rules = relationship(
        "ComplianceRule", back_populates="brokerage", cascade="all, delete-orphan"
    )
    agent_consistency_metrics = relationship(
        "AgentConsistencyMetric", back_populates="brokerage", cascade="all, delete-orphan"
    )
    lead_retention_analytics = relationship(
        "LeadRetentionAnalytic", back_populates="brokerage", cascade="all, delete-orphan"
    )
    workflow_efficiency_metrics = relationship(
        "WorkflowEfficiencyMetric", back_populates="brokerage", cascade="all, delete-orphan"
    )
    predictive_models = relationship(
        "PredictivePerformanceModel",
        back_populates="brokerage",
        cascade="all, delete-orphan",
    )
    benchmarking_data = relationship(
        "BenchmarkingData", back_populates="brokerage", cascade="all, delete-orphan"
    )
    activity_analytics = relationship(
        "UserActivityAnalytic", back_populates="brokerage", cascade="all, delete-orphan"
    )
    ai_requests = relationship(
        "AIRequest", back_populates="brokerage", cascade="all, delete-orphan"
    )
    ai_requests_new = relationship(
        "AIRequestNew", back_populates="brokerage", cascade="all, delete-orphan"
    )
    task_automations = relationship(
        "TaskAutomation", back_populates="brokerage", cascade="all, delete-orphan"
    )
    rera_compliance_data = relationship(
        "RERAComplianceData", back_populates="brokerage", cascade="all, delete-orphan"
    )
    retention_analytics = relationship(
        "RetentionAnalytic", back_populates="brokerage", cascade="all, delete-orphan"
    )
    voice_requests = relationship(
        "VoiceRequest", back_populates="brokerage", cascade="all, delete-orphan"
    )
    nurturing_sequences = relationship(
        "SmartNurturingSequence", back_populates="brokerage", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Brokerage id={self.id} name='{self.name}'>"

    @property
    def branding_config_dict(self):
        """Return branding configuration as a dictionary."""
        try:
            if not self.branding_config:
                return {}
            return (
                json.loads(self.branding_config)
                if isinstance(self.branding_config, str)
                else dict(self.branding_config)
            )
        except (json.JSONDecodeError, TypeError, ValueError):
            return {}

    @branding_config_dict.setter
    def branding_config_dict(self, value):
        """Persist branding configuration from a dictionary."""
        self.branding_config = json.dumps(value) if value else "{}"


# Association tables for many-to-many relationships
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class User(Base):
    """User model for authentication and authorization"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(
        String(50), default="client"
    )  # client, agent, employee, admin, brokerage_owner
    brokerage_id = Column(
        Integer, ForeignKey("brokerages.id"), nullable=True, index=True
    )
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
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    user_roles_rel = relationship("Role", secondary=user_roles, back_populates="users")
    brokerage = relationship("Brokerage", back_populates="users")
    team_performance = relationship(
        "TeamPerformance", back_populates="agent", cascade="all, delete-orphan"
    )
    created_knowledge = relationship(
        "KnowledgeBase", back_populates="creator", cascade="all, delete-orphan"
    )
    created_workflows = relationship(
        "WorkflowAutomation", back_populates="creator", cascade="all, delete-orphan"
    )
    created_nurturing_sequences = relationship(
        "ClientNurturing", back_populates="creator", cascade="all, delete-orphan"
    )
    created_compliance_rules = relationship(
        "ComplianceRule", back_populates="creator", cascade="all, delete-orphan"
    )
    consistency_metrics = relationship(
        "AgentConsistencyMetric", back_populates="agent", cascade="all, delete-orphan"
    )
    activity_analytics = relationship(
        "UserActivityAnalytic", back_populates="user", cascade="all, delete-orphan"
    )
    developer_settings = relationship(
        "DeveloperPanelSetting", back_populates="user", cascade="all, delete-orphan"
    )

    # AI Assistant relationships
    ai_requests = relationship(
        "AIRequest", foreign_keys="AIRequest.agent_id", cascade="all, delete-orphan"
    )
    ai_requests_new = relationship(
        "AIRequestNew",
        foreign_keys="AIRequestNew.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    human_expert_profile = relationship(
        "HumanExpert",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    voice_requests = relationship(
        "VoiceRequest", back_populates="agent", cascade="all, delete-orphan"
    )
    task_automations = relationship(
        "TaskAutomation", back_populates="agent", cascade="all, delete-orphan"
    )
    created_nurturing_sequences_ai = relationship(
        "SmartNurturingSequence", back_populates="creator", cascade="all, delete-orphan"
    )
    
    # Enhanced relationships for domain models
    managed_properties = relationship(
        "EnhancedProperty", foreign_keys="EnhancedProperty.agent_id", back_populates="agent"
    )
    assigned_leads = relationship(
        "EnhancedLead", foreign_keys="EnhancedLead.assigned_agent_id", back_populates="assigned_agent"
    )
    assigned_clients = relationship(
        "EnhancedClient", foreign_keys="EnhancedClient.assigned_agent_id", back_populates="assigned_agent"
    )

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

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    resource = Column(String(100), nullable=False)  # e.g., 'property', 'user', 'chat'
    action = Column(String(50), nullable=False)  # e.g., 'read', 'write', 'delete'
    created_at = Column(DateTime, default=func.now())

    # Relationships
    roles = relationship(
        "Role", secondary=role_permissions, back_populates="permissions"
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}', resource='{self.resource}', action='{self.action}')>"


class Role(Base):
    """Role model for role-based access control"""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    permissions = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )
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

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    contact_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    event_type = Column(
        String(100), nullable=False
    )  # login, logout, password_change, etc.
    event_data = Column(Text, nullable=True)  # JSON string with event details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    occurred_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', user_id={self.user_id}, success={self.success})>"


# ========================================
# Chat Console Models (Additive)
# ========================================


class ChatThread(Base):
    """Chat thread for agentic chat sessions"""

    __tablename__ = "chat_threads"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ChatMessage(Base):
    """Chat messages within a thread"""

    __tablename__ = "chat_messages"

    id = Column(String(64), primary_key=True, index=True)
    thread_id = Column(
        String(64), ForeignKey("chat_threads.id"), nullable=False, index=True
    )
    role = Column(String(16), nullable=False)  # 'user' | 'assistant' | 'system'
    text = Column(Text, nullable=False)
    tokens_in = Column(Integer, nullable=True)
    tokens_out = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())


# ========================================
# Brochure Drafts (AI brochure flow)
# ========================================


class BrochureDraft(Base):
    __tablename__ = "brochure_drafts"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    data = Column(JSON, default=dict)  # entire draft blob
    status = Column(String(20), default="draft", index=True)
    download_url = Column(String(512), nullable=True)
    template_id = Column(String(36), ForeignKey("brochure_templates.id"), nullable=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True)
    property_id = Column(String(36), ForeignKey("properties.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    property = relationship("Property")

    def __repr__(self):
        return f"<BrochureDraft id={self.id} status={self.status}>"


class BrochureTemplate(Base):
    __tablename__ = "brochure_templates"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=False)
    preview_url = Column(String(512), nullable=True)
    fields_schema = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<BrochureTemplate id={self.id} name={self.name}>"


# ========================================
# Property Management Models
# ========================================

import enum

class PropertyType(enum.Enum):
    apartment = "apartment"
    villa = "villa"
    townhouse = "townhouse"
    mixed = "mixed"

class PropertyStatus(enum.Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class Property(Base):
    """Property model for real estate listings"""
    
    __tablename__ = "properties"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    title = Column(String(255), nullable=False, index=True)  # e.g., "2BR at Orla Residences"
    building = Column(String(255), nullable=False, index=True)  # e.g., "Orla Residences"
    community = Column(String(255), nullable=True, index=True)  # e.g., "Palm Jumeirah"
    unit = Column(String(100), nullable=True)  # e.g., "Unit 1803"
    
    property_type = Column(Enum(PropertyType), default=PropertyType.apartment, nullable=False)
    beds = Column(Integer, nullable=True)
    baths = Column(Float, nullable=True)
    area_sqft = Column(Float, nullable=True)
    price_aed = Column(Integer, nullable=True)  # Price in AED
    
    description = Column(Text, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    
    status = Column(Enum(PropertyStatus), default=PropertyStatus.draft, nullable=False, index=True)
    
    # Relationships
    photos = relationship("PropertyPhoto", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Property id={self.id} title='{self.title}' status={self.status}>"


class PropertyPhoto(Base):
    """Property photo model"""
    
    __tablename__ = "property_photos"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    property_id = Column(String(36), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    
    url = Column(String(512), nullable=False)  # public URL or local path served by backend
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Relationships
    property = relationship("Property", back_populates="photos")
    
    def __repr__(self):
        return f"<PropertyPhoto id={self.id} property_id={self.property_id} sort_order={self.sort_order}>"
