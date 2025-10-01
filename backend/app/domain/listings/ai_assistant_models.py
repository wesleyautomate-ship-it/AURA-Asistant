"""
AI Assistant Models
==================

SQLAlchemy models for the AI-powered assistant system including:
- AI request processing
- Human expertise management
- Content delivery
- Voice processing
- Task automation
- Dubai data integration
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, DECIMAL, JSON, ARRAY, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import json

from . import Base

class AIRequest(Base):
    """AI request processing and management"""
    __tablename__ = "ai_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    request_type = Column(String(50), nullable=False, index=True)  # 'cma', 'presentation', 'marketing', 'compliance', 'general'
    request_content = Column(Text, nullable=False)
    request_metadata_json = Column(JSON, default=dict)
    status = Column(String(20), default='pending', index=True)  # 'pending', 'processing', 'ai_complete', 'human_review', 'completed', 'failed'
    priority = Column(String(10), default='normal')  # 'low', 'normal', 'high', 'urgent'
    ai_response = Column(Text)
    ai_confidence = Column(DECIMAL(3, 2))  # 0.00-1.00
    human_expert_id = Column(Integer, ForeignKey('human_experts.id'), nullable=True)
    human_review = Column(Text)
    human_rating = Column(Integer)  # 1-5 rating
    final_output = Column(Text)
    output_format = Column(String(20), default='text')  # 'text', 'pdf', 'presentation', 'email', 'social'
    estimated_completion = Column(DateTime)
    actual_completion = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    agent = relationship("User", foreign_keys=[agent_id], back_populates="ai_requests")
    brokerage = relationship("Brokerage", back_populates="ai_requests")
    human_expert = relationship("HumanExpert", back_populates="ai_requests")
    content_deliverables = relationship("ContentDeliverable", back_populates="request", cascade="all, delete-orphan")
    processing_analytics = relationship("AIProcessingAnalytic", back_populates="request", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AIRequest(id={self.id}, type='{self.request_type}', status='{self.status}')>"
    
    @property
    def request_metadata_dict(self):
        """Get request metadata as dictionary"""
        try:
            return json.loads(self.request_metadata_json) if isinstance(self.request_metadata_json, str) else self.request_metadata_json
        except (json.JSONDecodeError, TypeError):
            return {}

class HumanExpert(Base):
    """Human experts who review and refine AI output"""
    __tablename__ = "human_experts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    expertise_area = Column(String(100), nullable=False, index=True)  # 'market_analysis', 'presentations', 'compliance', 'marketing', 'general'
    availability_status = Column(String(20), default='available', index=True)  # 'available', 'busy', 'offline'
    max_concurrent_tasks = Column(Integer, default=3)
    rating = Column(DECIMAL(3, 2), default=5.00, index=True)  # 1.00-5.00
    completed_tasks = Column(Integer, default=0)
    total_revenue = Column(DECIMAL(10, 2), default=0.00)
    specializations = Column(ARRAY(String))
    languages = Column(ARRAY(String), default=['English'])
    timezone = Column(String(50), default='Asia/Dubai')
    working_hours = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="human_expert_profile")
    ai_requests = relationship("AIRequest", back_populates="human_expert")
    
    def __repr__(self):
        return f"<HumanExpert(id={self.id}, user_id={self.user_id}, expertise='{self.expertise_area}')>"
    
    @property
    def working_hours_dict(self):
        """Get working hours as dictionary"""
        try:
            return json.loads(self.working_hours) if isinstance(self.working_hours, str) else self.working_hours
        except (json.JSONDecodeError, TypeError):
            return {"start": "09:00", "end": "18:00"}

class ContentDeliverable(Base):
    """Final content generated for AI requests"""
    __tablename__ = "content_deliverables"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey('ai_requests.id'), nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)  # 'cma', 'presentation', 'email', 'social_post', 'document'
    file_path = Column(String(500))
    content_data = Column(Text)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    branding_applied = Column(Boolean, default=False)
    branding_config = Column(JSON, default=dict)
    quality_score = Column(DECIMAL(3, 2))
    client_feedback = Column(Text)
    download_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    request = relationship("AIRequest", back_populates="content_deliverables")
    
    def __repr__(self):
        return f"<ContentDeliverable(id={self.id}, type='{self.content_type}', request_id={self.request_id})>"
    
    @property
    def branding_config_dict(self):
        """Get branding config as dictionary"""
        try:
            return json.loads(self.branding_config) if isinstance(self.branding_config, str) else self.branding_config
        except (json.JSONDecodeError, TypeError):
            return {}

class VoiceRequest(Base):
    """Voice-to-text processing and audio file management"""
    __tablename__ = "voice_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    audio_file_path = Column(String(500), nullable=False)
    audio_duration = Column(Integer)  # Duration in seconds
    audio_format = Column(String(20))  # 'mp3', 'wav', 'm4a', etc.
    file_size = Column(Integer)  # File size in bytes
    transcription = Column(Text)
    transcription_confidence = Column(DECIMAL(3, 2))  # 0.00-1.00
    processed_request = Column(Text)
    language_detected = Column(String(10), default='en')
    processing_status = Column(String(20), default='pending', index=True)  # 'pending', 'transcribing', 'processed', 'failed'
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    agent = relationship("User", back_populates="voice_requests")
    brokerage = relationship("Brokerage", back_populates="voice_requests")
    
    def __repr__(self):
        return f"<VoiceRequest(id={self.id}, agent_id={self.agent_id}, status='{self.processing_status}')>"

class TaskAutomation(Base):
    """Automated task execution and workflow management"""
    __tablename__ = "task_automation"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    task_type = Column(String(50), nullable=False, index=True)  # 'follow_up', 'report_generation', 'client_communication', 'data_entry'
    task_name = Column(String(255), nullable=False)
    task_description = Column(Text)
    automation_level = Column(String(20), default='semi')  # 'full', 'semi', 'manual'
    trigger_conditions_json = Column(JSON, default=dict)
    execution_schedule_json = Column(JSON, default=dict)
    status = Column(String(20), default='active', index=True)  # 'active', 'paused', 'completed', 'failed'
    last_execution = Column(DateTime)
    next_execution = Column(DateTime, index=True)
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    success_rate = Column(DECIMAL(5, 2), default=0.00)  # Success rate percentage
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    agent = relationship("User", back_populates="task_automations")
    brokerage = relationship("Brokerage", back_populates="task_automations")
    
    def __repr__(self):
        return f"<TaskAutomation(id={self.id}, name='{self.task_name}', type='{self.task_type}')>"
    
    @property
    def trigger_conditions_dict(self):
        """Get trigger conditions as dictionary"""
        try:
            return json.loads(self.trigger_conditions_json) if isinstance(self.trigger_conditions_json, str) else self.trigger_conditions_json
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def execution_schedule_dict(self):
        """Get execution schedule as dictionary"""
        try:
            return json.loads(self.execution_schedule_json) if isinstance(self.execution_schedule_json, str) else self.execution_schedule_json
        except (json.JSONDecodeError, TypeError):
            return {}

class SmartNurturingSequence(Base):
    """Automated client communication sequences"""
    __tablename__ = "smart_nurturing_sequences"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    sequence_name = Column(String(255), nullable=False)
    sequence_type = Column(String(50), nullable=False, index=True)  # 'lead_nurturing', 'client_retention', 'follow_up', 'marketing'
    description = Column(Text)
    triggers = Column(JSON, default=dict)
    steps = Column(JSON, default=list)
    target_audience = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True, index=True)
    performance_metrics = Column(JSON, default=dict)
    total_sent = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_converted = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="nurturing_sequences")
    creator = relationship("User", back_populates="created_nurturing_sequences_ai")
    
    def __repr__(self):
        return f"<SmartNurturingSequence(id={self.id}, name='{self.sequence_name}', type='{self.sequence_type}')>"
    
    @property
    def triggers_dict(self):
        """Get triggers as dictionary"""
        try:
            return json.loads(self.triggers) if isinstance(self.triggers, str) else self.triggers
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def steps_list(self):
        """Get steps as list"""
        try:
            return json.loads(self.steps) if isinstance(self.steps, str) else self.steps
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def target_audience_dict(self):
        """Get target audience as dictionary"""
        try:
            return json.loads(self.target_audience) if isinstance(self.target_audience, str) else self.target_audience
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def performance_metrics_dict(self):
        """Get performance metrics as dictionary"""
        try:
            return json.loads(self.performance_metrics) if isinstance(self.performance_metrics, str) else self.performance_metrics
        except (json.JSONDecodeError, TypeError):
            return {}

class DubaiPropertyData(Base):
    """Integrated Dubai real estate data"""
    __tablename__ = "dubai_property_data"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=True)
    rera_number = Column(String(50), unique=True, index=True)
    property_type = Column(String(50), index=True)  # 'apartment', 'villa', 'townhouse', 'office', 'retail'
    location_area = Column(String(100), index=True)  # 'Dubai Marina', 'Palm Jumeirah', etc.
    market_data = Column(JSON, default=dict)
    price_history = Column(JSON, default=list)
    neighborhood_data = Column(JSON, default=dict)
    rera_compliance_status = Column(String(20), default='unknown', index=True)  # 'compliant', 'non_compliant', 'unknown'
    last_market_update = Column(DateTime)
    data_source = Column(String(100))
    data_quality_score = Column(DECIMAL(3, 2), default=1.00)  # 0.00-1.00
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    # property_obj = relationship("Property", back_populates="dubai_data")  # Commented out - Property class not accessible
    
    def __repr__(self):
        return f"<DubaiPropertyData(id={self.id}, rera_number='{self.rera_number}', area='{self.location_area}')>"
    
    @property
    def market_data_dict(self):
        """Get market data as dictionary"""
        try:
            return json.loads(self.market_data) if isinstance(self.market_data, str) else self.market_data
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def price_history_list(self):
        """Get price history as list"""
        try:
            return json.loads(self.price_history) if isinstance(self.price_history, str) else self.price_history
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def neighborhood_data_dict(self):
        """Get neighborhood data as dictionary"""
        try:
            return json.loads(self.neighborhood_data) if isinstance(self.neighborhood_data, str) else self.neighborhood_data
        except (json.JSONDecodeError, TypeError):
            return {}

class RERAComplianceData(Base):
    """RERA compliance status and requirements"""
    __tablename__ = "rera_compliance_data"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    compliance_status = Column(String(20), default='pending', index=True)  # 'compliant', 'non_compliant', 'pending', 'exempt'
    compliance_type = Column(String(50), index=True)  # 'listing', 'transaction', 'disclosure', 'documentation'
    required_documents = Column(JSON, default=list)
    submitted_documents = Column(JSON, default=list)
    compliance_score = Column(DECIMAL(3, 2))  # 0.00-1.00
    last_check = Column(DateTime)
    next_check = Column(DateTime, index=True)
    compliance_notes = Column(Text)
    regulatory_updates = Column(JSON, default=list)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    # property_obj = relationship("Property", back_populates="rera_compliance")  # Commented out - Property class not accessible
    brokerage = relationship("Brokerage", back_populates="rera_compliance_data")
    
    def __repr__(self):
        return f"<RERAComplianceData(id={self.id}, property_id={self.property_id}, status='{self.compliance_status}')>"
    
    @property
    def required_documents_list(self):
        """Get required documents as list"""
        try:
            return json.loads(self.required_documents) if isinstance(self.required_documents, str) else self.required_documents
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def submitted_documents_list(self):
        """Get submitted documents as list"""
        try:
            return json.loads(self.submitted_documents) if isinstance(self.submitted_documents, str) else self.submitted_documents
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def regulatory_updates_list(self):
        """Get regulatory updates as list"""
        try:
            return json.loads(self.regulatory_updates) if isinstance(self.regulatory_updates, str) else self.regulatory_updates
        except (json.JSONDecodeError, TypeError):
            return []

class RetentionAnalytic(Base):
    """Lead retention and conversion metrics"""
    __tablename__ = "retention_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)  # 'lead_conversion', 'client_retention', 'follow_up_success'
    metric_value = Column(DECIMAL(10, 2), nullable=False)
    metric_unit = Column(String(20))  # 'percentage', 'count', 'days', 'currency'
    period = Column(String(20), nullable=False, index=True)  # 'daily', 'weekly', 'monthly', 'quarterly'
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    benchmark_value = Column(DECIMAL(10, 2))  # Industry benchmark for comparison
    trend_direction = Column(String(10))  # 'up', 'down', 'stable'
    trend_percentage = Column(DECIMAL(5, 2))  # Percentage change from previous period
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="retention_analytics")
    
    def __repr__(self):
        return f"<RetentionAnalytic(id={self.id}, metric='{self.metric_name}', value={self.metric_value})>"
    
    @property
    def metadata_dict(self):
        """Get metadata as dictionary"""
        try:
            return json.loads(self.metadata_json) if isinstance(self.metadata_json, str) else self.metadata_json
        except (json.JSONDecodeError, TypeError):
            return {}
