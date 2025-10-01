"""
AI Processing Service
====================

This service handles the actual AI processing for each team's requests.
It integrates with various AI models and services to generate content.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import google.generativeai as genai
from sqlalchemy.orm import Session

from app.domain.listings.ai_request_models import (
    AIRequest,
    AIRequestStep,
    Deliverable,
    Template,
)
from auth.database import get_db

logger = logging.getLogger(__name__)


"""
AI Processing Service
====================

This service handles the actual AI processing for each team's requests.
It integrates with various AI models and services to generate content.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from fastapi import HTTPException, status
from enum import Enum
import os
import uuid

from app.domain.listings.ai_request_models import (
    AIRequestNew as AIRequest,
    AIRequestStep,
    Deliverable,
    Template,
)
from app.domain.listings.ai_assistant_models import (
    HumanExpert,
    ContentDeliverable,
    VoiceRequest,
)
from auth.database import get_db

logger = logging.getLogger(__name__)

class RequestType(str, Enum):
    """AI request types"""
    CMA = "cma"
    PRESENTATION = "presentation"
    MARKETING = "marketing"
    COMPLIANCE = "compliance"
    GENERAL = "general"
    FOLLOW_UP = "follow_up"
    REPORT = "report"
    SOCIAL_MEDIA = "social_media"

class RequestStatus(str, Enum):
    """AI request status"""
    PENDING = "pending"
    PROCESSING = "processing"
    AI_COMPLETE = "ai_complete"
    HUMAN_REVIEW = "human_review"
    COMPLETED = "completed"
    FAILED = "failed"

