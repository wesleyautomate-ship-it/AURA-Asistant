#!/usr/bin/env python3
"""
Enhanced Action Engine for Blueprint 2.0: Proactive AI Copilot
Handles proactive lead nurturing, follow-up suggestions, and context retrieval
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize database connection
db_url = os.getenv('DATABASE_URL', 'postgresql://admin:password123@localhost:5432/real_estate_db')
engine = create_engine(db_url)

class ActionEngine:
    """Enhanced action engine for proactive lead nurturing and real estate operations"""
    
    def __init__(self, ai_model=None):
        self.ai_model = ai_model
        
        # Import Celery tasks
        try:
            from tasks.ai_commands import execute_ai_command, get_task_status
            self.execute_ai_command_task = execute_ai_command
            self.get_task_status_task = get_task_status
            logger.info("✅ Celery tasks imported successfully")
        except ImportError as e:
            logger.warning(f"⚠️ Celery tasks not available: {e}")
            self.execute_ai_command_task = None
            self.get_task_status_task = None
        
        # Enhanced real estate specific features
        self.follow_up_channels = ['email', 'sms', 'whatsapp', 'phone', 'in_person']
        self.nurture_statuses = ['New', 'Contacted', 'Qualified', 'Nurturing', 'Hot', 'Warm', 'Cold', 'Closed']
        self.interaction_types = ['email', 'call', 'sms', 'whatsapp', 'meeting', 'viewing', 'note', 'follow_up']
    
    def get_follow_up_context(self, lead_id: int) -> Dict[str, Any]:
        """
        Retrieves the last 5 interactions for a lead to help generate a follow-up script.
        """
        try:
            with engine.connect() as conn:
                # Get lead profile
                lead_result = conn.execute(text("""
                    SELECT id, name, email, phone, status, budget_min, budget_max, 
                           preferred_areas, property_type, last_contacted_at, 
                           next_follow_up_at, nurture_status, notes
                    FROM leads 
                    WHERE id = :lead_id
                """), {'lead_id': lead_id})
                
                lead_row = lead_result.fetchone()
                if not lead_row:
                    return {"error": "Lead not found"}
                
                lead_profile = {
                    "id": lead_row.id,
                    "name": lead_row.name,
                    "email": lead_row.email,
                    "phone": lead_row.phone,
                    "status": lead_row.status,
                    "budget_min": float(lead_row.budget_min) if lead_row.budget_min else None,
                    "budget_max": float(lead_row.budget_max) if lead_row.budget_max else None,
                    "preferred_areas": json.loads(lead_row.preferred_areas) if lead_row.preferred_areas and isinstance(lead_row.preferred_areas, str) else [],
                    "property_type": lead_row.property_type,
                    "last_contacted_at": lead_row.last_contacted_at.isoformat() if lead_row.last_contacted_at else None,
                    "next_follow_up_at": lead_row.next_follow_up_at.isoformat() if lead_row.next_follow_up_at else None,
                    "nurture_status": lead_row.nurture_status,
                    "notes": lead_row.notes
                }
                
                # Get recent interaction history
                history_result = conn.execute(text("""
                    SELECT id, content, created_at, scheduled_for
                    FROM lead_history 
                    WHERE lead_id = :lead_id 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """), {'lead_id': lead_id})
                
                history = []
                for row in history_result.fetchall():
                    history.append({
                        "id": row.id,
                        "interaction_type": "note",  # Default to note since column doesn't exist yet
                        "content": row.content,
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                        "scheduled_for": row.scheduled_for.isoformat() if row.scheduled_for else None
                    })
                
                return {
                    "profile": lead_profile,
                    "history": history,
                    "days_since_last_contact": self._calculate_days_since_contact(lead_profile.get("last_contacted_at"))
                }
        except Exception as e:
            logger.error(f"Error getting follow-up context for lead {lead_id}: {e}")
            return {"error": f"Failed to retrieve lead context: {str(e)}"}
    
    def execute_ai_command(self, command: str, user_id: int, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an AI command asynchronously using Celery task queue
        
        Args:
            command: The AI command to execute
            user_id: ID of the user who issued the command
            context: Additional context for the command
            
        Returns:
            Dict containing task information
        """
        try:
            if not self.execute_ai_command_task:
                logger.error("Celery tasks not available")
                return {"error": "Task queue not available"}
            
            # Queue the task for asynchronous execution
            task = self.execute_ai_command_task.delay(command, user_id, context)
            
            logger.info(f"AI command queued for execution: {task.id}")
            
            return {
                "status": "queued",
                "task_id": task.id,
                "command": command,
                "user_id": user_id,
                "message": "Command has been queued for processing"
            }
            
        except Exception as e:
            logger.error(f"Error queuing AI command: {e}")
            return {"error": f"Failed to queue command: {str(e)}"}
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a queued task
        
        Args:
            task_id: The Celery task ID
            
        Returns:
            Dict containing task status and result
        """
        try:
            if not self.get_task_status_task:
                logger.error("Celery tasks not available")
                return {"error": "Task queue not available"}
            
            # Get task status
            status_result = self.get_task_status_task.delay(task_id)
            status = status_result.get()
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return {"error": f"Failed to get task status: {str(e)}"}
    
    def create_nurture_suggestion(self, lead_id: int) -> Dict[str, Any]:
        """
        Generate follow-up suggestions based on lead context and history.
        """
        try:
            context = self.get_follow_up_context(lead_id)
            if "error" in context:
                return context
            
            lead_profile = context["profile"]
            history = context["history"]
            days_since_contact = context["days_since_last_contact"]
            
            # Generate suggestion based on context
            suggestion = self._generate_nurture_suggestion(lead_profile, history, days_since_contact)
            
            return {
                "lead_id": lead_id,
                "lead_name": lead_profile["name"],
                "suggestion": suggestion,
                "urgency": self._calculate_urgency(days_since_contact, lead_profile["nurture_status"]),
                "recommended_action": self._get_recommended_action(lead_profile, history),
                "context_summary": self._create_context_summary(lead_profile, history)
            }
            
        except Exception as e:
            logger.error(f"Error creating nurture suggestion for lead {lead_id}: {e}")
            return {"error": f"Failed to create nurture suggestion: {str(e)}"}
    
    def schedule_follow_up(self, lead_id: int, follow_up_date: datetime, 
                          interaction_type: str = "follow_up", notes: str = "") -> Dict[str, Any]:
        """
        Schedule a future follow-up interaction for a lead.
        """
        try:
            with engine.connect() as conn:
                # Add to lead history as scheduled interaction
                conn.execute(text("""
                    INSERT INTO lead_history 
                    (lead_id, agent_id, interaction_type, content, scheduled_for, created_at)
                    VALUES (:lead_id, :agent_id, :interaction_type, :content, :scheduled_for, NOW())
            """), {
                    'lead_id': lead_id,
                    'agent_id': 1,  # Default agent ID - in production, get from auth
                    'interaction_type': interaction_type,
                    'content': notes,
                    'scheduled_for': follow_up_date
                })
                
                # Update lead's next follow-up date
                conn.execute(text("""
                UPDATE leads 
                    SET next_follow_up_at = :follow_up_date, 
                        updated_at = NOW()
                    WHERE id = :lead_id
            """), {
                    'follow_up_date': follow_up_date,
                    'lead_id': lead_id
                })
                
                conn.commit()
                
                return {
                    "success": True,
                    "message": f"Follow-up scheduled for {follow_up_date.strftime('%B %d, %Y at %I:%M %p')}",
                    "lead_id": lead_id,
                    "scheduled_date": follow_up_date.isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error scheduling follow-up for lead {lead_id}: {e}")
            return {"error": f"Failed to schedule follow-up: {str(e)}"}
    
    def log_interaction(self, lead_id: int, interaction_type: str, content: str, 
                       agent_id: int = 1) -> Dict[str, Any]:
        """
        Log a new interaction with a lead.
        """
        try:
            with engine.connect() as conn:
                # Add interaction to history
                conn.execute(text("""
                    INSERT INTO lead_history 
                    (lead_id, agent_id, interaction_type, content, created_at)
                    VALUES (:lead_id, :agent_id, :interaction_type, :content, NOW())
            """), {
                    'lead_id': lead_id,
                    'agent_id': agent_id,
                    'interaction_type': interaction_type,
                    'content': content
                })
                
                # Update lead's last contacted timestamp
                conn.execute(text("""
                UPDATE leads 
                    SET last_contacted_at = NOW(), 
                        updated_at = NOW()
                    WHERE id = :lead_id
                """), {'lead_id': lead_id})
                
                conn.commit()
                
                return {
                    "success": True,
                    "message": "Interaction logged successfully",
                    "lead_id": lead_id,
                    "interaction_type": interaction_type,
                    "logged_at": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error logging interaction for lead {lead_id}: {e}")
            return {"error": f"Failed to log interaction: {str(e)}"}
    
    def get_leads_needing_follow_up(self, agent_id: int = None, days_threshold: int = 5) -> List[Dict[str, Any]]:
        """
        Get leads that need follow-up based on last contact date and nurture status.
        """
        try:
            with engine.connect() as conn:
                query = """
                    SELECT id, name, email, phone, status, nurture_status, 
                           last_contacted_at, next_follow_up_at, notes
                    FROM leads 
                    WHERE (last_contacted_at IS NULL OR 
                           last_contacted_at < NOW() - INTERVAL ':days_threshold days')
                    AND status NOT IN ('closed', 'lost')
                    AND nurture_status != 'Closed'
                """
                
                params = {'days_threshold': days_threshold}
                
                if agent_id:
                    query += " AND agent_id = :agent_id"
                    params['agent_id'] = agent_id
                
                query += " ORDER BY last_contacted_at ASC NULLS FIRST"
                
                result = conn.execute(text(query), params)
                
                leads = []
                for row in result.fetchall():
                    leads.append({
                        "id": row.id,
                        "name": row.name,
                        "email": row.email,
                        "phone": row.phone,
                        "status": row.status,
                        "nurture_status": row.nurture_status,
                        "last_contacted_at": row.last_contacted_at.isoformat() if row.last_contacted_at else None,
                        "next_follow_up_at": row.next_follow_up_at.isoformat() if row.next_follow_up_at else None,
                        "notes": row.notes,
                        "days_since_contact": self._calculate_days_since_contact(row.last_contacted_at)
                    })
                
                return leads
            
        except Exception as e:
            logger.error(f"Error getting leads needing follow-up: {e}")
            return []
    
    def _calculate_days_since_contact(self, last_contacted_at) -> int:
        """Calculate days since last contact"""
        if not last_contacted_at:
            return 999  # Never contacted
        
        if isinstance(last_contacted_at, str):
            last_contacted_at = datetime.fromisoformat(last_contacted_at.replace('Z', '+00:00'))
        
        return (datetime.now() - last_contacted_at).days
    
    def _generate_nurture_suggestion(self, lead_profile: dict, history: list, days_since_contact: int) -> str:
        """Generate nurture suggestion based on context"""
        if self.ai_model:
            # Use AI to generate personalized suggestion
            prompt = f"""
