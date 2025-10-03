-- ============================================================
-- SCHEMA ENHANCEMENT MIGRATION
-- Addresses critical gaps in database schema for real estate workflow
-- ============================================================

-- ============================================================
-- 1. PROPERTY SCHEMA ENHANCEMENTS
-- ============================================================

-- Add missing critical fields to properties table
ALTER TABLE properties ADD COLUMN IF NOT EXISTS price_aed DECIMAL(15,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS listing_status VARCHAR(20) DEFAULT 'draft';
ALTER TABLE properties ADD COLUMN IF NOT EXISTS features JSONB DEFAULT '{}';
ALTER TABLE properties ADD COLUMN IF NOT EXISTS agent_id INTEGER REFERENCES users(id);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS market_data JSONB DEFAULT '{}';
ALTER TABLE properties ADD COLUMN IF NOT EXISTS neighborhood_data JSONB DEFAULT '{}';
ALTER TABLE properties ADD COLUMN IF NOT EXISTS property_images JSONB DEFAULT '[]';
ALTER TABLE properties ADD COLUMN IF NOT EXISTS floor_plan_url VARCHAR(500);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS virtual_tour_url VARCHAR(500);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS rera_number VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS developer_name VARCHAR(255);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS completion_date DATE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS maintenance_fee DECIMAL(10,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS parking_spaces INTEGER;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS balcony_area DECIMAL(8,2);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS view_type VARCHAR(100);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS furnishing_status VARCHAR(50);
ALTER TABLE properties ADD COLUMN IF NOT EXISTS pet_friendly BOOLEAN DEFAULT FALSE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS gym_available BOOLEAN DEFAULT FALSE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS pool_available BOOLEAN DEFAULT FALSE;
ALTER TABLE properties ADD COLUMN IF NOT EXISTS security_24_7 BOOLEAN DEFAULT FALSE;

-- Update existing price field to price_aed if not already set
UPDATE properties SET price_aed = price WHERE price_aed IS NULL AND price IS NOT NULL;

-- ============================================================
-- 2. LEAD MANAGEMENT ENHANCEMENTS
-- ============================================================

-- Add missing lead nurturing and automation fields
ALTER TABLE leads ADD COLUMN IF NOT EXISTS nurture_status VARCHAR(20) DEFAULT 'new';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS assigned_agent_id INTEGER REFERENCES users(id);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_contacted_at TIMESTAMP;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS next_follow_up_at TIMESTAMP;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS lead_score INTEGER DEFAULT 0;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS source_details JSONB DEFAULT '{}';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS preferred_contact_method VARCHAR(20) DEFAULT 'email';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Asia/Dubai';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS language_preference VARCHAR(10) DEFAULT 'en';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS urgency_level VARCHAR(20) DEFAULT 'normal';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS decision_timeline VARCHAR(50);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS financing_status VARCHAR(50);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS viewing_history JSONB DEFAULT '[]';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS communication_preferences JSONB DEFAULT '{}';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS lead_source_campaign VARCHAR(100);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS lead_source_medium VARCHAR(50);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS lead_source_content VARCHAR(100);

-- ============================================================
-- 3. CLIENT MANAGEMENT ENHANCEMENTS
-- ============================================================

-- Enhance clients table to distinguish from leads
ALTER TABLE clients ADD COLUMN IF NOT EXISTS client_type VARCHAR(20) DEFAULT 'buyer';
ALTER TABLE clients ADD COLUMN IF NOT EXISTS lead_id INTEGER REFERENCES leads(id);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS assigned_agent_id INTEGER REFERENCES users(id);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS client_status VARCHAR(20) DEFAULT 'active';
ALTER TABLE clients ADD COLUMN IF NOT EXISTS relationship_start_date DATE;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS total_transactions INTEGER DEFAULT 0;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS total_value DECIMAL(15,2) DEFAULT 0;
ALTER TABLE clients ADD COLUMN IF NOT EXISTS client_tier VARCHAR(20) DEFAULT 'standard';
ALTER TABLE clients ADD COLUMN IF NOT EXISTS referral_source VARCHAR(100);
ALTER TABLE clients ADD COLUMN IF NOT EXISTS communication_history JSONB DEFAULT '[]';
ALTER TABLE clients ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}';
ALTER TABLE clients ADD COLUMN IF NOT EXISTS documents JSONB DEFAULT '[]';

-- ============================================================
-- 4. MARKET DATA INTEGRATION TABLES
-- ============================================================

-- Market Data Table
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    area VARCHAR(100) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    avg_price DECIMAL(15,2),
    price_per_sqft DECIMAL(10,2),
    market_trend VARCHAR(20), -- 'rising', 'stable', 'declining'
    data_date DATE NOT NULL,
    source VARCHAR(100),
    market_context JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(area, property_type, data_date)
);

