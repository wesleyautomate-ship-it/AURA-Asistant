"""
Compliance Monitoring Service
=============================

This service provides comprehensive compliance monitoring capabilities including:
- Regulatory compliance checking
- Automated compliance alerts
- Compliance rule management
- RERA compliance monitoring
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from fastapi import HTTPException, status
import json

from app.domain.listings.brokerage_models import ComplianceRule, Brokerage
from auth.models import User

logger = logging.getLogger(__name__)

class ComplianceMonitoringService:
    """Service for compliance monitoring and regulatory checking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =====================================================
    # COMPLIANCE RULE MANAGEMENT
    # =====================================================
    
    async def create_compliance_rule(
        self, 
        brokerage_id: int, 
        rule_data: Dict[str, Any], 
        created_by: int
    ) -> ComplianceRule:
        """Create a new compliance rule"""
        try:
            # Validate required fields
            required_fields = ['rule_name', 'rule_type']
            for field in required_fields:
                if not rule_data.get(field):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Field '{field}' is required"
                    )
            
            # Verify brokerage exists
            brokerage = self.db.query(Brokerage).filter(
                Brokerage.id == brokerage_id,
                Brokerage.is_active == True
            ).first()
            
            if not brokerage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Brokerage not found"
                )
            
            # Validate rule type
            valid_types = ['rera', 'vat', 'contract', 'disclosure', 'licensing', 'data_protection']
            if rule_data['rule_type'] not in valid_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid rule type. Must be one of: {', '.join(valid_types)}"
                )
            
            # Create compliance rule
            compliance_rule = ComplianceRule(
                brokerage_id=brokerage_id,
                rule_name=rule_data['rule_name'],
                rule_type=rule_data['rule_type'],
                description=rule_data.get('description'),
                conditions=json.dumps(rule_data.get('conditions', {})),
                actions=json.dumps(rule_data.get('actions', {})),
                is_active=rule_data.get('is_active', True),
                created_by=created_by
            )
            
            self.db.add(compliance_rule)
            self.db.commit()
            self.db.refresh(compliance_rule)
            
            logger.info(f"Created compliance rule: {compliance_rule.rule_name} (ID: {compliance_rule.id})")
            return compliance_rule
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating compliance rule: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create compliance rule: {str(e)}"
            )
    
    async def get_compliance_rule(self, rule_id: int, brokerage_id: int) -> ComplianceRule:
        """Get compliance rule by ID"""
        try:
            rule = self.db.query(ComplianceRule).filter(
                ComplianceRule.id == rule_id,
                ComplianceRule.brokerage_id == brokerage_id,
                ComplianceRule.is_active == True
            ).first()
            
            if not rule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Compliance rule not found"
                )
            
            return rule
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting compliance rule {rule_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get compliance rule: {str(e)}"
            )
    
    async def update_compliance_rule(
        self, 
        rule_id: int, 
        brokerage_id: int, 
        update_data: Dict[str, Any]
    ) -> ComplianceRule:
        """Update compliance rule"""
        try:
            rule = await self.get_compliance_rule(rule_id, brokerage_id)
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(rule, field):
                    if field in ['conditions', 'actions'] and isinstance(value, dict):
                        setattr(rule, field, json.dumps(value))
                    else:
                        setattr(rule, field, value)
            
            rule.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(rule)
            
            logger.info(f"Updated compliance rule: {rule.rule_name} (ID: {rule.id})")
            return rule
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating compliance rule {rule_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update compliance rule: {str(e)}"
            )
    
    async def delete_compliance_rule(self, rule_id: int, brokerage_id: int) -> bool:
        """Soft delete compliance rule (set is_active to False)"""
        try:
            rule = await self.get_compliance_rule(rule_id, brokerage_id)
            
            rule.is_active = False
            rule.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted compliance rule: {rule.rule_name} (ID: {rule.id})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting compliance rule {rule_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete compliance rule: {str(e)}"
            )
    
    async def list_compliance_rules(
        self, 
        brokerage_id: int, 
        rule_type: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ComplianceRule]:
        """List compliance rules with filtering"""
        try:
            query = self.db.query(ComplianceRule).filter(
                ComplianceRule.brokerage_id == brokerage_id
            )
            
            if active_only:
                query = query.filter(ComplianceRule.is_active == True)
            
            if rule_type:
                query = query.filter(ComplianceRule.rule_type == rule_type)
            
            rules = query.order_by(ComplianceRule.updated_at.desc()).offset(skip).limit(limit).all()
            return rules
            
        except Exception as e:
            logger.error(f"Error listing compliance rules: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list compliance rules: {str(e)}"
            )
    
    # =====================================================
    # COMPLIANCE CHECKING
    # =====================================================
    
    async def check_compliance(
        self, 
        brokerage_id: int, 
        check_type: str, 
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform compliance check"""
        try:
            # Get relevant compliance rules
            rules = await self.list_compliance_rules(brokerage_id, rule_type=check_type)
            
            if not rules:
                return {
                    "brokerage_id": brokerage_id,
                    "check_type": check_type,
                    "compliant": True,
                    "message": "No compliance rules found for this type",
                    "checked_at": datetime.utcnow().isoformat()
                }
            
            violations = []
            warnings = []
            
            # Check each rule
            for rule in rules:
                rule_result = await self._check_rule_compliance(rule, data)
                
                if rule_result['violation']:
                    violations.append({
                        "rule_id": rule.id,
                        "rule_name": rule.rule_name,
                        "violation": rule_result['violation'],
                        "severity": rule_result.get('severity', 'medium')
                    })
                elif rule_result['warning']:
                    warnings.append({
                        "rule_id": rule.id,
                        "rule_name": rule.rule_name,
                        "warning": rule_result['warning'],
                        "severity": rule_result.get('severity', 'low')
                    })
            
            # Determine overall compliance
            is_compliant = len(violations) == 0
            
            result = {
                "brokerage_id": brokerage_id,
                "check_type": check_type,
                "compliant": is_compliant,
                "violations": violations,
                "warnings": warnings,
                "rules_checked": len(rules),
                "checked_at": datetime.utcnow().isoformat()
            }
            
            # Execute compliance actions if violations found
            if violations:
                await self._execute_compliance_actions(brokerage_id, violations, data)
            
            logger.info(f"Compliance check completed for brokerage {brokerage_id}: {len(violations)} violations, {len(warnings)} warnings")
            return result
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to check compliance: {str(e)}"
            )
    
    async def _check_rule_compliance(self, rule: ComplianceRule, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance for a specific rule"""
        try:
            conditions = rule.conditions_dict
            
            if not conditions:
                return {"violation": None, "warning": None}
            
            # Check required fields
            required_fields = conditions.get('required_fields', [])
            for field in required_fields:
                if field not in data or not data[field]:
                    return {
                        "violation": f"Required field '{field}' is missing",
                        "severity": "high"
                    }
            
            # Check value constraints
            value_constraints = conditions.get('value_constraints', [])
            for constraint in value_constraints:
                field = constraint.get('field')
                min_value = constraint.get('min_value')
                max_value = constraint.get('max_value')
                allowed_values = constraint.get('allowed_values')
                
                if field in data:
                    value = data[field]
                    
                    # Check min/max values
                    if min_value is not None and value < min_value:
                        return {
                            "violation": f"Field '{field}' value {value} is below minimum {min_value}",
                            "severity": "medium"
                        }
                    
                    if max_value is not None and value > max_value:
                        return {
                            "violation": f"Field '{field}' value {value} is above maximum {max_value}",
                            "severity": "medium"
                        }
                    
                    # Check allowed values
                    if allowed_values and value not in allowed_values:
                        return {
                            "violation": f"Field '{field}' value '{value}' is not in allowed values: {allowed_values}",
                            "severity": "medium"
                        }
            
            # Check format constraints
            format_constraints = conditions.get('format_constraints', [])
            for constraint in format_constraints:
                field = constraint.get('field')
                pattern = constraint.get('pattern')
                
                if field in data and pattern:
                    import re
                    if not re.match(pattern, str(data[field])):
                        return {
                            "warning": f"Field '{field}' format does not match expected pattern",
                            "severity": "low"
                        }
            
            return {"violation": None, "warning": None}
            
        except Exception as e:
            logger.error(f"Error checking rule compliance: {e}")
            return {"violation": f"Error checking rule: {str(e)}", "severity": "high"}
    
    async def _execute_compliance_actions(self, brokerage_id: int, violations: List[Dict[str, Any]], data: Dict[str, Any]):
        """Execute compliance actions for violations"""
        try:
            for violation in violations:
                rule_id = violation['rule_id']
                rule = await self.get_compliance_rule(rule_id, brokerage_id)
                actions = rule.actions_dict
                
                # Execute actions
                action_list = actions.get('actions', [])
                for action in action_list:
                    action_type = action.get('type')
                    
                    if action_type == 'send_alert':
                        await self._send_compliance_alert(brokerage_id, violation, action)
                    elif action_type == 'log_violation':
                        await self._log_compliance_violation(brokerage_id, violation, data)
                    elif action_type == 'block_action':
                        await self._block_action(brokerage_id, violation, action)
            
        except Exception as e:
            logger.error(f"Error executing compliance actions: {e}")
    
    async def _send_compliance_alert(self, brokerage_id: int, violation: Dict[str, Any], action: Dict[str, Any]):
        """Send compliance alert"""
        # Placeholder implementation
        logger.warning(f"Compliance alert for brokerage {brokerage_id}: {violation['violation']}")
    
    async def _log_compliance_violation(self, brokerage_id: int, violation: Dict[str, Any], data: Dict[str, Any]):
        """Log compliance violation"""
        # Placeholder implementation
        logger.warning(f"Compliance violation logged for brokerage {brokerage_id}: {violation['violation']}")
    
    async def _block_action(self, brokerage_id: int, violation: Dict[str, Any], action: Dict[str, Any]):
        """Block action due to compliance violation"""
        # Placeholder implementation
        logger.warning(f"Action blocked for brokerage {brokerage_id} due to: {violation['violation']}")
    
    # =====================================================
    # RERA COMPLIANCE
    # =====================================================
    
    async def check_rera_compliance(self, brokerage_id: int, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check RERA compliance for property transactions"""
        try:
            rera_rules = [
                {
                    "field": "rera_number",
                    "required": True,
                    "message": "RERA number is required for all property transactions"
                },
                {
                    "field": "developer_license",
                    "required": True,
                    "message": "Developer license number is required"
                },
                {
                    "field": "property_type",
                    "allowed_values": ["apartment", "villa", "townhouse", "commercial", "land"],
                    "message": "Property type must be one of the allowed values"
                },
                {
                    "field": "price_aed",
                    "min_value": 100000,
                    "message": "Property price must be at least AED 100,000"
                }
            ]
            
            violations = []
            warnings = []
            
            for rule in rera_rules:
                field = rule['field']
                
                if rule.get('required') and (field not in property_data or not property_data[field]):
                    violations.append({
                        "rule": rule['field'],
                        "violation": rule['message'],
                        "severity": "high"
                    })
                elif field in property_data:
                    value = property_data[field]
                    
                    # Check allowed values
                    if 'allowed_values' in rule and value not in rule['allowed_values']:
                        violations.append({
                            "rule": rule['field'],
                            "violation": f"{rule['message']}. Got: {value}",
                            "severity": "medium"
                        })
                    
                    # Check min value
                    if 'min_value' in rule and value < rule['min_value']:
                        violations.append({
                            "rule": rule['field'],
                            "violation": f"{rule['message']}. Got: {value}",
                            "severity": "medium"
                        })
            
            return {
                "brokerage_id": brokerage_id,
                "rera_compliant": len(violations) == 0,
                "violations": violations,
                "warnings": warnings,
                "checked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking RERA compliance: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to check RERA compliance: {str(e)}"
            )
    
    # =====================================================
    # COMPLIANCE ANALYTICS
    # =====================================================
    
    async def get_compliance_analytics(self, brokerage_id: int) -> Dict[str, Any]:
        """Get compliance monitoring analytics"""
        try:
            # Get rule counts by type
            rules_by_type = self.db.query(
                ComplianceRule.rule_type,
                func.count(ComplianceRule.id).label('count')
            ).filter(
                ComplianceRule.brokerage_id == brokerage_id,
                ComplianceRule.is_active == True
            ).group_by(ComplianceRule.rule_type).all()
            
            # Get total rules
            total_rules = sum(count.count for count in rules_by_type)
            
            # Get recent rules (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_rules = self.db.query(ComplianceRule).filter(
                ComplianceRule.brokerage_id == brokerage_id,
                ComplianceRule.is_active == True,
                ComplianceRule.created_at >= thirty_days_ago
            ).count()
            
            analytics = {
                "brokerage_id": brokerage_id,
                "total_rules": total_rules,
                "recent_rules_30_days": recent_rules,
                "rules_by_type": [
                    {"rule_type": r.rule_type, "count": r.count}
                    for r in rules_by_type
                ],
                "compliance_coverage": self._calculate_compliance_coverage(rules_by_type),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting compliance analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get compliance analytics: {str(e)}"
            )
    
    def _calculate_compliance_coverage(self, rules_by_type: List[Any]) -> Dict[str, Any]:
        """Calculate compliance coverage percentage"""
        required_types = ['rera', 'vat', 'contract', 'disclosure']
        covered_types = [r.rule_type for r in rules_by_type]
        
        coverage_percentage = (len(set(covered_types) & set(required_types)) / len(required_types)) * 100
        
        return {
            "coverage_percentage": round(coverage_percentage, 2),
            "covered_types": covered_types,
            "missing_types": list(set(required_types) - set(covered_types))
        }