Generate a personalized follow-up suggestion for a real estate lead.

**Lead Profile:**
- Name: {lead_profile['name']}
- Status: {lead_profile['status']}
- Property Type: {lead_profile['property_type']}
- Budget: AED {lead_profile['budget_min']:,.0f} - {lead_profile['budget_max']:,.0f}
- Preferred Areas: {', '.join(lead_profile['preferred_areas'])}
- Days Since Last Contact: {days_since_contact}

**Recent Interactions:**
{json.dumps(history, indent=2)}

**Requirements:**
- Generate a 2-3 sentence personalized follow-up suggestion
- Be specific to their property preferences and budget
- Reference previous interactions if relevant
- Suggest next steps
- Keep tone professional but warm

Suggestion:
"""
            try:
                response = self.ai_model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                logger.error(f"Error generating AI suggestion: {e}")
        
        # Fallback to rule-based suggestion
        return self._get_rule_based_suggestion(lead_profile, history, days_since_contact)
    
    def _get_rule_based_suggestion(self, lead_profile: dict, history: list, days_since_contact: int) -> str:
        """Generate rule-based nurture suggestion"""
        if days_since_contact > 30:
            return f"It's been over a month since you last contacted {lead_profile['name']}. Consider reaching out with new property listings in their preferred areas ({', '.join(lead_profile['preferred_areas'])}) within their budget range."
        elif days_since_contact > 14:
            return f"Follow up with {lead_profile['name']} about their property search. They're interested in {lead_profile['property_type']} properties in {', '.join(lead_profile['preferred_areas'])}."
        elif days_since_contact > 7:
            return f"Check in with {lead_profile['name']} to see if they have any questions about the properties we discussed or if they'd like to schedule viewings."
        else:
            return f"Send a quick follow-up to {lead_profile['name']} to maintain engagement and offer additional assistance with their property search."
    
    def _calculate_urgency(self, days_since_contact: int, nurture_status: str) -> str:
        """Calculate urgency level for follow-up"""
        if days_since_contact > 30:
            return "high"
        elif days_since_contact > 14:
            return "medium"
        elif days_since_contact > 7:
            return "low"
        else:
            return "normal"
    
    def _get_recommended_action(self, lead_profile: dict, history: list) -> str:
        """Get recommended action based on lead context"""
        if not history:
            return "Initial contact - introduce yourself and understand their requirements"
        
        last_interaction = history[0]
        if last_interaction["interaction_type"] == "viewing_log":
            return "Follow up on viewing feedback and next steps"
        elif last_interaction["interaction_type"] == "email":
            return "Check if they received your email and have any questions"
        elif last_interaction["interaction_type"] == "call":
            return "Send follow-up email summarizing the call and next steps"
        else:
            return "General follow-up to maintain engagement"
    
    def _create_context_summary(self, lead_profile: dict, history: list) -> str:
        """Create a summary of lead context"""
        summary = f"{lead_profile['name']} is looking for {lead_profile['property_type']} properties"
        
        if lead_profile['preferred_areas']:
            summary += f" in {', '.join(lead_profile['preferred_areas'])}"
        
        if lead_profile['budget_min'] and lead_profile['budget_max']:
            summary += f" with a budget of AED {lead_profile['budget_min']:,.0f} - {lead_profile['budget_max']:,.0f}"
        
        if history:
            summary += f". Last interaction was {history[0]['interaction_type']} on {history[0]['created_at'][:10]}"
        
        return summary
    
    # ============================================================================
    # ENHANCED FOLLOW-UP AND CONTACT MANAGEMENT METHODS
    # ============================================================================
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact with enhanced lead scoring"""
        try:
            with engine.connect() as conn:
                # Calculate initial lead score
                lead_score = self._calculate_lead_score(contact_data)
                
                # Insert contact
                result = conn.execute(text("""
                    INSERT INTO leads 
                    (name, email, phone, status, budget_min, budget_max, preferred_areas, 
                     property_type, lead_score, agent_id, created_at, updated_at)
                    VALUES (:name, :email, :phone, :status, :budget_min, :budget_max, 
                           :preferred_areas, :property_type, :lead_score, :agent_id, NOW(), NOW())
                    RETURNING id
                """), {
                    'name': contact_data.get('name'),
                    'email': contact_data.get('email'),
                    'phone': contact_data.get('phone'),
                    'status': contact_data.get('status', 'new'),
                    'budget_min': contact_data.get('budget_min'),
                    'budget_max': contact_data.get('budget_max'),
                    'preferred_areas': json.dumps(contact_data.get('preferred_areas', [])),
                    'property_type': contact_data.get('property_type'),
                    'lead_score': lead_score,
                    'agent_id': contact_data.get('agent_id', 1)
                })
                
                contact_id = result.fetchone()[0]
                conn.commit()
                
                # Log initial interaction
                self.log_interaction(contact_id, 'initial_contact', 'Contact created', contact_data.get('agent_id', 1))
                
                return {
                    "success": True,
                    "contact_id": contact_id,
                    "lead_score": lead_score,
                    "message": "Contact created successfully"
                }
                
        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            return {"error": f"Failed to create contact: {str(e)}"}
    
    def update_contact(self, contact_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact information and recalculate lead score"""
        try:
            with engine.connect() as conn:
                # Get current contact data
                current_result = conn.execute(text("""
                    SELECT name, email, phone, budget_min, budget_max, preferred_areas, 
                           property_type, lead_score
                    FROM leads WHERE id = :contact_id
                """), {'contact_id': contact_id})
                
                current_data = current_result.fetchone()
                if not current_data:
                    return {"error": "Contact not found"}
                
                # Merge current data with updates
                updated_data = {
                    'name': update_data.get('name', current_data.name),
                    'email': update_data.get('email', current_data.email),
                    'phone': update_data.get('phone', current_data.phone),
                    'budget_min': update_data.get('budget_min', current_data.budget_min),
                    'budget_max': update_data.get('budget_max', current_data.budget_max),
                    'preferred_areas': update_data.get('preferred_areas', 
                                                      json.loads(current_data.preferred_areas) if current_data.preferred_areas else []),
                    'property_type': update_data.get('property_type', current_data.property_type)
                }
                
                # Recalculate lead score
                new_lead_score = self._calculate_lead_score(updated_data)
                
                # Update contact
                conn.execute(text("""
                    UPDATE leads 
                    SET name = :name, email = :email, phone = :phone, 
                        budget_min = :budget_min, budget_max = :budget_max,
                        preferred_areas = :preferred_areas, property_type = :property_type,
                        lead_score = :lead_score, updated_at = NOW()
                    WHERE id = :contact_id
                """), {
                    'contact_id': contact_id,
                    'name': updated_data['name'],
                    'email': updated_data['email'],
                    'phone': updated_data['phone'],
                    'budget_min': updated_data['budget_min'],
                    'budget_max': updated_data['budget_max'],
                    'preferred_areas': json.dumps(updated_data['preferred_areas']),
                    'property_type': updated_data['property_type'],
                    'lead_score': new_lead_score
                })
                
                conn.commit()
                
                return {
                    "success": True,
                    "contact_id": contact_id,
                    "new_lead_score": new_lead_score,
                    "message": "Contact updated successfully"
                }
                
        except Exception as e:
            logger.error(f"Error updating contact: {e}")
            return {"error": f"Failed to update contact: {str(e)}"}
    
    def get_contact_details(self, contact_id: int) -> Dict[str, Any]:
        """Get comprehensive contact details with interaction history"""
        try:
            with engine.connect() as conn:
                # Get contact details
                contact_result = conn.execute(text("""
                    SELECT id, name, email, phone, status, budget_min, budget_max, 
                           preferred_areas, property_type, lead_score, nurture_status,
                           last_contacted_at, next_follow_up_at, notes, created_at
                    FROM leads WHERE id = :contact_id
                """), {'contact_id': contact_id})
                
                contact_row = contact_result.fetchone()
                if not contact_row:
                    return {"error": "Contact not found"}
                
                # Get interaction history
                history_result = conn.execute(text("""
                    SELECT id, interaction_type, content, created_at, scheduled_for
                    FROM lead_history 
                    WHERE lead_id = :contact_id 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """), {'contact_id': contact_id})
                
                interactions = []
                for row in history_result.fetchall():
                    interactions.append({
                        "id": row.id,
                        "interaction_type": row.interaction_type,
                        "content": row.content,
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                        "scheduled_for": row.scheduled_for.isoformat() if row.scheduled_for else None
                    })
                
                return {
                    "contact_id": contact_row.id,
                    "name": contact_row.name,
                    "email": contact_row.email,
                    "phone": contact_row.phone,
                    "status": contact_row.status,
                    "budget_min": float(contact_row.budget_min) if contact_row.budget_min else None,
                    "budget_max": float(contact_row.budget_max) if contact_row.budget_max else None,
                    "preferred_areas": json.loads(contact_row.preferred_areas) if contact_row.preferred_areas else [],
                    "property_type": contact_row.property_type,
                    "lead_score": float(contact_row.lead_score) if contact_row.lead_score else 0,
                    "nurture_status": contact_row.nurture_status,
                    "last_contacted_at": contact_row.last_contacted_at.isoformat() if contact_row.last_contacted_at else None,
                    "next_follow_up_at": contact_row.next_follow_up_at.isoformat() if contact_row.next_follow_up_at else None,
                    "notes": contact_row.notes,
                    "created_at": contact_row.created_at.isoformat() if contact_row.created_at else None,
                    "interactions": interactions
                }
                
        except Exception as e:
            logger.error(f"Error getting contact details: {e}")
            return {"error": f"Failed to get contact details: {str(e)}"}
    
    def schedule_follow_up_enhanced(self, contact_id: int, follow_up_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced follow-up scheduling with multiple channels and AI suggestions"""
        try:
            with engine.connect() as conn:
                # Get contact details for context
                contact_details = self.get_contact_details(contact_id)
                if "error" in contact_details:
                    return contact_details
                
                # Generate AI-powered follow-up suggestions
                ai_suggestions = self._generate_follow_up_suggestions(contact_details, follow_up_data)
                
                # Schedule follow-up
                follow_up_date = follow_up_data.get('scheduled_date')
                channel = follow_up_data.get('channel', 'email')
                message = follow_up_data.get('message', '')
                
                # Add to lead history
                conn.execute(text("""
                    INSERT INTO lead_history 
                    (lead_id, agent_id, interaction_type, content, scheduled_for, created_at)
                    VALUES (:lead_id, :agent_id, :interaction_type, :content, :scheduled_for, NOW())
                """), {
                    'lead_id': contact_id,
                    'agent_id': follow_up_data.get('agent_id', 1),
                    'interaction_type': f'follow_up_{channel}',
                    'content': message,
                    'scheduled_for': follow_up_date
                })
                
                # Update lead's next follow-up date
                conn.execute(text("""
                    UPDATE leads 
                    SET next_follow_up_at = :follow_up_date, 
                        updated_at = NOW()
                    WHERE id = :contact_id
                """), {
                    'follow_up_date': follow_up_date,
                    'contact_id': contact_id
                })
                
                conn.commit()
                
                return {
                    "success": True,
                    "contact_id": contact_id,
                    "scheduled_date": follow_up_date.isoformat() if follow_up_date else None,
                    "channel": channel,
                    "ai_suggestions": ai_suggestions,
                    "message": f"Follow-up scheduled for {follow_up_date.strftime('%B %d, %Y at %I:%M %p') if follow_up_date else 'TBD'}"
                }
                
        except Exception as e:
            logger.error(f"Error scheduling enhanced follow-up: {e}")
            return {"error": f"Failed to schedule follow-up: {str(e)}"}
    
    def _calculate_lead_score(self, contact_data: Dict[str, Any]) -> float:
        """Calculate lead score based on contact data"""
        score = 0.0
        
        # Budget scoring (0-40 points)
        budget_min = contact_data.get('budget_min', 0)
        budget_max = contact_data.get('budget_max', 0)
        if budget_max > 0:
            if budget_max >= 5000000:  # 5M+ AED
                score += 40
            elif budget_max >= 3000000:  # 3M+ AED
                score += 30
            elif budget_max >= 1000000:  # 1M+ AED
                score += 20
            elif budget_max >= 500000:  # 500K+ AED
                score += 10
        
        # Property type scoring (0-20 points)
        property_type = contact_data.get('property_type', '').lower()
        if 'villa' in property_type or 'penthouse' in property_type:
            score += 20
        elif 'apartment' in property_type:
            score += 15
        elif 'townhouse' in property_type:
            score += 10
        
        # Preferred areas scoring (0-20 points)
        preferred_areas = contact_data.get('preferred_areas', [])
        premium_areas = ['downtown dubai', 'palm jumeirah', 'dubai marina', 'business bay']
        if any(area.lower() in premium_areas for area in preferred_areas):
            score += 20
        elif len(preferred_areas) > 0:
            score += 10
        
        # Contact completeness (0-20 points)
        if contact_data.get('email') and contact_data.get('phone'):
            score += 20
        elif contact_data.get('email') or contact_data.get('phone'):
            score += 10
        
        return min(score, 100.0)  # Cap at 100
    
    def _generate_follow_up_suggestions(self, contact_details: Dict[str, Any], follow_up_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered follow-up suggestions"""
        if not self.ai_model:
            return {"suggestions": ["Consider reaching out to maintain engagement"]}
        
        try:
            prompt = f"""
            Generate personalized follow-up suggestions for a real estate lead.
            
            **Contact Details:**
            - Name: {contact_details.get('name', 'Unknown')}
            - Budget: AED {contact_details.get('budget_min', 0):,.0f} - {contact_details.get('budget_max', 0):,.0f}
            - Property Type: {contact_details.get('property_type', 'Unknown')}
            - Preferred Areas: {', '.join(contact_details.get('preferred_areas', []))}
            - Lead Score: {contact_details.get('lead_score', 0)}
            - Last Contacted: {contact_details.get('last_contacted_at', 'Never')}
            
            **Follow-up Context:**
            - Channel: {follow_up_data.get('channel', 'email')}
            - Scheduled Date: {follow_up_data.get('scheduled_date', 'TBD')}
            
            Provide 3-5 specific, actionable follow-up suggestions including:
            1. Personalized message content
            2. Best time to contact
            3. Recommended next steps
            4. Property suggestions if applicable
            5. Follow-up frequency recommendations
            
            Format as JSON with keys: message_suggestions, timing_recommendations, next_steps, property_suggestions, follow_up_frequency
            """
            
            response = self.ai_model.generate_content(prompt)
            # Parse AI response and return structured suggestions
            return {
                "ai_generated": True,
                "suggestions": response.text,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating AI follow-up suggestions: {e}")
            return {
                "ai_generated": False,
                "suggestions": [
                    "Send personalized email with new property listings",
                    "Schedule a call to discuss requirements",
                    "Share market insights for their preferred areas"
                ]
            }