-- Neighborhood Profiles Table
CREATE TABLE IF NOT EXISTS neighborhood_profiles (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(100) NOT NULL UNIQUE,
    amenities JSONB DEFAULT '{}',
    demographics JSONB DEFAULT '{}',
    transportation_score INTEGER CHECK (transportation_score >= 1 AND transportation_score <= 10),
    safety_rating INTEGER CHECK (safety_rating >= 1 AND safety_rating <= 10),
    investment_potential VARCHAR(20), -- 'high', 'medium', 'low'
    average_rental_yield DECIMAL(5,2),
    population_density INTEGER,
    average_age DECIMAL(4,1),
    family_friendly_score INTEGER CHECK (family_friendly_score >= 1 AND family_friendly_score <= 10),
    nightlife_score INTEGER CHECK (nightlife_score >= 1 AND nightlife_score <= 10),
    shopping_score INTEGER CHECK (shopping_score >= 1 AND shopping_score <= 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. TRANSACTION MANAGEMENT TABLES
-- ============================================================

-- Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    buyer_id INTEGER REFERENCES clients(id),
    seller_id INTEGER REFERENCES clients(id),
    agent_id INTEGER REFERENCES users(id),
    transaction_type VARCHAR(20) NOT NULL, -- 'sale', 'rental', 'lease'
    transaction_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'cancelled'
    offer_price DECIMAL(15,2),
    final_price DECIMAL(15,2),
    commission_rate DECIMAL(5,2),
    commission_amount DECIMAL(15,2),
    transaction_date DATE,
    closing_date DATE,
    contract_signed_date DATE,
    payment_terms JSONB DEFAULT '{}',
    documents JSONB DEFAULT '[]',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction History Table
CREATE TABLE IF NOT EXISTS transaction_history (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    status_change VARCHAR(50) NOT NULL,
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    changed_by INTEGER REFERENCES users(id),
    change_reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. VIEWING AND APPOINTMENT MANAGEMENT
-- ============================================================

-- Property Viewings Table
CREATE TABLE IF NOT EXISTS property_viewings (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    lead_id INTEGER REFERENCES leads(id),
    agent_id INTEGER REFERENCES users(id),
    viewing_date TIMESTAMP NOT NULL,
    viewing_status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled', 'rescheduled'
    viewing_type VARCHAR(20) DEFAULT 'in_person', -- 'in_person', 'virtual', 'video_call'
    feedback TEXT,
    interest_level INTEGER CHECK (interest_level >= 1 AND interest_level <= 10),
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Appointments Table
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES users(id),
    client_id INTEGER REFERENCES clients(id),
    lead_id INTEGER REFERENCES leads(id),
    appointment_type VARCHAR(50) NOT NULL, -- 'meeting', 'call', 'viewing', 'presentation'
    appointment_date TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    location VARCHAR(255),
    meeting_link VARCHAR(500),
    status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled', 'rescheduled'
    agenda TEXT,
    notes TEXT,
    outcome TEXT,
    follow_up_required BOOLEAN DEFAULT FALSE,
    follow_up_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 7. COMPLIANCE AND REGULATORY TABLES
-- ============================================================

-- RERA Compliance Table
CREATE TABLE IF NOT EXISTS rera_compliance (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES properties(id),
    compliance_status VARCHAR(20) DEFAULT 'unknown', -- 'compliant', 'non_compliant', 'unknown', 'pending'
    rera_number VARCHAR(50),
    compliance_check_date DATE,
    compliance_notes TEXT,
    required_actions JSONB DEFAULT '[]',
    compliance_officer VARCHAR(255),
    next_review_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document Management Table
CREATE TABLE IF NOT EXISTS document_management (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL, -- 'property', 'lead', 'client', 'transaction'
    entity_id INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INTEGER REFERENCES users(id),
    is_required BOOLEAN DEFAULT FALSE,
    expiry_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'expired', 'archived'
    metadata JSONB DEFAULT '{}'
);

-- ============================================================
-- 8. PERFORMANCE INDEXES
-- ============================================================

-- Property indexes
CREATE INDEX IF NOT EXISTS idx_properties_price_aed ON properties(price_aed);
CREATE INDEX IF NOT EXISTS idx_properties_listing_status ON properties(listing_status);
CREATE INDEX IF NOT EXISTS idx_properties_agent_id ON properties(agent_id);
CREATE INDEX IF NOT EXISTS idx_properties_features_gin ON properties USING GIN (features);
CREATE INDEX IF NOT EXISTS idx_properties_market_data_gin ON properties USING GIN (market_data);
CREATE INDEX IF NOT EXISTS idx_properties_neighborhood_data_gin ON properties USING GIN (neighborhood_data);
CREATE INDEX IF NOT EXISTS idx_properties_is_deleted ON properties(is_deleted);
CREATE INDEX IF NOT EXISTS idx_properties_rera_number ON properties(rera_number);
CREATE INDEX IF NOT EXISTS idx_properties_developer_name ON properties(developer_name);

-- Lead indexes
CREATE INDEX IF NOT EXISTS idx_leads_nurture_status ON leads(nurture_status);
CREATE INDEX IF NOT EXISTS idx_leads_assigned_agent_id ON leads(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_leads_next_follow_up_at ON leads(next_follow_up_at);
CREATE INDEX IF NOT EXISTS idx_leads_lead_score ON leads(lead_score);
CREATE INDEX IF NOT EXISTS idx_leads_source_details_gin ON leads USING GIN (source_details);
CREATE INDEX IF NOT EXISTS idx_leads_urgency_level ON leads(urgency_level);
CREATE INDEX IF NOT EXISTS idx_leads_decision_timeline ON leads(decision_timeline);

-- Client indexes
CREATE INDEX IF NOT EXISTS idx_clients_client_type ON clients(client_type);
CREATE INDEX IF NOT EXISTS idx_clients_assigned_agent_id ON clients(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_clients_client_status ON clients(client_status);
CREATE INDEX IF NOT EXISTS idx_clients_client_tier ON clients(client_tier);
CREATE INDEX IF NOT EXISTS idx_clients_lead_id ON clients(lead_id);

-- Market data indexes
CREATE INDEX IF NOT EXISTS idx_market_data_area_type ON market_data(area, property_type);
CREATE INDEX IF NOT EXISTS idx_market_data_date ON market_data(data_date);
CREATE INDEX IF NOT EXISTS idx_market_data_trend ON market_data(market_trend);

-- Neighborhood profiles indexes
CREATE INDEX IF NOT EXISTS idx_neighborhood_profiles_area ON neighborhood_profiles(area_name);
CREATE INDEX IF NOT EXISTS idx_neighborhood_profiles_investment ON neighborhood_profiles(investment_potential);
CREATE INDEX IF NOT EXISTS idx_neighborhood_profiles_amenities_gin ON neighborhood_profiles USING GIN (amenities);

-- Transaction indexes
CREATE INDEX IF NOT EXISTS idx_transactions_property_id ON transactions(property_id);
CREATE INDEX IF NOT EXISTS idx_transactions_buyer_id ON transactions(buyer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_agent_id ON transactions(agent_id);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(transaction_status);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);

-- Viewing indexes
CREATE INDEX IF NOT EXISTS idx_property_viewings_property_id ON property_viewings(property_id);
CREATE INDEX IF NOT EXISTS idx_property_viewings_lead_id ON property_viewings(lead_id);
CREATE INDEX IF NOT EXISTS idx_property_viewings_agent_id ON property_viewings(agent_id);
CREATE INDEX IF NOT EXISTS idx_property_viewings_date ON property_viewings(viewing_date);
CREATE INDEX IF NOT EXISTS idx_property_viewings_status ON property_viewings(viewing_status);

-- Appointment indexes
CREATE INDEX IF NOT EXISTS idx_appointments_agent_id ON appointments(agent_id);
CREATE INDEX IF NOT EXISTS idx_appointments_client_id ON appointments(client_id);
CREATE INDEX IF NOT EXISTS idx_appointments_lead_id ON appointments(lead_id);
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

-- Compliance indexes
CREATE INDEX IF NOT EXISTS idx_rera_compliance_property_id ON rera_compliance(property_id);
CREATE INDEX IF NOT EXISTS idx_rera_compliance_status ON rera_compliance(compliance_status);
CREATE INDEX IF NOT EXISTS idx_rera_compliance_next_review ON rera_compliance(next_review_date);

-- Document management indexes
CREATE INDEX IF NOT EXISTS idx_document_management_entity ON document_management(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_document_management_type ON document_management(document_type);
CREATE INDEX IF NOT EXISTS idx_document_management_status ON document_management(status);
CREATE INDEX IF NOT EXISTS idx_document_management_expiry ON document_management(expiry_date);

-- ============================================================
-- 9. UPDATE TRIGGERS
-- ============================================================

-- Add updated_at triggers for new tables
CREATE TRIGGER update_market_data_updated_at BEFORE UPDATE ON market_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_neighborhood_profiles_updated_at BEFORE UPDATE ON neighborhood_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_property_viewings_updated_at BEFORE UPDATE ON property_viewings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON appointments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_rera_compliance_updated_at BEFORE UPDATE ON rera_compliance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- 10. DATA VALIDATION CONSTRAINTS
-- ============================================================

-- Add check constraints for data validation
ALTER TABLE properties ADD CONSTRAINT chk_properties_price_aed_positive CHECK (price_aed >= 0);
ALTER TABLE properties ADD CONSTRAINT chk_properties_listing_status CHECK (listing_status IN ('draft', 'live', 'sold', 'withdrawn', 'pending'));
ALTER TABLE properties ADD CONSTRAINT chk_properties_bedrooms_positive CHECK (bedrooms >= 0);
ALTER TABLE properties ADD CONSTRAINT chk_properties_bathrooms_positive CHECK (bathrooms >= 0);

ALTER TABLE leads ADD CONSTRAINT chk_leads_nurture_status CHECK (nurture_status IN ('new', 'hot', 'warm', 'cold', 'qualified', 'unqualified'));
ALTER TABLE leads ADD CONSTRAINT chk_leads_lead_score CHECK (lead_score >= 0 AND lead_score <= 100);
ALTER TABLE leads ADD CONSTRAINT chk_leads_urgency_level CHECK (urgency_level IN ('low', 'normal', 'high', 'urgent'));

ALTER TABLE clients ADD CONSTRAINT chk_clients_client_type CHECK (client_type IN ('buyer', 'seller', 'investor', 'tenant', 'landlord'));
ALTER TABLE clients ADD CONSTRAINT chk_clients_client_status CHECK (client_status IN ('active', 'inactive', 'prospect', 'closed'));

ALTER TABLE transactions ADD CONSTRAINT chk_transactions_type CHECK (transaction_type IN ('sale', 'rental', 'lease', 'investment'));
ALTER TABLE transactions ADD CONSTRAINT chk_transactions_status CHECK (transaction_status IN ('pending', 'in_progress', 'completed', 'cancelled', 'on_hold'));

-- ============================================================
-- 11. SAMPLE DATA INSERTION
-- ============================================================

-- Insert sample neighborhood profiles for Dubai areas
INSERT INTO neighborhood_profiles (area_name, amenities, demographics, transportation_score, safety_rating, investment_potential, average_rental_yield, population_density, family_friendly_score, nightlife_score, shopping_score) VALUES
('Dubai Marina', '{"beach": true, "marina": true, "restaurants": true, "shopping": true, "gym": true}', '{"expat_ratio": 0.85, "average_age": 32.5}', 9, 8, 'high', 6.5, 12000, 7, 9, 9),
('Palm Jumeirah', '{"beach": true, "luxury_resorts": true, "restaurants": true, "spa": true}', '{"expat_ratio": 0.90, "average_age": 35.2}', 7, 9, 'high', 5.8, 8000, 8, 8, 7),
('Downtown Dubai', '{"burj_khalifa": true, "dubai_mall": true, "restaurants": true, "entertainment": true}', '{"expat_ratio": 0.80, "average_age": 33.8}', 10, 9, 'high', 6.2, 15000, 6, 9, 10),
('Jumeirah', '{"beach": true, "parks": true, "schools": true, "hospitals": true}', '{"expat_ratio": 0.70, "average_age": 38.5}', 8, 9, 'medium', 5.5, 6000, 9, 6, 7),
('Business Bay', '{"business_district": true, "restaurants": true, "gym": true, "shopping": true}', '{"expat_ratio": 0.75, "average_age": 31.2}', 9, 8, 'high', 6.8, 18000, 5, 7, 8)
ON CONFLICT (area_name) DO NOTHING;

-- Insert sample market data
INSERT INTO market_data (area, property_type, avg_price, price_per_sqft, market_trend, data_date, source) VALUES
('Dubai Marina', 'apartment', 1200000, 1200, 'rising', CURRENT_DATE, 'DLD'),
('Palm Jumeirah', 'villa', 3500000, 1800, 'stable', CURRENT_DATE, 'DLD'),
('Downtown Dubai', 'apartment', 1500000, 1400, 'rising', CURRENT_DATE, 'DLD'),
('Jumeirah', 'villa', 2800000, 1600, 'stable', CURRENT_DATE, 'DLD'),
('Business Bay', 'apartment', 1100000, 1100, 'rising', CURRENT_DATE, 'DLD')
ON CONFLICT (area, property_type, data_date) DO NOTHING;

-- ============================================================
-- 12. VERIFICATION QUERIES
-- ============================================================

-- Verify schema enhancements
SELECT 
    'Properties Table Enhanced' as table_name,
    COUNT(*) as total_columns
FROM information_schema.columns 
WHERE table_name = 'properties' AND table_schema = 'public';

SELECT 
    'Leads Table Enhanced' as table_name,
    COUNT(*) as total_columns
FROM information_schema.columns 
WHERE table_name = 'leads' AND table_schema = 'public';

SELECT 
    'New Tables Created' as status,
    COUNT(*) as table_count
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('market_data', 'neighborhood_profiles', 'transactions', 'property_viewings', 'appointments', 'rera_compliance', 'document_management');

-- ============================================================
-- MIGRATION COMPLETION
-- ============================================================

-- Update statistics
ANALYZE;

-- Display completion message
SELECT 
    'Schema Enhancement Migration Complete' as status,
    CURRENT_TIMESTAMP as completed_at,
    'Database schema enhanced for real estate workflow optimization' as description;
