"""
Brokerage-Centric Database Models
=================================

This module contains all database models for the brokerage-centric architecture,
including brokerage management, team performance, knowledge base, and workflow automation.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table, DECIMAL, Date, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import json

from . import Base

# Import models that are referenced in relationships (temporarily disabled to resolve import issues)
# try:
#     from .ai_assistant_models import RERAComplianceData, RetentionAnalytic
# except ImportError:
#     # Define placeholder classes if models are not available
#     class RERAComplianceData(Base):
#         __tablename__ = "rera_compliance_data"
#         id = Column(Integer, primary_key=True, index=True)
#         brokerage = relationship("Brokerage", back_populates="rera_compliance_data")
#     
#     class RetentionAnalytic(Base):
#         __tablename__ = "retention_analytics"
#         id = Column(Integer, primary_key=True, index=True)
#         brokerage = relationship("Brokerage", back_populates="retention_analytics")

class Brokerage(Base):
    __tablename__ = "brokerages"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    license_number = Column(String(100), unique=True, nullable=True, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    branding_config = Column(Text, default='{}')  # JSONB equivalent
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="brokerage")
    team_performance = relationship("TeamPerformance", back_populates="brokerage", cascade="all, delete-orphan")
    knowledge_base = relationship("KnowledgeBase", back_populates="brokerage", cascade="all, delete-orphan")
    brand_assets = relationship("BrandAsset", back_populates="brokerage", cascade="all, delete-orphan")
    ai_brand_assets = relationship("AIBrandAsset", back_populates="brokerage", cascade="all, delete-orphan")
    workflow_automation = relationship("WorkflowAutomation", back_populates="brokerage", cascade="all, delete-orphan")
    client_nurturing = relationship("ClientNurturing", back_populates="brokerage", cascade="all, delete-orphan")
    compliance_rules = relationship("ComplianceRule", back_populates="brokerage", cascade="all, delete-orphan")
    agent_consistency_metrics = relationship("AgentConsistencyMetric", back_populates="brokerage", cascade="all, delete-orphan")
    lead_retention_analytics = relationship("LeadRetentionAnalytic", back_populates="brokerage", cascade="all, delete-orphan")
    workflow_efficiency_metrics = relationship("WorkflowEfficiencyMetric", back_populates="brokerage", cascade="all, delete-orphan")
    
    # Phase 3 Advanced Models relationships
    predictive_models = relationship("PredictivePerformanceModel", back_populates="brokerage", cascade="all, delete-orphan")
    benchmarking_data = relationship("BenchmarkingData", back_populates="brokerage", cascade="all, delete-orphan")
    activity_analytics = relationship("UserActivityAnalytic", back_populates="brokerage", cascade="all, delete-orphan")
    
    # AI Assistant relationships
    ai_requests = relationship("AIRequest", back_populates="brokerage", cascade="all, delete-orphan")
    ai_requests_new = relationship("AIRequestNew", back_populates="brokerage", cascade="all, delete-orphan")
    rera_compliance_data = relationship("RERAComplianceData", back_populates="brokerage", cascade="all, delete-orphan")
    retention_analytics = relationship("RetentionAnalytic", back_populates="brokerage", cascade="all, delete-orphan")
    voice_requests = relationship("VoiceRequest", back_populates="brokerage", cascade="all, delete-orphan")
    task_automations = relationship("TaskAutomation", back_populates="brokerage", cascade="all, delete-orphan")
    nurturing_sequences = relationship("SmartNurturingSequence", back_populates="brokerage", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Brokerage(id={self.id}, name='{self.name}', license='{self.license_number}')>"
    
    @property
    def branding_config_dict(self):
        """Get branding config as dictionary"""
        try:
            return json.loads(self.branding_config) if self.branding_config else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @branding_config_dict.setter
    def branding_config_dict(self, value):
        """Set branding config from dictionary"""
        self.branding_config = json.dumps(value) if value else '{}'

class TeamPerformance(Base):
    """Agent performance tracking and analytics"""
    __tablename__ = "team_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 2), nullable=True)
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    metadata_json = Column(Text, default='{}')  # JSONB equivalent
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="team_performance")
    agent = relationship("User", back_populates="team_performance")
    
    def __repr__(self):
        return f"<TeamPerformance(id={self.id}, agent_id={self.agent_id}, metric='{self.metric_name}')>"
    
    @property
    def metadata_dict(self):
        """Get metadata as dictionary"""
        try:
            return json.loads(self.metadata_json) if self.metadata_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}

class KnowledgeBase(Base):
    """Company policies, training materials, and best practices"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(ARRAY(String), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="knowledge_base")
    creator = relationship("User", back_populates="created_knowledge")
    
    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, title='{self.title}', category='{self.category}')>"

class BrandAsset(Base):
    """Logos, templates, and branding guidelines"""
    __tablename__ = "brand_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False, index=True)  # 'logo', 'template', 'color_scheme', 'font'
    asset_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    metadata_json = Column(Text, default='{}')  # JSONB equivalent
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="brand_assets")
    
    def __repr__(self):
        return f"<BrandAsset(id={self.id}, type='{self.asset_type}', name='{self.asset_name}')>"
    
    @property
    def metadata_dict(self):
        """Get metadata as dictionary"""
        try:
            return json.loads(self.metadata_json) if self.metadata_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}

