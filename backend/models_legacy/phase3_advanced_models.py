"""
Phase 3 Advanced Models
======================

SQLAlchemy models for Phase 3 advanced features including:
- Predictive performance models
- Benchmarking data
- Dubai market data integration
- System performance metrics
- User activity analytics
- Multi-brokerage analytics
- Developer panel settings
- System alerts
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, DECIMAL, JSON, Date, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import json

from . import Base

class PredictivePerformanceModel(Base):
    """ML models for predicting agent and brokerage performance"""
    __tablename__ = "predictive_performance_models"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=True, index=True)
    model_type = Column(String(50), nullable=False, index=True)  # 'agent_performance', 'lead_conversion', 'market_trend', 'client_retention'
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(20), default='1.0.0')
    parameters = Column(JSON, default=dict)  # Model hyperparameters and configuration
    training_data_period_start = Column(Date, nullable=False)
    training_data_period_end = Column(Date, nullable=False)
    accuracy_score = Column(DECIMAL(5, 4))  # 0.0000-1.0000
    precision_score = Column(DECIMAL(5, 4))
    recall_score = Column(DECIMAL(5, 4))
    f1_score = Column(DECIMAL(5, 4))
    model_file_path = Column(String(500))
    feature_importance = Column(JSON, default=dict)  # Feature importance scores
    is_active = Column(Boolean, default=True, index=True)
    last_trained = Column(DateTime, default=func.now(), index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="predictive_models")
    
    def __repr__(self):
        return f"<PredictivePerformanceModel(id={self.id}, type='{self.model_type}', name='{self.model_name}')>"
    
    @property
    def parameters_dict(self):
        """Get parameters as dictionary"""
        try:
            return json.loads(self.parameters) if isinstance(self.parameters, str) else self.parameters
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def feature_importance_dict(self):
        """Get feature importance as dictionary"""
        try:
            return json.loads(self.feature_importance) if isinstance(self.feature_importance, str) else self.feature_importance
        except (json.JSONDecodeError, TypeError):
            return {}

class BenchmarkingData(Base):
    """Industry benchmarks and performance comparisons"""
    __tablename__ = "benchmarking_data"
    
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    benchmark_type = Column(String(50), nullable=False, index=True)  # 'agent_performance', 'lead_conversion', 'client_retention', 'market_share'
    metric_name = Column(String(100), nullable=False)
    industry_standard = Column(DECIMAL(10, 2))  # Industry average/standard
    top_performer_standard = Column(DECIMAL(10, 2))  # Top 10% performer standard
    brokerage_performance = Column(DECIMAL(10, 2))  # Current brokerage performance
    performance_gap = Column(DECIMAL(10, 2))  # Gap from industry standard
    percentile_ranking = Column(Integer)  # Percentile ranking (1-100)
    benchmark_period_start = Column(Date, nullable=False, index=True)
    benchmark_period_end = Column(Date, nullable=False, index=True)
    data_source = Column(String(100))  # Source of benchmark data
    confidence_level = Column(DECIMAL(3, 2), default=0.95)  # Statistical confidence
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    brokerage = relationship("Brokerage", back_populates="benchmarking_data")
    
    def __repr__(self):
        return f"<BenchmarkingData(id={self.id}, type='{self.benchmark_type}', metric='{self.metric_name}')>"
    
    @property
    def metadata_dict(self):
        """Get metadata as dictionary"""
        try:
            return json.loads(self.metadata_json) if isinstance(self.metadata_json, str) else self.metadata_json
        except (json.JSONDecodeError, TypeError):
            return {}

class DubaiMarketData(Base):
    """Integrated Dubai real estate market data from multiple sources"""
    __tablename__ = "dubai_market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_name = Column(String(100), nullable=False, index=True)  # 'Dubai Marina', 'Palm Jumeirah', etc.
    property_type = Column(String(50), nullable=False, index=True)  # 'apartment', 'villa', 'townhouse', 'office', 'retail'
    data_type = Column(String(50), nullable=False, index=True)  # 'price_per_sqft', 'rental_yield', 'occupancy_rate', 'transaction_volume'
    data_value = Column(DECIMAL(15, 2), nullable=False)
    data_unit = Column(String(20))  # 'AED', 'percentage', 'count', 'sqft'
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    data_source = Column(String(100), nullable=False)  # 'RERA', 'Dubai Land Department', 'Property Finder', 'Bayut'
    data_quality_score = Column(DECIMAL(3, 2), default=1.00)  # Data quality assessment
    is_verified = Column(Boolean, default=False)  # Data verification status
    last_updated = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<DubaiMarketData(id={self.id}, area='{self.area_name}', type='{self.data_type}', value={self.data_value})>"

class RERAIntegrationData(Base):
    """RERA-specific data and compliance information"""
    __tablename__ = "rera_integration_data"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey('properties.id'), nullable=True)
    rera_number = Column(String(50), unique=True, nullable=False, index=True)
    developer_name = Column(String(255))
    project_name = Column(String(255))
    completion_status = Column(String(50))  # 'completed', 'under_construction', 'planned'
    handover_date = Column(Date)
    rera_approval_date = Column(Date)
    escrow_account_number = Column(String(100))
    escrow_bank = Column(String(255))
    payment_plan = Column(JSON, default=dict)  # Payment plan details
    amenities = Column(JSON, default=list)  # Project amenities
    nearby_facilities = Column(JSON, default=list)  # Nearby facilities and services
    transportation_links = Column(JSON, default=list)  # Metro, bus, road connections
    compliance_status = Column(String(20), default='compliant', index=True)  # 'compliant', 'non_compliant', 'pending'
    last_rera_check = Column(DateTime)
    rera_notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    # property_obj = relationship("Property", back_populates="rera_integration")  # Commented out - Property class not accessible
    
    def __repr__(self):
        return f"<RERAIntegrationData(id={self.id}, rera_number='{self.rera_number}', status='{self.compliance_status}')>"
    
    @property
    def payment_plan_dict(self):
        """Get payment plan as dictionary"""
        try:
            return json.loads(self.payment_plan) if isinstance(self.payment_plan, str) else self.payment_plan
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def amenities_list(self):
        """Get amenities as list"""
        try:
            return json.loads(self.amenities) if isinstance(self.amenities, str) else self.amenities
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def nearby_facilities_list(self):
        """Get nearby facilities as list"""
        try:
            return json.loads(self.nearby_facilities) if isinstance(self.nearby_facilities, str) else self.nearby_facilities
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def transportation_links_list(self):
        """Get transportation links as list"""
        try:
            return json.loads(self.transportation_links) if isinstance(self.transportation_links, str) else self.transportation_links
        except (json.JSONDecodeError, TypeError):
            return []

class SystemPerformanceMetric(Base):
    """System-wide performance and usage metrics"""
    __tablename__ = "system_performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_category = Column(String(50), nullable=False, index=True)  # 'api_performance', 'database_performance', 'ai_processing', 'user_activity'
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 4), nullable=False)
    metric_unit = Column(String(20))  # 'milliseconds', 'requests_per_second', 'percentage', 'count'
    measurement_timestamp = Column(DateTime, default=func.now(), index=True)
    additional_data = Column(JSON, default=dict)  # Additional context data
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<SystemPerformanceMetric(id={self.id}, category='{self.metric_category}', name='{self.metric_name}')>"
    
    @property
    def additional_data_dict(self):
        """Get additional data as dictionary"""
        try:
            return json.loads(self.additional_data) if isinstance(self.additional_data, str) else self.additional_data
        except (json.JSONDecodeError, TypeError):
            return {}

class UserActivityAnalytic(Base):
    """Detailed user activity and behavior analytics"""
    __tablename__ = "user_activity_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    brokerage_id = Column(Integer, ForeignKey('brokerages.id'), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False, index=True)  # 'login', 'request_creation', 'content_download', 'expert_review'
    activity_details = Column(JSON, default=dict)  # Detailed activity information
    session_id = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_type = Column(String(50))  # 'desktop', 'mobile', 'tablet'
    browser_type = Column(String(50))
    duration_seconds = Column(Integer)  # Activity duration
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="activity_analytics")
    brokerage = relationship("Brokerage", back_populates="activity_analytics")
    
    def __repr__(self):
        return f"<UserActivityAnalytic(id={self.id}, user_id={self.user_id}, activity='{self.activity_type}')>"
    
    @property
    def activity_details_dict(self):
        """Get activity details as dictionary"""
        try:
            return json.loads(self.activity_details) if isinstance(self.activity_details, str) else self.activity_details
        except (json.JSONDecodeError, TypeError):
            return {}

class AIProcessingAnalytic(Base):
    """AI processing performance and quality metrics"""
    __tablename__ = "ai_processing_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey('ai_requests.id'), nullable=False, index=True)
    processing_stage = Column(String(50), nullable=False, index=True)  # 'request_analysis', 'ai_generation', 'human_review', 'content_delivery'
    processing_time_ms = Column(Integer, nullable=False)  # Processing time in milliseconds
    ai_model_used = Column(String(100))
    ai_confidence_score = Column(DECIMAL(3, 2))
    human_review_time_ms = Column(Integer)
    human_rating = Column(Integer)  # 1-5 rating
    quality_score = Column(DECIMAL(3, 2))
    error_occurred = Column(Boolean, default=False)
    error_type = Column(String(100))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    request = relationship("AIRequest", back_populates="processing_analytics")
    
    def __repr__(self):
        return f"<AIProcessingAnalytic(id={self.id}, request_id={self.request_id}, stage='{self.processing_stage}')>"

class MultiBrokerageAnalytic(Base):
    """Cross-brokerage analytics for system-wide insights"""
    __tablename__ = "multi_brokerage_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    analytics_type = Column(String(50), nullable=False, index=True)  # 'system_usage', 'feature_adoption', 'performance_comparison', 'market_insights'
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(DECIMAL(15, 4), nullable=False)
    metric_unit = Column(String(20))
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    brokerage_count = Column(Integer)  # Number of brokerages included
    total_users = Column(Integer)  # Total users across brokerages
    additional_metrics = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<MultiBrokerageAnalytic(id={self.id}, type='{self.analytics_type}', metric='{self.metric_name}')>"
    
    @property
    def additional_metrics_dict(self):
        """Get additional metrics as dictionary"""
        try:
            return json.loads(self.additional_metrics) if isinstance(self.additional_metrics, str) else self.additional_metrics
        except (json.JSONDecodeError, TypeError):
            return {}

class DeveloperPanelSetting(Base):
    """Developer panel configuration and preferences"""
    __tablename__ = "developer_panel_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    setting_category = Column(String(50), nullable=False, index=True)  # 'monitoring', 'alerts', 'analytics', 'system_control'
    setting_name = Column(String(100), nullable=False)
    setting_value = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="developer_settings")
    
    def __repr__(self):
        return f"<DeveloperPanelSetting(id={self.id}, user_id={self.user_id}, category='{self.setting_category}')>"
    
    @property
    def setting_value_dict(self):
        """Get setting value as dictionary"""
        try:
            return json.loads(self.setting_value) if isinstance(self.setting_value, str) else self.setting_value
        except (json.JSONDecodeError, TypeError):
            return {}

class SystemAlert(Base):
    """System alerts and notifications for developers"""
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # 'error', 'warning', 'info', 'performance'
    alert_category = Column(String(50), nullable=False, index=True)  # 'system', 'database', 'ai_processing', 'user_activity'
    alert_title = Column(String(255), nullable=False)
    alert_message = Column(Text, nullable=False)
    severity = Column(String(20), default='medium', index=True)  # 'low', 'medium', 'high', 'critical'
    affected_components = Column(JSON, default=list)  # List of affected system components
    alert_data = Column(JSON, default=dict)  # Additional alert context
    is_resolved = Column(Boolean, default=False, index=True)
    resolved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f"<SystemAlert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
    
    @property
    def affected_components_list(self):
        """Get affected components as list"""
        try:
            return json.loads(self.affected_components) if isinstance(self.affected_components, str) else self.affected_components
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def alert_data_dict(self):
        """Get alert data as dictionary"""
        try:
            return json.loads(self.alert_data) if isinstance(self.alert_data, str) else self.alert_data
        except (json.JSONDecodeError, TypeError):
            return {}
