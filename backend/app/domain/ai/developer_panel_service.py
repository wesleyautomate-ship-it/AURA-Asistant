"""
Developer Panel Service
======================

This service provides comprehensive system oversight and control for developers:
- System monitoring and health checks
- Performance analytics and metrics
- User activity tracking
- Multi-brokerage analytics
- System alerts and notifications
- Configuration management
"""

import logging
import psutil
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from fastapi import HTTPException, status
import json

from app.domain.listings.phase3_advanced_models import (
    SystemPerformanceMetric, UserActivityAnalytic, AIProcessingAnalytic,
    MultiBrokerageAnalytic, DeveloperPanelSetting, SystemAlert
)
from app.domain.listings.ai_assistant_models import AIRequest, HumanExpert, VoiceRequest
from app.domain.listings.brokerage_models import Brokerage
from auth.models import User

logger = logging.getLogger(__name__)

class DeveloperPanelService:
    """Service for developer panel functionality and system oversight"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================
    # SYSTEM MONITORING
    # =====================================================
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        try:
            # System resource monitoring
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Database health check
            db_health = await self._check_database_health()
            
            # API health check
            api_health = await self._check_api_health()
            
            # AI service health check
            ai_health = await self._check_ai_service_health()
            
            # Recent error count
            recent_errors = self.db.query(SystemAlert).filter(
                and_(
                    SystemAlert.alert_type == 'error',
                    SystemAlert.created_at >= datetime.utcnow() - timedelta(hours=24),
                    SystemAlert.is_resolved == False
                )
            ).count()
            
            # Overall health score
            health_score = self._calculate_health_score(
                cpu_percent, memory.percent, disk.percent, 
                db_health, api_health, ai_health, recent_errors
            )
            
            return {
                'overall_health': 'healthy' if health_score >= 80 else 'warning' if health_score >= 60 else 'critical',
                'health_score': health_score,
                'system_resources': {
                    'cpu_usage_percent': cpu_percent,
                    'memory_usage_percent': memory.percent,
                    'disk_usage_percent': disk.percent,
                    'available_memory_gb': round(memory.available / (1024**3), 2),
                    'available_disk_gb': round(disk.free / (1024**3), 2)
                },
                'service_health': {
                    'database': db_health,
                    'api': api_health,
                    'ai_service': ai_health
                },
                'recent_errors_24h': recent_errors,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get system health: {str(e)}"
            )
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health and performance"""
        try:
            # Test database connection
            start_time = datetime.utcnow()
            result = self.db.execute(text("SELECT 1"))
            end_time = datetime.utcnow()
            
            response_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
            
            # Check active connections
            active_connections = self.db.execute(text(
                "SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'"
            )).scalar()
            
            # Check database size
            db_size = self.db.execute(text(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            )).scalar()
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'active_connections': active_connections,
                'database_size': db_size
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Check API health and performance"""
        try:
            # Get recent API performance metrics
            recent_metrics = self.db.query(SystemPerformanceMetric).filter(
                and_(
                    SystemPerformanceMetric.metric_category == 'api_performance',
                    SystemPerformanceMetric.measurement_timestamp >= datetime.utcnow() - timedelta(minutes=5)
                )
            ).order_by(desc(SystemPerformanceMetric.measurement_timestamp)).first()
            
            if recent_metrics:
                avg_response_time = float(recent_metrics.metric_value)
                status = 'healthy' if avg_response_time < 500 else 'warning' if avg_response_time < 1000 else 'critical'
                
                return {
                    'status': status,
                    'average_response_time_ms': avg_response_time,
                    'last_updated': recent_metrics.measurement_timestamp
                }
            else:
                return {
                    'status': 'unknown',
                    'message': 'No recent API metrics available'
                }
                
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_ai_service_health(self) -> Dict[str, Any]:
        """Check AI service health and performance"""
        try:
            # Get recent AI processing metrics
            recent_metrics = self.db.query(SystemPerformanceMetric).filter(
                and_(
                    SystemPerformanceMetric.metric_category == 'ai_processing',
                    SystemPerformanceMetric.measurement_timestamp >= datetime.utcnow() - timedelta(minutes=10)
                )
            ).order_by(desc(SystemPerformanceMetric.measurement_timestamp)).first()
            
            if recent_metrics:
                avg_processing_time = float(recent_metrics.metric_value)
                status = 'healthy' if avg_processing_time < 10000 else 'warning' if avg_processing_time < 30000 else 'critical'
                
                return {
                    'status': status,
                    'average_processing_time_ms': avg_processing_time,
                    'last_updated': recent_metrics.measurement_timestamp
                }
            else:
                return {
                    'status': 'unknown',
                    'message': 'No recent AI processing metrics available'
                }
                
        except Exception as e:
            logger.error(f"AI service health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _calculate_health_score(
        self, 
        cpu_percent: float, 
        memory_percent: float, 
        disk_percent: float,
        db_health: Dict, 
        api_health: Dict, 
        ai_health: Dict, 
        recent_errors: int
    ) -> int:
        """Calculate overall system health score"""
        try:
            score = 100
            
            # Resource usage penalties
            if cpu_percent > 80:
                score -= 20
            elif cpu_percent > 60:
                score -= 10
            
            if memory_percent > 85:
                score -= 20
            elif memory_percent > 70:
                score -= 10
            
            if disk_percent > 90:
                score -= 20
            elif disk_percent > 80:
                score -= 10
            
            # Service health penalties
            if db_health.get('status') != 'healthy':
                score -= 30
            if api_health.get('status') not in ['healthy', 'unknown']:
                score -= 20
            if ai_health.get('status') not in ['healthy', 'unknown']:
                score -= 15
            
            # Error penalties
            if recent_errors > 10:
                score -= 20
            elif recent_errors > 5:
                score -= 10
            elif recent_errors > 0:
                score -= 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 0
    
    # =====================================================
    # PERFORMANCE ANALYTICS
    # =====================================================
    
    async def get_performance_analytics(
        self,
        period_hours: int = 24,
        metric_categories: List[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive performance analytics"""
        try:
            if not metric_categories:
                metric_categories = ['api_performance', 'database_performance', 'ai_processing', 'user_activity']
            
            start_time = datetime.utcnow() - timedelta(hours=period_hours)
            
            analytics = {}
            
            for category in metric_categories:
                metrics = self.db.query(SystemPerformanceMetric).filter(
                    and_(
                        SystemPerformanceMetric.metric_category == category,
                        SystemPerformanceMetric.measurement_timestamp >= start_time
                    )
                ).order_by(SystemPerformanceMetric.measurement_timestamp).all()
                
                if metrics:
                    analytics[category] = {
                        'total_measurements': len(metrics),
                        'average_value': sum([float(m.metric_value) for m in metrics]) / len(metrics),
                        'min_value': min([float(m.metric_value) for m in metrics]),
                        'max_value': max([float(m.metric_value) for m in metrics]),
                        'latest_value': float(metrics[-1].metric_value),
                        'latest_timestamp': metrics[-1].measurement_timestamp,
                        'trend': self._calculate_trend([float(m.metric_value) for m in metrics])
                    }
                else:
                    analytics[category] = {
                        'total_measurements': 0,
                        'message': 'No data available for this period'
                    }
            
            return {
                'period_hours': period_hours,
                'start_time': start_time,
                'end_time': datetime.utcnow(),
                'analytics': analytics
            }
            
        except Exception as e:
            logger.error(f"Error getting performance analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get performance analytics: {str(e)}"
            )
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        try:
            if len(values) < 2:
                return 'insufficient_data'
            
            # Simple linear trend calculation
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            change_percent = ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0
            
            if change_percent > 5:
                return 'increasing'
            elif change_percent < -5:
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return 'error'
    
    # =====================================================
    # USER ACTIVITY ANALYTICS
    # =====================================================
    
    async def get_user_activity_analytics(
        self,
        period_days: int = 7,
        brokerage_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get user activity analytics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=period_days)
            
            query = self.db.query(UserActivityAnalytic).filter(
                UserActivityAnalytic.created_at >= start_date
            )
            
            if brokerage_id:
                query = query.filter(UserActivityAnalytic.brokerage_id == brokerage_id)
            
            activities = query.all()
            
            if not activities:
                return {
                    'period_days': period_days,
                    'total_activities': 0,
                    'message': 'No activity data available for this period'
                }
            
            # Activity breakdown
            activity_breakdown = {}
            for activity in activities:
                activity_type = activity.activity_type
                activity_breakdown[activity_type] = activity_breakdown.get(activity_type, 0) + 1
            
            # User breakdown
            user_breakdown = {}
            for activity in activities:
                user_id = activity.user_id
                if user_id not in user_breakdown:
                    user_breakdown[user_id] = {
                        'total_activities': 0,
                        'activity_types': {},
                        'success_rate': 0,
                        'total_duration': 0
                    }
                
                user_breakdown[user_id]['total_activities'] += 1
                user_breakdown[user_id]['activity_types'][activity.activity_type] = \
                    user_breakdown[user_id]['activity_types'].get(activity.activity_type, 0) + 1
                
                if activity.duration_seconds:
                    user_breakdown[user_id]['total_duration'] += activity.duration_seconds
            
            # Calculate success rates
            for user_id in user_breakdown:
                user_activities = [a for a in activities if a.user_id == user_id]
                successful_activities = len([a for a in user_activities if a.success])
                user_breakdown[user_id]['success_rate'] = (successful_activities / len(user_activities)) * 100
            
            # Device and browser breakdown
            device_breakdown = {}
            browser_breakdown = {}
            for activity in activities:
                if activity.device_type:
                    device_breakdown[activity.device_type] = device_breakdown.get(activity.device_type, 0) + 1
                if activity.browser_type:
                    browser_breakdown[activity.browser_type] = browser_breakdown.get(activity.browser_type, 0) + 1
            
            return {
                'period_days': period_days,
                'total_activities': len(activities),
                'unique_users': len(user_breakdown),
                'activity_breakdown': activity_breakdown,
                'user_breakdown': user_breakdown,
                'device_breakdown': device_breakdown,
                'browser_breakdown': browser_breakdown,
                'average_activities_per_user': len(activities) / len(user_breakdown) if user_breakdown else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting user activity analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user activity analytics: {str(e)}"
            )
    
    # =====================================================
    # MULTI-BROKERAGE ANALYTICS
    # =====================================================
    
    async def get_multi_brokerage_analytics(
        self,
        period_days: int = 30,
        analytics_types: List[str] = None
    ) -> Dict[str, Any]:
        """Get system-wide analytics across all brokerages"""
        try:
            if not analytics_types:
                analytics_types = ['system_usage', 'feature_adoption', 'performance_comparison']
            
            start_date = date.today() - timedelta(days=period_days)
            
            # Get multi-brokerage analytics
            multi_analytics = self.db.query(MultiBrokerageAnalytic).filter(
                and_(
                    MultiBrokerageAnalytic.analytics_type.in_(analytics_types),
                    MultiBrokerageAnalytic.period_start >= start_date
                )
            ).all()
            
            # Get brokerage statistics
            total_brokerages = self.db.query(Brokerage).filter(Brokerage.is_active == True).count()
            total_users = self.db.query(User).filter(User.brokerage_id.isnot(None)).count()
            
            # Get AI request statistics
            ai_requests = self.db.query(AIRequest).filter(
                AIRequest.created_at >= datetime.utcnow() - timedelta(days=period_days)
            ).all()
            
            # Get voice request statistics
            voice_requests = self.db.query(VoiceRequest).filter(
                VoiceRequest.created_at >= datetime.utcnow() - timedelta(days=period_days)
            ).all()
            
            # Get human expert statistics
            active_experts = self.db.query(HumanExpert).filter(
                and_(
                    HumanExpert.is_active == True,
                    HumanExpert.availability_status == 'available'
                )
            ).count()
            
            # Organize analytics by type
            analytics_by_type = {}
            for analytics in multi_analytics:
                analytics_type = analytics.analytics_type
                if analytics_type not in analytics_by_type:
                    analytics_by_type[analytics_type] = []
                analytics_by_type[analytics_type].append({
                    'metric_name': analytics.metric_name,
                    'metric_value': float(analytics.metric_value),
                    'metric_unit': analytics.metric_unit,
                    'period_start': analytics.period_start,
                    'period_end': analytics.period_end,
                    'brokerage_count': analytics.brokerage_count,
                    'total_users': analytics.total_users,
                    'additional_metrics': analytics.additional_metrics_dict
                })
            
            return {
                'period_days': period_days,
                'system_overview': {
                    'total_brokerages': total_brokerages,
                    'total_users': total_users,
                    'active_experts': active_experts,
                    'total_ai_requests': len(ai_requests),
                    'total_voice_requests': len(voice_requests)
                },
                'analytics_by_type': analytics_by_type,
                'feature_adoption': {
                    'ai_requests_per_brokerage': len(ai_requests) / total_brokerages if total_brokerages > 0 else 0,
                    'voice_requests_per_brokerage': len(voice_requests) / total_brokerages if total_brokerages > 0 else 0,
                    'experts_per_brokerage': active_experts / total_brokerages if total_brokerages > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting multi-brokerage analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get multi-brokerage analytics: {str(e)}"
            )
    
    # =====================================================
    # SYSTEM ALERTS MANAGEMENT
    # =====================================================
    
    async def get_system_alerts(
        self,
        alert_type: Optional[str] = None,
        severity: Optional[str] = None,
        is_resolved: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get system alerts with filtering"""
        try:
            query = self.db.query(SystemAlert)
            
            if alert_type:
                query = query.filter(SystemAlert.alert_type == alert_type)
            
            if severity:
                query = query.filter(SystemAlert.severity == severity)
            
            if is_resolved is not None:
                query = query.filter(SystemAlert.is_resolved == is_resolved)
            
            total = query.count()
            alerts = query.order_by(desc(SystemAlert.created_at)).offset(offset).limit(limit).all()
            
            return {
                'alerts': [
                    {
                        'id': alert.id,
                        'alert_type': alert.alert_type,
                        'alert_category': alert.alert_category,
                        'alert_title': alert.alert_title,
                        'alert_message': alert.alert_message,
                        'severity': alert.severity,
                        'affected_components': alert.affected_components_list,
                        'alert_data': alert.alert_data_dict,
                        'is_resolved': alert.is_resolved,
                        'resolved_by': alert.resolved_by,
                        'resolved_at': alert.resolved_at,
                        'resolution_notes': alert.resolution_notes,
                        'created_at': alert.created_at
                    }
                    for alert in alerts
                ],
                'total': total,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Error getting system alerts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get system alerts: {str(e)}"
            )
    
    async def create_system_alert(
        self,
        alert_type: str,
        alert_category: str,
        alert_title: str,
        alert_message: str,
        severity: str = 'medium',
        affected_components: List[str] = None,
        alert_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new system alert"""
        try:
            alert = SystemAlert(
                alert_type=alert_type,
                alert_category=alert_category,
                alert_title=alert_title,
                alert_message=alert_message,
                severity=severity,
                affected_components=affected_components or [],
                alert_data=alert_data or {}
            )
            
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            
            logger.info(f"Created system alert: {alert_title}")
            
            return {
                'alert_id': alert.id,
                'message': 'System alert created successfully'
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating system alert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create system alert: {str(e)}"
            )
    
    async def resolve_system_alert(
        self,
        alert_id: int,
        resolved_by: int,
        resolution_notes: str = None
    ) -> Dict[str, Any]:
        """Resolve a system alert"""
        try:
            alert = self.db.query(SystemAlert).filter(SystemAlert.id == alert_id).first()
            
            if not alert:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="System alert not found"
                )
            
            if alert.is_resolved:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Alert is already resolved"
                )
            
            alert.is_resolved = True
            alert.resolved_by = resolved_by
            alert.resolved_at = datetime.utcnow()
            alert.resolution_notes = resolution_notes
            
            self.db.commit()
            
            logger.info(f"Resolved system alert {alert_id}")
            
            return {
                'alert_id': alert_id,
                'message': 'System alert resolved successfully'
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resolving system alert: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to resolve system alert: {str(e)}"
            )
    
    # =====================================================
    # DEVELOPER SETTINGS MANAGEMENT
    # =====================================================
    
    async def get_developer_settings(self, user_id: int) -> Dict[str, Any]:
        """Get developer panel settings for a user"""
        try:
            settings = self.db.query(DeveloperPanelSetting).filter(
                and_(
                    DeveloperPanelSetting.user_id == user_id,
                    DeveloperPanelSetting.is_active == True
                )
            ).all()
            
            settings_dict = {}
            for setting in settings:
                category = setting.setting_category
                if category not in settings_dict:
                    settings_dict[category] = {}
                settings_dict[category][setting.setting_name] = setting.setting_value_dict
            
            return {
                'user_id': user_id,
                'settings': settings_dict
            }
            
        except Exception as e:
            logger.error(f"Error getting developer settings: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get developer settings: {str(e)}"
            )
    
    async def update_developer_settings(
        self,
        user_id: int,
        settings: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update developer panel settings"""
        try:
            for category, category_settings in settings.items():
                for setting_name, setting_value in category_settings.items():
                    # Check if setting exists
                    existing_setting = self.db.query(DeveloperPanelSetting).filter(
                        and_(
                            DeveloperPanelSetting.user_id == user_id,
                            DeveloperPanelSetting.setting_category == category,
                            DeveloperPanelSetting.setting_name == setting_name
                        )
                    ).first()
                    
                    if existing_setting:
                        # Update existing setting
                        existing_setting.setting_value = setting_value
                        existing_setting.updated_at = datetime.utcnow()
                    else:
                        # Create new setting
                        new_setting = DeveloperPanelSetting(
                            user_id=user_id,
                            setting_category=category,
                            setting_name=setting_name,
                            setting_value=setting_value
                        )
                        self.db.add(new_setting)
            
            self.db.commit()
            
            logger.info(f"Updated developer settings for user {user_id}")
            
            return {
                'user_id': user_id,
                'message': 'Developer settings updated successfully'
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating developer settings: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update developer settings: {str(e)}"
            )