class WorkflowAutomation(Base):
    """Task management and automation rules"""
    __tablename__ = "workflow_automation"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    trigger_type = Column(String(50), nullable=False, index=True)  # 'manual', 'scheduled', 'event_based'
    conditions = Column(Text, default='{}')  # JSONB equivalent
    actions = Column(Text, default='{}')  # JSONB equivalent
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="workflow_automation")
    creator = relationship("User", back_populates="created_workflows")
    efficiency_metrics = relationship("WorkflowEfficiencyMetric", back_populates="workflow", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkflowAutomation(id={self.id}, name='{self.name}', trigger='{self.trigger_type}')>"
    
    @property
    def conditions_dict(self):
        """Get conditions as dictionary"""
        try:
            return json.loads(self.conditions) if self.conditions else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def actions_dict(self):
        """Get actions as dictionary"""
        try:
            return json.loads(self.actions) if self.actions else {}
        except (json.JSONDecodeError, TypeError):
            return {}

class ClientNurturing(Base):
    """Communication sequences and templates for lead nurturing"""
    __tablename__ = "client_nurturing"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    sequence_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    steps = Column(Text, default='[]')  # JSONB equivalent
    triggers = Column(Text, default='{}')  # JSONB equivalent
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="client_nurturing")
    creator = relationship("User", back_populates="created_nurturing_sequences")
    
    def __repr__(self):
        return f"<ClientNurturing(id={self.id}, name='{self.sequence_name}')>"
    
    @property
    def steps_list(self):
        """Get steps as list"""
        try:
            return json.loads(self.steps) if self.steps else []
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def triggers_dict(self):
        """Get triggers as dictionary"""
        try:
            return json.loads(self.triggers) if self.triggers else {}
        except (json.JSONDecodeError, TypeError):
            return {}

class ComplianceRule(Base):
    """Regulatory requirements and compliance monitoring"""
    __tablename__ = "compliance_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_type = Column(String(50), nullable=False, index=True)  # 'rera', 'vat', 'contract', 'disclosure'
    description = Column(Text, nullable=True)
    conditions = Column(Text, default='{}')  # JSONB equivalent
    actions = Column(Text, default='{}')  # JSONB equivalent
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="compliance_rules")
    creator = relationship("User", back_populates="created_compliance_rules")
    
    def __repr__(self):
        return f"<ComplianceRule(id={self.id}, name='{self.rule_name}', type='{self.rule_type}')>"
    
    @property
    def conditions_dict(self):
        """Get conditions as dictionary"""
        try:
            return json.loads(self.conditions) if self.conditions else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def actions_dict(self):
        """Get actions as dictionary"""
        try:
            return json.loads(self.actions) if self.actions else {}
        except (json.JSONDecodeError, TypeError):
            return {}

class AgentConsistencyMetric(Base):
    """Agent consistency tracking and scoring"""
    __tablename__ = "agent_consistency_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    consistency_score = Column(DECIMAL(5, 2), nullable=False)
    metrics = Column(Text, default='{}')  # JSONB equivalent
    period = Column(String(20), nullable=False, index=True)  # 'daily', 'weekly', 'monthly'
    calculated_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    agent = relationship("User", back_populates="consistency_metrics")
    brokerage = relationship("Brokerage", back_populates="agent_consistency_metrics")
    
    def __repr__(self):
        return f"<AgentConsistencyMetric(id={self.id}, agent_id={self.agent_id}, score={self.consistency_score})>"
    
    @property
    def metrics_dict(self):
        """Get metrics as dictionary"""
        try:
            return json.loads(self.metrics) if self.metrics else {}
        except (json.JSONDecodeError, TypeError):
            return {}

class LeadRetentionAnalytic(Base):
    """Lead retention tracking and conversion analytics"""
    __tablename__ = "lead_retention_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    lead_id = Column(Integer, nullable=True)  # Will reference leads table when it exists
    retention_score = Column(DECIMAL(5, 2), nullable=True)
    touchpoints = Column(Integer, default=0)
    conversion_probability = Column(DECIMAL(5, 2), nullable=True)
    last_contact_date = Column(DateTime, nullable=True)
    metadata_json = Column(Text, default='{}')  # JSONB equivalent
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="lead_retention_analytics")
    
    def __repr__(self):
        return f"<LeadRetentionAnalytic(id={self.id}, lead_id={self.lead_id}, score={self.retention_score})>"
    
    @property
    def metadata_dict(self):
        """Get metadata as dictionary"""
        try:
            return json.loads(self.metadata_json) if self.metadata_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}

class WorkflowEfficiencyMetric(Base):
    """Workflow efficiency tracking and optimization metrics"""
    __tablename__ = "workflow_efficiency_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    workflow_id = Column(Integer, ForeignKey('workflow_automation.id'), nullable=False, index=True)
    efficiency_score = Column(DECIMAL(5, 2), nullable=True)
    time_saved = Column(Integer, nullable=True)  # in minutes
    automation_rate = Column(DECIMAL(5, 2), nullable=True)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    metadata_json = Column(Text, default='{}')  # JSONB equivalent
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="workflow_efficiency_metrics")
    workflow = relationship("WorkflowAutomation", back_populates="efficiency_metrics")
    
    def __repr__(self):
        return f"<WorkflowEfficiencyMetric(id={self.id}, workflow_id={self.workflow_id}, score={self.efficiency_score})>"
    
    @property
    def metadata_dict(self):
        """Get metadata as dictionary"""
        try:
            return json.loads(self.metadata_json) if self.metadata_json else {}
        except (json.JSONDecodeError, TypeError):
            return {}
