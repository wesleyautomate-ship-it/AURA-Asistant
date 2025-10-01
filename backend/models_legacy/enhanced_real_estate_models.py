"""
Enhanced Real Estate Models
===========================

SQLAlchemy models for the enhanced real estate system including:
- Enhanced property management
- Advanced lead nurturing
- Market data integration
- Transaction management
- Compliance tracking
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, DECIMAL, JSON, Date, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import json

from . import Base

class EnhancedProperty(Base):
    """Enhanced property model with comprehensive real estate data"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    property_type = Column(String(50), index=True)
    price = Column(DECIMAL(15,2))  # Legacy field
    price_aed = Column(DECIMAL(15,2), index=True)  # Enhanced field
    location = Column(String(255), index=True)
    area_sqft = Column(DECIMAL(10,2))
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    
    # Enhanced fields
    listing_status = Column(String(20), default='draft', index=True)
    features = Column(JSON, default=dict)
    agent_id = Column(Integer, ForeignKey('users.id'), index=True)
    is_deleted = Column(Boolean, default=False, index=True)
    market_data = Column(JSON, default=dict)
    neighborhood_data = Column(JSON, default=dict)
    property_images = Column(JSON, default=list)
    floor_plan_url = Column(String(500))
    virtual_tour_url = Column(String(500))
    rera_number = Column(String(50), index=True)
    developer_name = Column(String(255), index=True)
    completion_date = Column(Date)
    maintenance_fee = Column(DECIMAL(10,2))
    parking_spaces = Column(Integer)
    balcony_area = Column(DECIMAL(8,2))
    view_type = Column(String(100))
    furnishing_status = Column(String(50))
    pet_friendly = Column(Boolean, default=False)
    gym_available = Column(Boolean, default=False)
    pool_available = Column(Boolean, default=False)
    security_24_7 = Column(Boolean, default=False)
    
    # Legacy fields
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    agent = relationship("User", foreign_keys=[agent_id], back_populates="managed_properties")
    creator = relationship("User", foreign_keys=[created_by])
    transactions = relationship("Transaction", back_populates="property")
    viewings = relationship("PropertyViewing", back_populates="property")
    compliance_records = relationship("RERACompliance", back_populates="property")
    
    def __repr__(self):
        return f"<EnhancedProperty(id={self.id}, title='{self.title}', price_aed={self.price_aed})>"
    
    @property
    def features_dict(self):
        """Get features as dictionary"""
        try:
            return json.loads(self.features) if isinstance(self.features, str) else self.features
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def market_data_dict(self):
        """Get market data as dictionary"""
        try:
            return json.loads(self.market_data) if isinstance(self.market_data, str) else self.market_data
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def neighborhood_data_dict(self):
        """Get neighborhood data as dictionary"""
        try:
            return json.loads(self.neighborhood_data) if isinstance(self.neighborhood_data, str) else self.neighborhood_data
        except (json.JSONDecodeError, TypeError):
            return {}

class EnhancedLead(Base):
    """Enhanced lead model with nurturing and automation capabilities"""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50), index=True)
    status = Column(String(50), default='new', index=True)
    source = Column(String(100))
    budget_min = Column(DECIMAL(12,2))
    budget_max = Column(DECIMAL(12,2))
    preferred_areas = Column(JSON, default=list)
    property_type = Column(String(100))
    last_contacted = Column(DateTime)
    notes = Column(Text)
    
    # Enhanced fields
    nurture_status = Column(String(20), default='new', index=True)
    assigned_agent_id = Column(Integer, ForeignKey('users.id'), index=True)
    last_contacted_at = Column(DateTime, index=True)
    next_follow_up_at = Column(DateTime, index=True)
    lead_score = Column(Integer, default=0, index=True)
    source_details = Column(JSON, default=dict)
    preferred_contact_method = Column(String(20), default='email')
    timezone = Column(String(50), default='Asia/Dubai')
    language_preference = Column(String(10), default='en')
    urgency_level = Column(String(20), default='normal', index=True)
    decision_timeline = Column(String(50))
    financing_status = Column(String(50))
    viewing_history = Column(JSON, default=list)
    communication_preferences = Column(JSON, default=dict)
    lead_source_campaign = Column(String(100))
    lead_source_medium = Column(String(50))
    lead_source_content = Column(String(100))
    
    # Legacy fields
    agent_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id], back_populates="assigned_leads")
    legacy_agent = relationship("User", foreign_keys=[agent_id])
    lead_history = relationship("LeadHistory", back_populates="lead", cascade="all, delete-orphan")
    viewings = relationship("PropertyViewing", back_populates="lead")
    appointments = relationship("Appointment", back_populates="lead")
    client = relationship("EnhancedClient", back_populates="lead", uselist=False)
    
    def __repr__(self):
        return f"<EnhancedLead(id={self.id}, name='{self.name}', nurture_status='{self.nurture_status}')>"
    
    @property
    def preferred_areas_list(self):
        """Get preferred areas as list"""
        try:
            return json.loads(self.preferred_areas) if isinstance(self.preferred_areas, str) else self.preferred_areas
        except (json.JSONDecodeError, TypeError):
            return []
    
    @property
    def source_details_dict(self):
        """Get source details as dictionary"""
        try:
            return json.loads(self.source_details) if isinstance(self.source_details, str) else self.source_details
        except (json.JSONDecodeError, TypeError):
            return {}