class RequestPriority(str, Enum):
    """Request priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class AIProcessingService:
    """Service for processing AI requests through different team pipelines"""
    
    def __init__(self, db: Session):
        self.db = db
        self.setup_ai_models()
    
    def setup_ai_models(self):
        """Initialize AI models and services"""
        try:
            # Configure Google Generative AI
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Google Generative AI configured")
            else:
                logger.warning("⚠️ GOOGLE_API_KEY not found, using mock responses")
                self.gemini_model = None
        except Exception as e:
            logger.error(f"❌ Failed to setup AI models: {e}")
            self.gemini_model = None

    async def create_ai_request(
        self,
        agent_id: int,
        brokerage_id: int,
        request_type: str,
        request_content: str = None,
        request_metadata: Optional[Dict[str, Any]] = None,
        priority: str = RequestPriority.NORMAL,
        output_format: str = "text",
        team: str = "general",
        audio_file_path: str = None
    ) -> Dict[str, Any]:
        """Create a new AI request"""
        try:
            if audio_file_path:
                voice_service = VoiceProcessingService(self.db)
                transcription_result = await voice_service.transcribe_audio(audio_file_path)
                if transcription_result["success"]:
                    request_content = transcription_result["text"]
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to transcribe audio"
                    )

            # Validate request type
            if request_type not in [rt.value for rt in RequestType]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid request type: {request_type}"
                )
            
            # Create AI request
            ai_request = AIRequest(
                user_id=agent_id,
                brokerage_id=brokerage_id,
                team=team,
                title=request_content[:100] + "..." if len(request_content) > 100 else request_content,
                description=request_content,
                content=request_content,
                request_metadata=request_metadata or {},
                priority=priority,
                output_format=output_format,
                status=RequestStatus.PENDING,
                eta=self._calculate_estimated_completion(request_type, priority)
            )
            
            self.db.add(ai_request)
            self.db.commit()
            self.db.refresh(ai_request)
            
            # Start processing
            asyncio.create_task(self.process_request(str(ai_request.id)))
            
            logger.info(f"Created AI request {ai_request.id} for agent {agent_id}")
            
            return {
                "request_id": str(ai_request.id),
                "status": ai_request.status,
                "estimated_completion": ai_request.eta,
                "message": "Request created successfully and processing started"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating AI request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create AI request: {str(e)}"
            )

    async def process_request(self, request_id: str) -> bool:
        """Process an AI request through the appropriate team pipeline"""
        try:
            request_uuid = uuid.UUID(request_id)
            ai_request = self.db.query(AIRequest).filter(AIRequest.id == request_uuid).first()
            
            if not ai_request:
                logger.error(f"Request {request_id} not found")
                return False
            
            # Update request status
            ai_request.status = 'planning'
            ai_request.started_at = datetime.now()
            self.db.commit()
            
            # Get team-specific processor
            processor = self.get_team_processor(ai_request.team)
            if not processor:
                logger.error(f"No processor found for team: {ai_request.team}")
                ai_request.status = 'failed'
                self.db.commit()
                return False
            
            # Process through team pipeline
            success = await processor.process(ai_request)
            
            if success:
                ai_request.status = 'draft_ready'
                ai_request.completed_at = datetime.now()
            else:
                ai_request.status = 'failed'
            
            self.db.commit()
            return success
            
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}")
            # Update request status to failed
            try:
                ai_request = self.db.query(AIRequest).filter(AIRequest.id == request_uuid).first()
                if ai_request:
                    ai_request.status = 'failed'
                    self.db.commit()
            except:
                pass
            return False
    
    def get_team_processor(self, team: str):
        """Get the appropriate processor for the team"""
        processors = {
            'marketing': MarketingProcessor(self.db),
            'analytics': AnalyticsProcessor(self.db),
            'social': SocialProcessor(self.db),
            'strategy': StrategyProcessor(self.db),
            'packages': PackagesProcessor(self.db),
            'transactions': TransactionsProcessor(self.db),
            'general': GeneralProcessor(self.db)
        }
        return processors.get(team)

    def _calculate_estimated_completion(self, request_type: str, priority: str) -> datetime:
        """Calculate estimated completion time"""
        base_times = {
            RequestType.CMA: timedelta(hours=2),
            RequestType.PRESENTATION: timedelta(hours=4),
            RequestType.MARKETING: timedelta(hours=1),
            RequestType.COMPLIANCE: timedelta(hours=3),
            RequestType.GENERAL: timedelta(hours=1)
        }
        
        priority_multipliers = {
            RequestPriority.URGENT: 0.5,
            RequestPriority.HIGH: 0.75,
            RequestPriority.NORMAL: 1.0,
            RequestPriority.LOW: 1.5
        }
        
        base_time = base_times.get(request_type, timedelta(hours=1))
        multiplier = priority_multipliers.get(priority, 1.0)
        
        return datetime.utcnow() + (base_time * multiplier)

class BaseTeamProcessor:
    """Base class for team-specific processors"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def process(self, request: AIRequest) -> bool:
        """Process a request through the team pipeline"""
        try:
            # Step 1: Planning
            await self.update_step(request.id, 'planning', 'in_progress', 0)
            plan = await self.create_plan(request)
            await self.update_step(request.id, 'planning', 'completed', 100)
            
            # Step 2: Generating
            await self.update_step(request.id, 'generating', 'in_progress', 0)
            content = await self.generate_content(request, plan)
            await self.update_step(request.id, 'generating', 'completed', 100)
            
            # Step 3: Validating
            await self.update_step(request.id, 'validating', 'in_progress', 0)
            validated = await self.validate_content(request, content)
            await self.update_step(request.id, 'validating', 'completed', 100)
            
            # Step 4: Create deliverables
            await self.create_deliverables(request, validated)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            return False
    
    async def update_step(self, request_id: str, step: str, status: str, progress: int):
        """Update a pipeline step"""
        step_obj = self.db.query(AIRequestStep).filter(
            AIRequestStep.request_id == request_id,
            AIRequestStep.step == step
        ).first()
        
        if step_obj:
            step_obj.status = status
            step_obj.progress = progress
            if status == 'in_progress' and not step_obj.started_at:
                step_obj.started_at = datetime.now()
            elif status == 'completed':
                step_obj.finished_at = datetime.now()
            self.db.commit()
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a plan for the request"""
        # This would be implemented by each team
        return {"plan": "Generated plan for request"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content based on the plan"""
        # This would be implemented by each team
        return {"content": "Generated content"}
    
    async def validate_content(self, request: AIRequest, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated content"""
        # This would be implemented by each team
        return content
    
    async def create_deliverables(self, request: AIRequest, content: Dict[str, Any]):
        """Create deliverables from the content"""
        # Create a mock deliverable
        deliverable = Deliverable(
            request_id=request.id,
            type='pdf',
            name=f'{request.team.title()} Output.pdf',
            description=f'AI-generated {request.team} content',
            url=f'/deliverables/{request.id}/output.pdf',
            preview_url=f'/previews/{request.id}/output.jpg',
            status='ready'
        )
        self.db.add(deliverable)
        self.db.commit()

class GeneralProcessor(BaseTeamProcessor):
    """Processor for general requests"""
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        return {"plan": "No plan needed for general request", "type": "general"}

    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Answer the following request: {request.content}"
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "general"}

class MarketingProcessor(BaseTeamProcessor):
    """Processor for marketing team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a marketing plan"""
        prompt = f"""
        Create a marketing plan for the following request:
        
        Team: Marketing
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Target audience analysis
        2. Key messaging strategy
        3. Content format recommendations
        4. Distribution channels
        5. Success metrics
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "marketing"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketing content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate marketing content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create engaging, professional marketing content that:
        - Appeals to the target audience
        - Includes compelling calls-to-action
        - Maintains brand consistency
        - Is optimized for the specified format
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "marketing"}
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID"""
        if not template_id:
            return None
        
        template = self.db.query(Template).filter(Template.id == template_id).first()
        if template:
            return {
                "id": template.id,
                "name": template.name,
                "prompt_template": template.prompt_template,
                "output_format": template.output_format
            }
        return None

class AnalyticsProcessor(BaseTeamProcessor):
    """Processor for analytics team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create an analytics plan"""
        prompt = f"""
        Create an analytics plan for the following request:
        
        Team: Analytics
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Data requirements and sources
        2. Analysis methodology
        3. Key metrics to calculate
        4. Visualization recommendations
        5. Report structure
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "analytics"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analytics content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate analytics content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create comprehensive analytics content that:
        - Provides data-driven insights
        - Includes relevant metrics and KPIs
        - Uses clear, professional language
        - Includes actionable recommendations
        - Is structured for easy understanding
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "analytics"}

