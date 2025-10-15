"""
Phase 4B ML Insights Database Models

This module defines the database schema for AI-powered insights, automated reporting,
smart notifications, and performance analytics.
"""

import os
from sqlalchemy import (
    create_engine,
    text,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Numeric,
    Text,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
    Index,
    Float,
    Date,
    Time,
    ARRAY,
    LargeBinary,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from env_loader import load_env

load_env()

# Database connection
database_url = os.getenv(
    "DATABASE_URL", "postgresql://admin:password123@localhost:5432/real_estate_db"
)
engine = create_engine(database_url)
Base = declarative_base()


def create_ml_insights_tables():
    """Create all Phase 4B ML insights database tables"""
    try:
        with engine.connect() as conn:
            print("🔍 Creating Phase 4B ML Insights database tables...")

            # 1. Automated Reports Table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS ml_automated_reports (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(255) UNIQUE NOT NULL,
                    report_type VARCHAR(100) NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    description TEXT,
                    content JSONB NOT NULL,
                    location VARCHAR(255),
                    property_type VARCHAR(100),
                    investment_type VARCHAR(100),
                    generated_by INTEGER REFERENCES users(id),
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active',
                    priority VARCHAR(20) DEFAULT 'medium',
                    tags TEXT[],
                    metadata JSONB,
                    version INTEGER DEFAULT 1,
                    is_template BOOLEAN DEFAULT FALSE,
                    template_id INTEGER REFERENCES ml_automated_reports(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )
            print("✅ ML Automated Reports table created")

            # 2. Smart Notifications Table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS ml_smart_notifications (
                    id SERIAL PRIMARY KEY,
                    notification_id VARCHAR(255) UNIQUE NOT NULL,
                    notification_type VARCHAR(100) NOT NULL,
                    title VARCHAR(500) NOT NULL,
                    message TEXT NOT NULL,
                    user_id INTEGER REFERENCES users(id),
                    priority VARCHAR(20) DEFAULT 'medium',
                    status VARCHAR(50) DEFAULT 'active',
                    read BOOLEAN DEFAULT FALSE,
                    dismissed BOOLEAN DEFAULT FALSE,
                    action_required BOOLEAN DEFAULT FALSE,
                    action_url VARCHAR(500),
                    action_text VARCHAR(100),
                    context_data JSONB,
                    source_service VARCHAR(100),
                    source_id VARCHAR(255),
                    expires_at TIMESTAMP,
                    scheduled_for TIMESTAMP,
                    sent_at TIMESTAMP,
                    read_at TIMESTAMP,
                    dismissed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )
            print("✅ ML Smart Notifications table created")

            # 3. Performance Analytics Table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS ml_performance_analytics (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    period VARCHAR(50) NOT NULL,
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    metrics JSONB NOT NULL,
                    performance_scores JSONB,
                    goal_progress JSONB,
                    insights JSONB,
                    recommendations JSONB,
                    comparison_data JSONB,
                    market_indicators JSONB,
                    client_analytics JSONB,
                    business_intelligence JSONB,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_current BOOLEAN DEFAULT TRUE,
                    version INTEGER DEFAULT 1,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )
            print("✅ ML Performance Analytics table created")

            # 4. Market Intelligence Table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS ml_market_intelligence (
                    id SERIAL PRIMARY KEY,
                    location VARCHAR(255) NOT NULL,
                    property_type VARCHAR(100) NOT NULL,
                    period VARCHAR(50) NOT NULL,
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    market_score FLOAT,
                    trend_indicators JSONB,
                    price_analysis JSONB,
                    demand_metrics JSONB,
                    supply_metrics JSONB,
                    investment_opportunities JSONB,
                    risk_assessment JSONB,
                    forecast_data JSONB,
                    competitor_analysis JSONB,
                    regulatory_updates JSONB,
                    infrastructure_developments JSONB,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_current BOOLEAN DEFAULT TRUE,
                    confidence_score FLOAT,
                    data_sources TEXT[],
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )
            print("✅ ML Market Intelligence table created")

            # 5. AI Model Performance Table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS ml_model_performance (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(255) NOT NULL,
                    model_version VARCHAR(100) NOT NULL,
                    model_type VARCHAR(100) NOT NULL,
                    performance_metrics JSONB NOT NULL,
                    accuracy_score FLOAT,
                    precision_score FLOAT,
                    recall_score FLOAT,
                    f1_score FLOAT,
                    training_data_size INTEGER,
                    training_duration FLOAT,
                    last_trained TIMESTAMP,
                    deployment_status VARCHAR(50) DEFAULT 'development',
                    is_active BOOLEAN DEFAULT FALSE,
                    model_file_path VARCHAR(500),
                    model_checksum VARCHAR(255),
                    hyperparameters JSONB,
                    feature_importance JSONB,
                    drift_detection JSONB,
                    monitoring_alerts JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )
            print("✅ ML Model Performance table created")

            # 6. WebSocket Connections Table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS ml_websocket_connections (
                    id SERIAL PRIMARY KEY,
                    connection_id VARCHAR(255) UNIQUE NOT NULL,
                    user_id INTEGER REFERENCES users(id),
                    session_token VARCHAR(255),
                    connection_status VARCHAR(50) DEFAULT 'connected',
                    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address INET,
                    user_agent TEXT,
                    connection_metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    disconnected_at TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )
            print("✅ ML WebSocket Connections table created")

            # 7. Notification Templates Table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS ml_notification_templates (
                    id SERIAL PRIMARY KEY,
                    template_name VARCHAR(255) UNIQUE NOT NULL,
                    template_type VARCHAR(100) NOT NULL,
                    title_template TEXT NOT NULL,
                    message_template TEXT NOT NULL,
                    variables JSONB,
                    conditions JSONB,
                    priority_rules JSONB,
                    delivery_channels TEXT[],
                    is_active BOOLEAN DEFAULT TRUE,
                    version INTEGER DEFAULT 1,
                    created_by INTEGER REFERENCES users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )
            print("✅ ML Notification Templates table created")

            # 8. AI Insights Log Table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS ml_insights_log (
                    id SERIAL PRIMARY KEY,
                    insight_type VARCHAR(100) NOT NULL,
                    user_id INTEGER REFERENCES users(id),
                    session_id VARCHAR(255),
                    query_text TEXT,
                    insight_data JSONB,
                    confidence_score FLOAT,
                    processing_time FLOAT,
                    model_used VARCHAR(255),
                    feedback_rating INTEGER,
                    feedback_comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
                )
            )
            print("✅ ML Insights Log table created")

            # Create indexes for performance
            print("🔍 Creating performance indexes...")

            # Automated Reports indexes
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_reports_type ON ml_automated_reports(report_type)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_reports_location ON ml_automated_reports(location)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_reports_generated_by ON ml_automated_reports(generated_by)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_reports_generated_at ON ml_automated_reports(generated_at)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_reports_status ON ml_automated_reports(status)"
                )
            )

            # Smart Notifications indexes
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_notifications_user ON ml_smart_notifications(user_id)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_notifications_type ON ml_smart_notifications(notification_type)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_notifications_status ON ml_smart_notifications(status)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_notifications_priority ON ml_smart_notifications(priority)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_notifications_created_at ON ml_smart_notifications(created_at)"
                )
            )

            # Performance Analytics indexes
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_analytics_user ON ml_performance_analytics(user_id)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_analytics_period ON ml_performance_analytics(period)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_analytics_period_start ON ml_performance_analytics(period_start)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_analytics_is_current ON ml_performance_analytics(is_current)"
                )
            )

            # Market Intelligence indexes
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_market_location ON ml_market_intelligence(location)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_market_property_type ON ml_market_intelligence(property_type)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_market_period ON ml_market_intelligence(period)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_market_is_current ON ml_market_intelligence(is_current)"
                )
            )

            # WebSocket Connections indexes
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_ws_user ON ml_websocket_connections(user_id)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_ws_status ON ml_websocket_connections(connection_status)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_ws_last_heartbeat ON ml_websocket_connections(last_heartbeat)"
                )
            )

            # Insights Log indexes
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_insights_user ON ml_insights_log(user_id)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_insights_type ON ml_insights_log(insight_type)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_ml_insights_created_at ON ml_insights_log(created_at)"
                )
            )

            conn.commit()
            print("✅ All Phase 4B ML Insights tables and indexes created successfully")

            # Insert default notification templates
            insert_default_templates(conn)

    except Exception as e:
        print(f"❌ Phase 4B database creation failed: {e}")
        raise