class EnhancedClient(Base):
    """Enhanced client model with relationship management"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(50), index=True)
    budget_min = Column(DECIMAL(12,2))
    budget_max = Column(DECIMAL(12,2))
    preferred_location = Column(String(255))
    requirements = Column(Text)
    
    # Enhanced fields
    client_type = Column(String(20), default='buyer', index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), index=True)
    assigned_agent_id = Column(Integer, ForeignKey('users.id'), index=True)
    client_status = Column(String(20), default='active', index=True)
    relationship_start_date = Column(Date)
    total_transactions = Column(Integer, default=0)
    total_value = Column(DECIMAL(15,2), default=0)
    client_tier = Column(String(20), default='standard', index=True)
    referral_source = Column(String(100))
    communication_history = Column(JSON, default=list)
    preferences = Column(JSON, default=dict)
    documents = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    lead = relationship("EnhancedLead", back_populates="client")
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id], back_populates="assigned_clients")
    transactions = relationship("Transaction", back_populates="buyer")
    appointments = relationship("Appointment", back_populates="client")
    
    def __repr__(self):
        return f"<EnhancedClient(id={self.id}, name='{self.name}', client_type='{self.client_type}')>"

class MarketData(Base):
    """Market data for Dubai real estate areas"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area = Column(String(100), nullable=False, index=True)
    property_type = Column(String(50), nullable=False, index=True)
    avg_price = Column(DECIMAL(15,2))
    price_per_sqft = Column(DECIMAL(10,2))
    market_trend = Column(String(20), index=True)
    data_date = Column(Date, nullable=False, index=True)
    source = Column(String(100))
    market_context = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<MarketData(area='{self.area}', property_type='{self.property_type}', avg_price={self.avg_price})>"

class NeighborhoodProfile(Base):
    """Neighborhood profiles for Dubai areas"""
    __tablename__ = "neighborhood_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    area_name = Column(String(100), nullable=False, unique=True, index=True)
    amenities = Column(JSON, default=dict)
    demographics = Column(JSON, default=dict)
    transportation_score = Column(Integer)
    safety_rating = Column(Integer)
    investment_potential = Column(String(20), index=True)
    average_rental_yield = Column(DECIMAL(5,2))
    population_density = Column(Integer)
    average_age = Column(DECIMAL(4,1))
    family_friendly_score = Column(Integer)
    nightlife_score = Column(Integer)
    shopping_score = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<NeighborhoodProfile(area_name='{self.area_name}', investment_potential='{self.investment_potential}')>"