class SocialProcessor(BaseTeamProcessor):
    """Processor for social media team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a social media plan"""
        prompt = f"""
        Create a social media plan for the following request:
        
        Team: Social Media
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Platform selection and rationale
        2. Content format and style
        3. Hashtag strategy
        4. Engagement tactics
        5. Posting schedule recommendations
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "social"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate social media content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create engaging social media content that:
        - Is platform-appropriate
        - Includes relevant hashtags
        - Encourages engagement
        - Maintains brand voice
        - Is visually appealing
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "social"}

class StrategyProcessor(BaseTeamProcessor):
    """Processor for strategy team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a strategy plan"""
        prompt = f"""
        Create a strategic plan for the following request:
        
        Team: Strategy
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Strategic objectives
        2. Market analysis
        3. Competitive positioning
        4. Implementation roadmap
        5. Success metrics and KPIs
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "strategy"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategy content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate strategic content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create comprehensive strategic content that:
        - Provides clear strategic direction
        - Includes actionable recommendations
        - Addresses market opportunities
        - Defines success criteria
        - Is professionally structured
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "strategy"}

class PackagesProcessor(BaseTeamProcessor):
    """Processor for packages team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a packages plan"""
        prompt = f"""
        Create a service package plan for the following request:
        
        Team: Packages
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Service components
        2. Pricing structure
        3. Delivery timeline
        4. Value propositions
        5. Terms and conditions
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "packages"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate packages content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate service package content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create compelling package content that:
        - Clearly outlines service offerings
        - Highlights value and benefits
        - Includes transparent pricing
        - Addresses client needs
        - Is professionally presented
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "packages"}

class TransactionsProcessor(BaseTeamProcessor):
    """Processor for transactions team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a transactions plan"""
        prompt = f"""
        Create a transaction management plan for the following request:
        
        Team: Transactions
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Transaction requirements
        2. Compliance considerations
        3. Risk assessment
        4. Process steps
        5. Documentation needs
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "transactions"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate transactions content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate transaction content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create comprehensive transaction content that:
        - Ensures legal compliance
        - Addresses all requirements
        - Minimizes risks
        - Provides clear guidance
        - Is professionally structured
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "transactions"}