def insert_default_templates(conn):
    """Insert default notification templates"""
    try:
        # Check if templates exist
        result = conn.execute(text("SELECT COUNT(*) FROM ml_notification_templates"))
        if result.fetchone()[0] == 0:
            print("📝 Inserting default notification templates...")

            default_templates = [
                {
                    "template_name": "market_alert_high",
                    "template_type": "market_alert",
                    "title_template": "🚨 High Priority Market Alert: {location}",
                    "message_template": "Critical market changes detected in {location}. {alert_details}",
                    "variables": ["location", "alert_details"],
                    "priority_rules": {"default": "high"},
                    "delivery_channels": ["websocket", "email", "push"],
                },
                {
                    "template_name": "opportunity_alert",
                    "template_type": "opportunity",
                    "title_template": "💡 New Opportunity: {opportunity_type}",
                    "message_template": "New {opportunity_type} opportunity detected: {description}",
                    "variables": ["opportunity_type", "description"],
                    "priority_rules": {"default": "medium"},
                    "delivery_channels": ["websocket", "email"],
                },
                {
                    "template_name": "performance_update",
                    "template_type": "performance",
                    "title_template": "📊 Performance Update: {period}",
                    "message_template": "Your {period} performance metrics are ready. Overall score: {score}%",
                    "variables": ["period", "score"],
                    "priority_rules": {"default": "low"},
                    "delivery_channels": ["websocket", "email"],
                },
                {
                    "template_name": "report_ready",
                    "template_type": "report",
                    "title_template": "📋 Report Ready: {report_type}",
                    "message_template": "Your {report_type} report for {location} is ready for review.",
                    "variables": ["report_type", "location"],
                    "priority_rules": {"default": "medium"},
                    "delivery_channels": ["websocket", "email"],
                },
            ]

            for template in default_templates:
                conn.execute(
                    text(
                        """
                    INSERT INTO ml_notification_templates (
                        template_name, template_type, title_template, message_template,
                        variables, priority_rules, delivery_channels
                    ) VALUES (
                        :template_name, :template_type, :title_template, :message_template,
                        :variables, :priority_rules, :delivery_channels
                    )
                """
                    ),
                    template,
                )

            print("✅ Default notification templates inserted")
        else:
            print("ℹ️ Notification templates already exist")

    except Exception as e:
        print(f"⚠️ Failed to insert default templates: {e}")