class Transaction(Base):
    """Transaction management for real estate deals"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey('properties.id'), index=True)
    buyer_id = Column(Integer, ForeignKey('clients.id'), index=True)
    seller_id = Column(Integer, ForeignKey('clients.id'))
    agent_id = Column(Integer, ForeignKey('users.id'), index=True)
    transaction_type = Column(String(20), nullable=False, index=True)
    transaction_status = Column(String(20), default='pending', index=True)
    offer_price = Column(DECIMAL(15,2))
    final_price = Column(DECIMAL(15,2))
    commission_rate = Column(DECIMAL(5,2))
    commission_amount = Column(DECIMAL(15,2))
    transaction_date = Column(Date, index=True)
    closing_date = Column(Date)
    contract_signed_date = Column(Date)
    payment_terms = Column(JSON, default=dict)
    documents = Column(JSON, default=list)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    property = relationship("EnhancedProperty", back_populates="transactions")
    buyer = relationship("EnhancedClient", foreign_keys=[buyer_id], back_populates="transactions")
    seller = relationship("EnhancedClient", foreign_keys=[seller_id])
    agent = relationship("User", back_populates="transactions")
    transaction_history = relationship("TransactionHistory", back_populates="transaction", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.transaction_type}', status='{self.transaction_status}')>"

class TransactionHistory(Base):
    """Transaction history tracking"""
    __tablename__ = "transaction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False, index=True)
    status_change = Column(String(50), nullable=False)
    previous_status = Column(String(20))
    new_status = Column(String(20))
    changed_by = Column(Integer, ForeignKey('users.id'))
    change_reason = Column(Text)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    transaction = relationship("Transaction", back_populates="transaction_history")
    changed_by_user = relationship("User")
    
    def __repr__(self):
        return f"<TransactionHistory(id={self.id}, transaction_id={self.transaction_id}, change='{self.status_change}')>"

class PropertyViewing(Base):
    """Property viewing management"""
    __tablename__ = "property_viewings"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey('properties.id'), index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), index=True)
    agent_id = Column(Integer, ForeignKey('users.id'), index=True)
    viewing_date = Column(DateTime, nullable=False, index=True)
    viewing_status = Column(String(20), default='scheduled', index=True)
    viewing_type = Column(String(20), default='in_person')
    feedback = Column(Text)
    interest_level = Column(Integer)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    property = relationship("EnhancedProperty", back_populates="viewings")
    lead = relationship("EnhancedLead", back_populates="viewings")
    agent = relationship("User", back_populates="property_viewings")
    
    def __repr__(self):
        return f"<PropertyViewing(id={self.id}, property_id={self.property_id}, viewing_date={self.viewing_date})>"

class Appointment(Base):
    """Appointment management"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('users.id'), index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), index=True)
    lead_id = Column(Integer, ForeignKey('leads.id'), index=True)
    appointment_type = Column(String(50), nullable=False, index=True)
    appointment_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    location = Column(String(255))
    meeting_link = Column(String(500))
    status = Column(String(20), default='scheduled', index=True)
    agenda = Column(Text)
    notes = Column(Text)
    outcome = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    agent = relationship("User", back_populates="appointments")
    client = relationship("EnhancedClient", back_populates="appointments")
    lead = relationship("EnhancedLead", back_populates="appointments")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, type='{self.appointment_type}', date={self.appointment_date})>"

class RERACompliance(Base):
    """RERA compliance tracking"""
    __tablename__ = "rera_compliance"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey('properties.id'), index=True)
    compliance_status = Column(String(20), default='unknown', index=True)
    rera_number = Column(String(50))
    compliance_check_date = Column(Date)
    compliance_notes = Column(Text)
    required_actions = Column(JSON, default=list)
    compliance_officer = Column(String(255))
    next_review_date = Column(Date, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    property = relationship("EnhancedProperty", back_populates="compliance_records")
    
    def __repr__(self):
        return f"<RERACompliance(id={self.id}, property_id={self.property_id}, status='{self.compliance_status}')>"

class DocumentManagement(Base):
    """Document management system"""
    __tablename__ = "document_management"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    document_type = Column(String(50), nullable=False, index=True)
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    upload_date = Column(DateTime, default=func.now())
    uploaded_by = Column(Integer, ForeignKey('users.id'))
    is_required = Column(Boolean, default=False)
    expiry_date = Column(Date, index=True)
    status = Column(String(20), default='active', index=True)
    metadata_json = Column(JSON, default=dict)
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_documents")
    
    def __repr__(self):
        return f"<DocumentManagement(id={self.id}, entity_type='{self.entity_type}', document_name='{self.document_name}')>"

# Add check constraints
__table_args__ = (
    CheckConstraint('price_aed >= 0', name='chk_properties_price_aed_positive'),
    CheckConstraint("listing_status IN ('draft', 'live', 'sold', 'withdrawn', 'pending')", name='chk_properties_listing_status'),
    CheckConstraint('bedrooms >= 0', name='chk_properties_bedrooms_positive'),
    CheckConstraint('bathrooms >= 0', name='chk_properties_bathrooms_positive'),
    CheckConstraint("nurture_status IN ('new', 'hot', 'warm', 'cold', 'qualified', 'unqualified')", name='chk_leads_nurture_status'),
    CheckConstraint('lead_score >= 0 AND lead_score <= 100', name='chk_leads_lead_score'),
    CheckConstraint("urgency_level IN ('low', 'normal', 'high', 'urgent')", name='chk_leads_urgency_level'),
    CheckConstraint("client_type IN ('buyer', 'seller', 'investor', 'tenant', 'landlord')", name='chk_clients_client_type'),
    CheckConstraint("client_status IN ('active', 'inactive', 'prospect', 'closed')", name='chk_clients_client_status'),
    CheckConstraint("transaction_type IN ('sale', 'rental', 'lease', 'investment')", name='chk_transactions_type'),
    CheckConstraint("transaction_status IN ('pending', 'in_progress', 'completed', 'cancelled', 'on_hold')", name='chk_transactions_status'),
)
