"""
Role-Based Access Control (RBAC) for Dubai Real Estate RAG System
===============================================================

This module implements strict data segregation and access control to prevent
cross-contamination between different user roles and sessions.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles with specific access levels"""

    AGENT = "agent"
    ADMIN = "admin"


class DataAccessLevel(Enum):
    """Data access levels for different content types"""

    PUBLIC = "public"  # Available to all users
    AGENT = "agent"  # Agent-specific resources
    CONFIDENTIAL = "confidential"  # Admin only


@dataclass
class AccessControl:
    """Access control configuration for data types"""

    data_type: str
    allowed_roles: Set[UserRole]
    access_level: DataAccessLevel
    requires_authentication: bool = True
    session_isolation: bool = True


class RBACManager:
    """Role-Based Access Control Manager"""

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Define access control rules
        self.access_rules = {
            # Property data
            "property_listings": AccessControl(
                data_type="property_listings",
                allowed_roles={UserRole.AGENT, UserRole.ADMIN},
                access_level=DataAccessLevel.PUBLIC,
            ),
            "property_details": AccessControl(
                data_type="property_details",
                allowed_roles={UserRole.AGENT, UserRole.ADMIN},
                access_level=DataAccessLevel.PUBLIC,
            ),
            # Client data
            "client_profiles": AccessControl(
                data_type="client_profiles",
                allowed_roles={UserRole.AGENT, UserRole.ADMIN},
                access_level=DataAccessLevel.AGENT,
                session_isolation=True,
            ),
            "client_preferences": AccessControl(
                data_type="client_preferences",
                allowed_roles={UserRole.AGENT, UserRole.ADMIN},
                access_level=DataAccessLevel.AGENT,
                session_isolation=True,
            ),
            # Agent resources
            "commission_structures": AccessControl(
                data_type="commission_structures",
                allowed_roles={UserRole.AGENT, UserRole.ADMIN},
                access_level=DataAccessLevel.AGENT,
            ),
            "sales_resources": AccessControl(
                data_type="sales_resources",
                allowed_roles={UserRole.AGENT, UserRole.ADMIN},
                access_level=DataAccessLevel.AGENT,
            ),
            "market_analysis": AccessControl(
                data_type="market_analysis",
                allowed_roles={UserRole.AGENT, UserRole.ADMIN},
                access_level=DataAccessLevel.AGENT,
            ),
            # Administrative data
            "financial_reports": AccessControl(
                data_type="financial_reports",
                allowed_roles={UserRole.ADMIN},
                access_level=DataAccessLevel.CONFIDENTIAL,
            ),
            "company_policies": AccessControl(
                data_type="company_policies",
                allowed_roles={UserRole.ADMIN},
                access_level=DataAccessLevel.CONFIDENTIAL,
            ),
            # Confidential data
            "legal_documents": AccessControl(
                data_type="legal_documents",
                allowed_roles={UserRole.ADMIN},
                access_level=DataAccessLevel.CONFIDENTIAL,
            ),
            "hr_records": AccessControl(
                data_type="hr_records",
                allowed_roles={UserRole.ADMIN},
                access_level=DataAccessLevel.CONFIDENTIAL,
            ),
        }

    def validate_access(
        self,
        user_role: UserRole,
        data_type: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> bool:
        """Validate if user has access to specific data type"""
        try:
            if data_type not in self.access_rules:
                logger.warning(f"Unknown data type: {data_type}")
                return False

            rule = self.access_rules[data_type]

            # Check role-based access
            if user_role not in rule.allowed_roles:
                logger.warning(
                    f"User role {user_role} not allowed for data type {data_type}"
                )
                return False

            # Check session isolation for agent-specific client data
            if rule.session_isolation and rule.access_level == DataAccessLevel.AGENT:
                if not user_id or not session_id:
                    logger.warning(
                        f"Session isolation required but missing user_id or session_id"
                    )
                    return False

                # Verify user owns this session
                if not self._verify_session_ownership(user_id, session_id):
                    logger.warning(
                        f"Session ownership verification failed for user {user_id}, session {session_id}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating access: {e}")
            return False

    def _verify_session_ownership(self, user_id: str, session_id: str) -> bool:
        """Verify that the session belongs to the user"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                    SELECT user_id FROM user_sessions 
                    WHERE session_token = :session_id AND user_id = :user_id AND is_active = TRUE
                """
                    ),
                    {"session_id": session_id, "user_id": user_id},
                )

                return result.fetchone() is not None

        except Exception as e:
            logger.error(f"Error verifying session ownership: {e}")
            return False

    def filter_data_by_role(
        self, data: List[Dict], user_role: UserRole, data_type: str
    ) -> List[Dict]:
        """Filter data based on user role and data type"""
        try:
            if not self.validate_access(user_role, data_type):
                return []

            rule = self.access_rules[data_type]

            # Apply role-specific filtering
            if user_role == UserRole.AGENT:
                return self._filter_for_agent(data, data_type)
            elif user_role == UserRole.ADMIN:
                return data  # Admin gets all data

            return []

        except Exception as e:
            logger.error(f"Error filtering data by role: {e}")
            return []

    def _filter_for_agent(self, data: List[Dict], data_type: str) -> List[Dict]:
        """Filter data for agent role - public + agent resources"""
        filtered_data = []

        for item in data:
            # Agents can see most data but not confidential admin info
            safe_item = item.copy()

            # Remove confidential admin fields
            confidential_fields = [
                "hr_notes",
                "legal_issues",
                "confidential_financials",
                "internal_disputes",
                "sensitive_legal_docs",
                "admin_notes",
            ]

            for field in confidential_fields:
                safe_item.pop(field, None)

            filtered_data.append(safe_item)

        return filtered_data

    def get_allowed_data_types(self, user_role: UserRole) -> List[str]:
        """Get list of data types allowed for user role"""
        allowed_types = []

        for data_type, rule in self.access_rules.items():
            if user_role in rule.allowed_roles:
                allowed_types.append(data_type)

        return allowed_types

    def create_session_context(
        self, user_id: str, session_id: str, user_role: UserRole
    ) -> Dict[str, Any]:
        """Create session context with access controls"""
        return {
            "user_id": user_id,
            "session_id": session_id,
            "user_role": user_role.value,
            "allowed_data_types": self.get_allowed_data_types(user_role),
            "access_level": self._get_access_level(user_role),
            "session_created_at": datetime.now().isoformat(),
            "session_expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
        }

    def _get_access_level(self, user_role: UserRole) -> str:
        """Get access level for user role"""
        if user_role == UserRole.ADMIN:
            return "confidential"
        elif user_role == UserRole.AGENT:
            return "agent"
        else:
            return "public"

    def audit_access(
        self,
        user_id: str,
        session_id: str,
        user_role: UserRole,
        data_type: str,
        action: str,
        success: bool,
    ) -> None:
        """Audit access attempts for security monitoring"""
        try:
            with self.engine.connect() as conn:
                conn.execute(
                    text(
                        """
                    INSERT INTO access_audit_log (
                        user_id, session_id, user_role, data_type, action, 
                        success, timestamp, ip_address
                    ) VALUES (
                        :user_id, :session_id, :user_role, :data_type, :action,
                        :success, CURRENT_TIMESTAMP, :ip_address
                    )
                """
                    ),
                    {
                        "user_id": user_id,
                        "session_id": session_id,
                        "user_role": user_role.value,
                        "data_type": data_type,
                        "action": action,
                        "success": success,
                        "ip_address": "127.0.0.1",  # TODO: Get actual IP
                    },
                )
                conn.commit()

        except Exception as e:
            logger.error(f"Error auditing access: {e}")


# Global RBAC manager instance
rbac_manager = None


def initialize_rbac(db_url: str):
    """Initialize the global RBAC manager"""
    global rbac_manager
    rbac_manager = RBACManager(db_url)
    logger.info("✅ RBAC Manager initialized successfully")


def get_rbac_manager() -> RBACManager:
    """Get the global RBAC manager instance"""
    if rbac_manager is None:
        raise RuntimeError(
            "RBAC Manager not initialized. Call initialize_rbac() first."
        )
    return rbac_manager
