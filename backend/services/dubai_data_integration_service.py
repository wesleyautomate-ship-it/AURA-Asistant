"""
Dubai Data Integration Service
=============================

This service handles integration with Dubai real estate data sources:
- RERA data integration
- Market data aggregation
- Property information enrichment
- Compliance checking
"""

import logging
import requests
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from fastapi import HTTPException, status
import json

from app.domain.listings.phase3_advanced_models import (
    DubaiMarketData, RERAIntegrationData, SystemPerformanceMetric
)
from app.domain.listings.ai_assistant_models import DubaiPropertyData, RERAComplianceData
from app.domain.listings.brokerage_models import Brokerage
from auth.models import User

logger = logging.getLogger(__name__)

class DubaiDataIntegrationService:
    """Service for integrating with Dubai real estate data sources"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # API endpoints for Dubai data sources
        self.data_sources = {
            'rera': {
                'base_url': 'https://api.rera.ae',  # Example URL
                'api_key': None,  # Would be configured via environment variables
                'rate_limit': 100  # requests per hour
            },
            'dubai_land_department': {
                'base_url': 'https://api.dld.gov.ae',  # Example URL
                'api_key': None,
                'rate_limit': 50
            },
            'property_finder': {
                'base_url': 'https://api.propertyfinder.ae',
                'api_key': None,
                'rate_limit': 200
            }
        }
    
    # =====================================================
    # MARKET DATA INTEGRATION
    # =====================================================
    
    async def fetch_market_data(
        self,
        area_name: str,
        property_type: str,
        data_types: List[str] = None,
        period_start: date = None,
        period_end: date = None
    ) -> Dict[str, Any]:
        """Fetch market data for a specific area and property type"""
        try:
            if not period_start:
                period_start = date.today() - timedelta(days=30)
            if not period_end:
                period_end = date.today()
            
            if not data_types:
                data_types = ['price_per_sqft', 'rental_yield', 'transaction_volume']
            
            market_data = {}
            
            for data_type in data_types:
                # Check if we have recent data in database
                existing_data = self.db.query(DubaiMarketData).filter(
                    and_(
                        DubaiMarketData.area_name == area_name,
                        DubaiMarketData.property_type == property_type,
                        DubaiMarketData.data_type == data_type,
                        DubaiMarketData.period_start >= period_start,
                        DubaiMarketData.period_end <= period_end
                    )
                ).first()
                
                if existing_data and existing_data.last_updated > datetime.utcnow() - timedelta(hours=24):
                    # Use cached data if it's less than 24 hours old
                    market_data[data_type] = {
                        'value': float(existing_data.data_value),
                        'unit': existing_data.data_unit,
                        'source': existing_data.data_source,
                        'quality_score': float(existing_data.data_quality_score),
                        'is_verified': existing_data.is_verified,
                        'last_updated': existing_data.last_updated
                    }
                else:
                    # Fetch fresh data from external sources
                    fresh_data = await self._fetch_external_market_data(
                        area_name, property_type, data_type, period_start, period_end
                    )
                    
                    if fresh_data:
                        # Store in database
                        await self._store_market_data(
                            area_name, property_type, data_type, fresh_data, period_start, period_end
                        )
                        market_data[data_type] = fresh_data
                    elif existing_data:
                        # Use existing data if fresh data unavailable
                        market_data[data_type] = {
                            'value': float(existing_data.data_value),
                            'unit': existing_data.data_unit,
                            'source': existing_data.data_source,
                            'quality_score': float(existing_data.data_quality_score),
                            'is_verified': existing_data.is_verified,
                            'last_updated': existing_data.last_updated,
                            'note': 'Using cached data - fresh data unavailable'
                        }
            
            return {
                'area_name': area_name,
                'property_type': property_type,
                'period_start': period_start,
                'period_end': period_end,
                'market_data': market_data,
                'data_sources_used': list(set([data['source'] for data in market_data.values() if 'source' in data]))
            }
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch market data: {str(e)}"
            )
    
    async def _fetch_external_market_data(
        self,
        area_name: str,
        property_type: str,
        data_type: str,
        period_start: date,
        period_end: date
    ) -> Optional[Dict[str, Any]]:
        """Fetch market data from external sources"""
        try:
            # In a real implementation, this would make actual API calls
            # For now, we'll simulate the data based on known Dubai market patterns
            
            simulated_data = {
                'price_per_sqft': {
                    'Dubai Marina': {'apartment': 1200, 'villa': 0},
                    'Palm Jumeirah': {'apartment': 1500, 'villa': 2500},
                    'Downtown Dubai': {'apartment': 1800, 'villa': 0},
                    'Business Bay': {'apartment': 1100, 'villa': 0}
                },
                'rental_yield': {
                    'Dubai Marina': {'apartment': 6.5, 'villa': 0},
                    'Palm Jumeirah': {'apartment': 5.2, 'villa': 5.2},
                    'Downtown Dubai': {'apartment': 7.1, 'villa': 0},
                    'Business Bay': {'apartment': 6.8, 'villa': 0}
                },
                'transaction_volume': {
                    'Dubai Marina': {'apartment': 45, 'villa': 0},
                    'Palm Jumeirah': {'apartment': 12, 'villa': 8},
                    'Downtown Dubai': {'apartment': 28, 'villa': 0},
                    'Business Bay': {'apartment': 35, 'villa': 0}
                }
            }
            
            if (area_name in simulated_data.get(data_type, {}) and 
                property_type in simulated_data[data_type][area_name]):
                
                value = simulated_data[data_type][area_name][property_type]
                
                return {
                    'value': value,
                    'unit': 'AED' if data_type == 'price_per_sqft' else 'percentage' if data_type == 'rental_yield' else 'count',
                    'source': 'RERA',
                    'quality_score': 0.95,
                    'is_verified': True,
                    'last_updated': datetime.utcnow()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching external market data: {e}")
            return None
    
    async def _store_market_data(
        self,
        area_name: str,
        property_type: str,
        data_type: str,
        data: Dict[str, Any],
        period_start: date,
        period_end: date
    ) -> None:
        """Store market data in database"""
        try:
            market_data = DubaiMarketData(
                area_name=area_name,
                property_type=property_type,
                data_type=data_type,
                data_value=data['value'],
                data_unit=data['unit'],
                period_start=period_start,
                period_end=period_end,
                data_source=data['source'],
                data_quality_score=data['quality_score'],
                is_verified=data['is_verified']
            )
            
            self.db.add(market_data)
            self.db.commit()
            
            logger.info(f"Stored market data for {area_name} {property_type} {data_type}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing market data: {e}")
    
    # =====================================================
    # RERA INTEGRATION
    # =====================================================
    
    async def fetch_rera_property_data(self, rera_number: str) -> Dict[str, Any]:
        """Fetch RERA property data by RERA number"""
        try:
            # Check if we have recent data in database
            existing_data = self.db.query(RERAIntegrationData).filter(
                RERAIntegrationData.rera_number == rera_number
            ).first()
            
            if existing_data and existing_data.last_rera_check and \
               existing_data.last_rera_check > datetime.utcnow() - timedelta(days=7):
                # Use cached data if it's less than 7 days old
                return {
                    'rera_number': existing_data.rera_number,
                    'developer_name': existing_data.developer_name,
                    'project_name': existing_data.project_name,
                    'completion_status': existing_data.completion_status,
                    'handover_date': existing_data.handover_date,
                    'rera_approval_date': existing_data.rera_approval_date,
                    'escrow_account_number': existing_data.escrow_account_number,
                    'escrow_bank': existing_data.escrow_bank,
                    'payment_plan': existing_data.payment_plan_dict,
                    'amenities': existing_data.amenities_list,
                    'nearby_facilities': existing_data.nearby_facilities_list,
                    'transportation_links': existing_data.transportation_links_list,
                    'compliance_status': existing_data.compliance_status,
                    'last_rera_check': existing_data.last_rera_check,
                    'rera_notes': existing_data.rera_notes,
                    'cached': True
                }
            
            # Fetch fresh data from RERA
            fresh_data = await self._fetch_external_rera_data(rera_number)
            
            if fresh_data:
                # Update or create database record
                if existing_data:
                    for key, value in fresh_data.items():
                        if hasattr(existing_data, key):
                            setattr(existing_data, key, value)
                    existing_data.last_rera_check = datetime.utcnow()
                    self.db.commit()
                    fresh_data['cached'] = False
                else:
                    rera_data = RERAIntegrationData(
                        rera_number=rera_number,
                        **fresh_data,
                        last_rera_check=datetime.utcnow()
                    )
                    self.db.add(rera_data)
                    self.db.commit()
                    fresh_data['cached'] = False
                
                return fresh_data
            elif existing_data:
                # Return existing data if fresh data unavailable
                return {
                    'rera_number': existing_data.rera_number,
                    'developer_name': existing_data.developer_name,
                    'project_name': existing_data.project_name,
                    'completion_status': existing_data.completion_status,
                    'handover_date': existing_data.handover_date,
                    'rera_approval_date': existing_data.rera_approval_date,
                    'escrow_account_number': existing_data.escrow_account_number,
                    'escrow_bank': existing_data.escrow_bank,
                    'payment_plan': existing_data.payment_plan_dict,
                    'amenities': existing_data.amenities_list,
                    'nearby_facilities': existing_data.nearby_facilities_list,
                    'transportation_links': existing_data.transportation_links_list,
                    'compliance_status': existing_data.compliance_status,
                    'last_rera_check': existing_data.last_rera_check,
                    'rera_notes': existing_data.rera_notes,
                    'cached': True,
                    'note': 'Using cached data - fresh data unavailable'
                }
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RERA data not found for number: {rera_number}"
            )
            
        except Exception as e:
            logger.error(f"Error fetching RERA property data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch RERA data: {str(e)}"
            )
    
    async def _fetch_external_rera_data(self, rera_number: str) -> Optional[Dict[str, Any]]:
        """Fetch RERA data from external source"""
        try:
            # In a real implementation, this would make actual API calls to RERA
            # For now, we'll simulate the data
            
            simulated_rera_data = {
                '12345': {
                    'developer_name': 'Emaar Properties',
                    'project_name': 'Marina Heights',
                    'completion_status': 'completed',
                    'handover_date': date(2023, 6, 15),
                    'rera_approval_date': date(2020, 3, 10),
                    'escrow_account_number': '1234567890',
                    'escrow_bank': 'Emirates NBD',
                    'payment_plan': {
                        'down_payment': '20%',
                        'construction_linked': '60%',
                        'handover': '20%'
                    },
                    'amenities': [
                        'Swimming Pool',
                        'Gym',
                        'Parking',
                        'Concierge',
                        'Security'
                    ],
                    'nearby_facilities': [
                        'Dubai Marina Mall',
                        'JBR Beach',
                        'Marina Walk',
                        'Metro Station'
                    ],
                    'transportation_links': [
                        'Dubai Marina Metro Station',
                        'JBR Tram',
                        'Sheikh Zayed Road'
                    ],
                    'compliance_status': 'compliant',
                    'rera_notes': 'All RERA requirements met'
                }
            }
            
            return simulated_rera_data.get(rera_number)
            
        except Exception as e:
            logger.error(f"Error fetching external RERA data: {e}")
            return None
    
    # =====================================================
    # COMPLIANCE CHECKING
    # =====================================================
    
    async def check_rera_compliance(
        self,
        property_id: int,
        brokerage_id: int,
        compliance_type: str = 'listing'
    ) -> Dict[str, Any]:
        """Check RERA compliance for a property"""
        try:
            # Get property data
            property_data = self.db.query(RERAIntegrationData).filter(
                RERAIntegrationData.property_id == property_id
            ).first()
            
            if not property_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Property not found or no RERA data available"
                )
            
            # Perform compliance checks
            compliance_result = await self._perform_compliance_checks(
                property_data, compliance_type
            )
            
            # Update compliance data
            compliance_data = self.db.query(RERAComplianceData).filter(
                and_(
                    RERAComplianceData.property_id == property_id,
                    RERAComplianceData.brokerage_id == brokerage_id,
                    RERAComplianceData.compliance_type == compliance_type
                )
            ).first()
            
            if not compliance_data:
                compliance_data = RERAComplianceData(
                    property_id=property_id,
                    brokerage_id=brokerage_id,
                    compliance_type=compliance_type,
                    compliance_status=compliance_result['status'],
                    required_documents=compliance_result['required_documents'],
                    submitted_documents=compliance_result['submitted_documents'],
                    compliance_score=compliance_result['score'],
                    last_check=datetime.utcnow(),
                    compliance_notes=compliance_result['notes']
                )
                self.db.add(compliance_data)
            else:
                compliance_data.compliance_status = compliance_result['status']
                compliance_data.required_documents = compliance_result['required_documents']
                compliance_data.submitted_documents = compliance_result['submitted_documents']
                compliance_data.compliance_score = compliance_result['score']
                compliance_data.last_check = datetime.utcnow()
                compliance_data.compliance_notes = compliance_result['notes']
            
            self.db.commit()
            
            return {
                'property_id': property_id,
                'compliance_type': compliance_type,
                'compliance_status': compliance_result['status'],
                'compliance_score': compliance_result['score'],
                'required_documents': compliance_result['required_documents'],
                'submitted_documents': compliance_result['submitted_documents'],
                'notes': compliance_result['notes'],
                'last_check': datetime.utcnow()
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error checking RERA compliance: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to check compliance: {str(e)}"
            )
    
    async def _perform_compliance_checks(
        self,
        property_data: RERAIntegrationData,
        compliance_type: str
    ) -> Dict[str, Any]:
        """Perform actual compliance checks"""
        try:
            required_documents = []
            submitted_documents = []
            compliance_score = 1.0
            notes = []
            
            if compliance_type == 'listing':
                required_documents = [
                    'RERA Registration Certificate',
                    'Property Title Deed',
                    'NOC from Developer',
                    'Property Photos',
                    'Floor Plan'
                ]
                
                # Check if property has RERA number
                if property_data.rera_number:
                    submitted_documents.append('RERA Registration Certificate')
                else:
                    compliance_score -= 0.3
                    notes.append('Missing RERA registration number')
                
                # Check completion status
                if property_data.completion_status == 'completed':
                    submitted_documents.append('Property Title Deed')
                else:
                    compliance_score -= 0.2
                    notes.append('Property not completed - title deed may not be available')
                
                # Check developer information
                if property_data.developer_name:
                    submitted_documents.append('NOC from Developer')
                else:
                    compliance_score -= 0.1
                    notes.append('Developer information not available')
            
            # Determine compliance status
            if compliance_score >= 0.9:
                status = 'compliant'
            elif compliance_score >= 0.7:
                status = 'pending'
            else:
                status = 'non_compliant'
            
            return {
                'status': status,
                'score': compliance_score,
                'required_documents': required_documents,
                'submitted_documents': submitted_documents,
                'notes': notes
            }
            
        except Exception as e:
            logger.error(f"Error performing compliance checks: {e}")
            return {
                'status': 'error',
                'score': 0.0,
                'required_documents': [],
                'submitted_documents': [],
                'notes': [f'Error during compliance check: {str(e)}']
            }
    
    # =====================================================
    # ANALYTICS AND REPORTING
    # =====================================================
    
    async def get_market_analytics(
        self,
        area_name: Optional[str] = None,
        property_type: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive market analytics"""
        try:
            start_date = date.today() - timedelta(days=period_days)
            
            query = self.db.query(DubaiMarketData).filter(
                DubaiMarketData.period_start >= start_date
            )
            
            if area_name:
                query = query.filter(DubaiMarketData.area_name == area_name)
            
            if property_type:
                query = query.filter(DubaiMarketData.property_type == property_type)
            
            market_data = query.all()
            
            # Analyze data
            analytics = {
                'total_data_points': len(market_data),
                'areas_covered': list(set([data.area_name for data in market_data])),
                'property_types': list(set([data.property_type for data in market_data])),
                'data_types': list(set([data.data_type for data in market_data])),
                'data_sources': list(set([data.data_source for data in market_data])),
                'average_quality_score': sum([float(data.data_quality_score) for data in market_data]) / len(market_data) if market_data else 0,
                'verified_data_percentage': (len([data for data in market_data if data.is_verified]) / len(market_data) * 100) if market_data else 0
            }
            
            # Price analysis
            price_data = [data for data in market_data if data.data_type == 'price_per_sqft']
            if price_data:
                analytics['price_analysis'] = {
                    'average_price': sum([float(data.data_value) for data in price_data]) / len(price_data),
                    'min_price': min([float(data.data_value) for data in price_data]),
                    'max_price': max([float(data.data_value) for data in price_data]),
                    'price_by_area': {
                        area: sum([float(data.data_value) for data in price_data if data.area_name == area]) / 
                              len([data for data in price_data if data.area_name == area])
                        for area in set([data.area_name for data in price_data])
                    }
                }
            
            # Rental yield analysis
            yield_data = [data for data in market_data if data.data_type == 'rental_yield']
            if yield_data:
                analytics['yield_analysis'] = {
                    'average_yield': sum([float(data.data_value) for data in yield_data]) / len(yield_data),
                    'min_yield': min([float(data.data_value) for data in yield_data]),
                    'max_yield': max([float(data.data_value) for data in yield_data])
                }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting market analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get market analytics: {str(e)}"
            )
    
    async def get_compliance_analytics(self, brokerage_id: int) -> Dict[str, Any]:
        """Get compliance analytics for a brokerage"""
        try:
            compliance_data = self.db.query(RERAComplianceData).filter(
                RERAComplianceData.brokerage_id == brokerage_id
            ).all()
            
            if not compliance_data:
                return {
                    'total_properties': 0,
                    'compliance_rate': 0,
                    'compliance_breakdown': {},
                    'average_score': 0
                }
            
            total_properties = len(compliance_data)
            compliant_properties = len([data for data in compliance_data if data.compliance_status == 'compliant'])
            compliance_rate = (compliant_properties / total_properties * 100) if total_properties > 0 else 0
            
            compliance_breakdown = {}
            for data in compliance_data:
                status = data.compliance_status
                compliance_breakdown[status] = compliance_breakdown.get(status, 0) + 1
            
            average_score = sum([float(data.compliance_score) for data in compliance_data if data.compliance_score]) / len(compliance_data)
            
            return {
                'total_properties': total_properties,
                'compliance_rate': compliance_rate,
                'compliance_breakdown': compliance_breakdown,
                'average_score': average_score,
                'last_updated': max([data.last_check for data in compliance_data if data.last_check])
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get compliance analytics: {str(e)}"
            )