# Helper function for AI model calls
async def call_ai_model(prompt: str) -> str:
    """Call the AI model with the given prompt"""
    try:
        if genai_model:
            response = genai_model.generate_content(prompt)
            return response.text
        else:
            # Mock response for testing
            return f"AI-generated response for: {prompt[:100]}..."
    except Exception as e:
        logger.error(f"AI model call failed: {e}")
        return f"Error generating content: {str(e)}"

class BaseTeamProcessor:
    """Base class for team-specific processors"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def process(self, request: AIRequest) -> bool:
        """Process a request through the team pipeline"""
        try:
            # Step 1: Planning
            await self.update_step(request.id, 'planning', 'in_progress', 0)
            plan = await self.create_plan(request)
            await self.update_step(request.id, 'planning', 'completed', 100)
            
            # Step 2: Generating
            await self.update_step(request.id, 'generating', 'in_progress', 0)
            content = await self.generate_content(request, plan)
            await self.update_step(request.id, 'generating', 'completed', 100)
            
            # Step 3: Validating
            await self.update_step(request.id, 'validating', 'in_progress', 0)
            validated = await self.validate_content(request, content)
            await self.update_step(request.id, 'validating', 'completed', 100)
            
            # Step 4: Create deliverables
            await self.create_deliverables(request, validated)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            return False
    
    async def update_step(self, request_id: str, step: str, status: str, progress: int):
        """Update a pipeline step"""
        step_obj = self.db.query(AIRequestStep).filter(
            AIRequestStep.request_id == request_id,
            AIRequestStep.step == step
        ).first()
        
        if step_obj:
            step_obj.status = status
            step_obj.progress = progress
            if status == 'in_progress' and not step_obj.started_at:
                step_obj.started_at = datetime.now()
            elif status == 'completed':
                step_obj.finished_at = datetime.now()
            self.db.commit()
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a plan for the request"""
        # This would be implemented by each team
        return {"plan": "Generated plan for request"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content based on the plan"""
        # This would be implemented by each team
        return {"content": "Generated content"}
    
    async def validate_content(self, request: AIRequest, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the generated content"""
        # This would be implemented by each team
        return content
    
    async def create_deliverables(self, request: AIRequest, content: Dict[str, Any]):
        """Create deliverables from the content"""
        # Create a mock deliverable
        deliverable = Deliverable(
            request_id=request.id,
            type='pdf',
            name=f'{request.team.title()} Output.pdf',
            description=f'AI-generated {request.team} content',
            url=f'/deliverables/{request.id}/output.pdf',
            preview_url=f'/previews/{request.id}/output.jpg',
            status='ready'
        )
        self.db.add(deliverable)
        self.db.commit()

class MarketingProcessor(BaseTeamProcessor):
    """Processor for marketing team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a marketing plan"""
        prompt = f"""
        Create a marketing plan for the following request:
        
        Team: Marketing
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Target audience analysis
        2. Key messaging strategy
        3. Content format recommendations
        4. Distribution channels
        5. Success metrics
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "marketing"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate marketing content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate marketing content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create engaging, professional marketing content that:
        - Appeals to the target audience
        - Includes compelling calls-to-action
        - Maintains brand consistency
        - Is optimized for the specified format
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "marketing"}
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID"""
        if not template_id:
            return None
        
        template = self.db.query(Template).filter(Template.id == template_id).first()
        if template:
            return {
                "id": template.id,
                "name": template.name,
                "prompt_template": template.prompt_template,
                "output_format": template.output_format
            }
        return None

class AnalyticsProcessor(BaseTeamProcessor):
    """Processor for analytics team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create an analytics plan"""
        prompt = f"""
        Create an analytics plan for the following request:
        
        Team: Analytics
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Data requirements and sources
        2. Analysis methodology
        3. Key metrics to calculate
        4. Visualization recommendations
        5. Report structure
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "analytics"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analytics content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate analytics content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create comprehensive analytics content that:
        - Provides data-driven insights
        - Includes relevant metrics and KPIs
        - Uses clear, professional language
        - Includes actionable recommendations
        - Is structured for easy understanding
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "analytics"}

class SocialProcessor(BaseTeamProcessor):
    """Processor for social media team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a social media plan"""
        prompt = f"""
        Create a social media plan for the following request:
        
        Team: Social Media
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Platform selection and rationale
        2. Content format and style
        3. Hashtag strategy
        4. Engagement tactics
        5. Posting schedule recommendations
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "social"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate social media content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create engaging social media content that:
        - Is platform-appropriate
        - Includes relevant hashtags
        - Encourages engagement
        - Maintains brand voice
        - Is visually appealing
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "social"}