def create_ml_insights_views():
    """Create useful database views for ML insights"""
    try:
        with engine.connect() as conn:
            print("🔍 Creating ML Insights database views...")

            # View for active notifications by user
            conn.execute(
                text(
                    """
                CREATE OR REPLACE VIEW ml_user_notifications_view AS
                SELECT 
                    n.id,
                    n.notification_id,
                    n.notification_type,
                    n.title,
                    n.message,
                    n.user_id,
                    n.priority,
                    n.status,
                    n.read,
                    n.dismissed,
                    n.action_required,
                    n.created_at,
                    u.email as user_email,
                    u.username as user_username
                FROM ml_smart_notifications n
                JOIN users u ON n.user_id = u.id
                WHERE n.status = 'active' AND n.dismissed = FALSE
                ORDER BY n.priority DESC, n.created_at DESC
            """
                )
            )

            # View for current performance metrics
            conn.execute(
                text(
                    """
                CREATE OR REPLACE VIEW ml_current_performance_view AS
                SELECT 
                    pa.id,
                    pa.user_id,
                    pa.period,
                    pa.period_start,
                    pa.period_end,
                    pa.performance_scores,
                    pa.goal_progress,
                    pa.insights,
                    pa.recommendations,
                    u.email as user_email,
                    u.username as user_username
                FROM ml_performance_analytics pa
                JOIN users u ON pa.user_id = u.id
                WHERE pa.is_current = TRUE
                ORDER BY pa.period_start DESC
            """
                )
            )

            # View for market intelligence summary
            conn.execute(
                text(
                    """
                CREATE OR REPLACE VIEW ml_market_summary_view AS
                SELECT 
                    location,
                    property_type,
                    period,
                    market_score,
                    trend_indicators,
                    price_analysis,
                    investment_opportunities,
                    generated_at,
                    confidence_score
                FROM ml_market_intelligence
                WHERE is_current = TRUE
                ORDER BY location, property_type, period_start DESC
            """
                )
            )

            # View for active WebSocket connections
            conn.execute(
                text(
                    """
                CREATE OR REPLACE VIEW ml_active_connections_view AS
                SELECT 
                    wc.id,
                    wc.connection_id,
                    wc.user_id,
                    wc.connection_status,
                    wc.last_heartbeat,
                    u.email as user_email,
                    u.username as user_username
                FROM ml_websocket_connections wc
                JOIN users u ON wc.user_id = u.id
                WHERE wc.connection_status = 'connected'
                ORDER BY wc.last_heartbeat DESC
            """
                )
            )

            conn.commit()
            print("✅ ML Insights database views created successfully")

    except Exception as e:
        print(f"⚠️ Failed to create database views: {e}")


def cleanup_old_data():
    """Clean up old ML insights data"""
    try:
        with engine.connect() as conn:
            print("🧹 Cleaning up old ML insights data...")

            # Clean up old notifications (older than 90 days)
            conn.execute(
                text(
                    """
                DELETE FROM ml_smart_notifications 
                WHERE created_at < NOW() - INTERVAL '90 days'
                AND (status = 'dismissed' OR status = 'inactive')
            """
                )
            )

            # Clean up old performance analytics (older than 1 year)
            conn.execute(
                text(
                    """
                DELETE FROM ml_performance_analytics 
                WHERE created_at < NOW() - INTERVAL '1 year'
                AND is_current = FALSE
            """
                )
            )

            # Clean up old market intelligence (older than 6 months)
            conn.execute(
                text(
                    """
                DELETE FROM ml_market_intelligence 
                WHERE created_at < NOW() - INTERVAL '6 months'
                AND is_current = FALSE
            """
                )
            )

            # Clean up old WebSocket connections (older than 1 day)
            conn.execute(
                text(
                    """
                DELETE FROM ml_websocket_connections 
                WHERE last_heartbeat < NOW() - INTERVAL '1 day'
                AND connection_status != 'connected'
            """
                )
            )

            # Clean up old insights log (older than 6 months)
            conn.execute(
                text(
                    """
                DELETE FROM ml_insights_log 
                WHERE created_at < NOW() - INTERVAL '6 months'
            """
                )
            )

            conn.commit()
            print("✅ Old ML insights data cleaned up successfully")

    except Exception as e:
        print(f"⚠️ Failed to cleanup old data: {e}")


if __name__ == "__main__":
    print("🚀 Creating Phase 4B ML Insights database...")
    create_ml_insights_tables()
    create_ml_insights_views()
    cleanup_old_data()
    print("✅ Phase 4B ML Insights database setup completed!")