class StrategyProcessor(BaseTeamProcessor):
    """Processor for strategy team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a strategy plan"""
        prompt = f"""
        Create a strategic plan for the following request:
        
        Team: Strategy
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Strategic objectives
        2. Market analysis
        3. Competitive positioning
        4. Implementation roadmap
        5. Success metrics and KPIs
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "strategy"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategy content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate strategic content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create comprehensive strategic content that:
        - Provides clear strategic direction
        - Includes actionable recommendations
        - Addresses market opportunities
        - Defines success criteria
        - Is professionally structured
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "strategy"}

class PackagesProcessor(BaseTeamProcessor):
    """Processor for packages team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a packages plan"""
        prompt = f"""
        Create a service package plan for the following request:
        
        Team: Packages
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Service components
        2. Pricing structure
        3. Delivery timeline
        4. Value propositions
        5. Terms and conditions
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "packages"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate packages content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate service package content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create compelling package content that:
        - Clearly outlines service offerings
        - Highlights value and benefits
        - Includes transparent pricing
        - Addresses client needs
        - Is professionally presented
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "packages"}

class TransactionsProcessor(BaseTeamProcessor):
    """Processor for transactions team requests"""
    
    async def create_plan(self, request: AIRequest) -> Dict[str, Any]:
        """Create a transactions plan"""
        prompt = f"""
        Create a transaction management plan for the following request:
        
        Team: Transactions
        Content: {request.content}
        Template: {request.template_id or 'None'}
        
        Please create a detailed plan including:
        1. Transaction requirements
        2. Compliance considerations
        3. Risk assessment
        4. Process steps
        5. Documentation needs
        """
        
        plan = await self.call_ai_model(prompt)
        return {"plan": plan, "type": "transactions"}
    
    async def generate_content(self, request: AIRequest, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate transactions content"""
        template = self.get_template(request.template_id)
        
        prompt = f"""
        Generate transaction content based on this plan:
        
        Plan: {plan['plan']}
        Original Request: {request.content}
        Template: {template.get('prompt_template', '') if template else 'None'}
        
        Create comprehensive transaction content that:
        - Ensures legal compliance
        - Addresses all requirements
        - Minimizes risks
        - Provides clear guidance
        - Is professionally structured
        """
        
        content = await self.call_ai_model(prompt)
        return {"content": content, "type": "transactions"}

# Helper function for AI model calls
async def call_ai_model(prompt: str) -> str:
    """Call the AI model with the given prompt"""
    try:
        if genai_model:
            response = genai_model.generate_content(prompt)
            return response.text
        else:
            # Mock response for testing
            return f"AI-generated response for: {prompt[:100]}..."
    except Exception as e:
        logger.error(f"AI model call failed: {e}")
        return f"Error generating content: {str(e)}"
