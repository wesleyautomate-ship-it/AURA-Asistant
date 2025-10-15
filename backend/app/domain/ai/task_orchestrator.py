"""
AI Task Orchestration Framework
===============================

AURA-inspired task orchestration system that manages async AI workflows,
package executions, and provides status tracking with retry logic.

This system powers all AURA-style features by:
- Managing async AI task queues
- Executing workflow packages (New Listing, Lead Nurturing, etc.)
- Providing real-time status updates
- Handling retries and error recovery
- Integrating with existing AI routers
"""

import uuid
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor
import threading

# Import existing AI components
try:
    from domain.ai.action_engine import ActionEngine
    from domain.ai.ai_manager import AIEnhancementManager
except ImportError:
    ActionEngine = None
    AIEnhancementManager = None

logger = logging.getLogger(__name__)

# Import intelligence components
try:
    from app.core.ai_content_generator import ai_content_generator
    from app.schemas.intelligence import (
        ContentType,
        IntelligenceContent,
        StreamProgressEvent,
        TaskStatus as IntelligenceTaskStatus,
    )
except ImportError:
    ai_content_generator = None
    ContentType = None
    IntelligenceContent = None
    StreamProgressEvent = None
    IntelligenceTaskStatus = None


try:
    from app.domain.ai.property_brochure_service import PropertyBrochureService
except ImportError:
    PropertyBrochureService = None


class TaskStatus(str, Enum):
    """Task execution status"""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskType(str, Enum):
    """AI task types for AURA features"""

    # Marketing Automation
    CONTENT_GENERATION = "content_generation"
    POSTCARD_GENERATION = "postcard_generation"
    EMAIL_CAMPAIGN = "email_campaign"
    SOCIAL_MEDIA_POST = "social_media_post"

    # Data & Analytics
    CMA_GENERATION = "cma_generation"
    MARKET_ANALYSIS = "market_analysis"
    TREND_ANALYSIS = "trend_analysis"
    PRICE_PREDICTION = "price_prediction"

    # Strategy & Advisory
    LISTING_STRATEGY = "listing_strategy"
    NEGOTIATION_PREP = "negotiation_prep"
    INVESTMENT_OUTLOOK = "investment_outlook"

    # Lead & Client Management
    LEAD_SCORING = "lead_scoring"
    PROPERTY_MATCHING = "property_matching"
    NURTURE_SEQUENCE = "nurture_sequence"

    # Workflow & Package Management
    WORKFLOW_EXECUTION = "workflow_execution"
    PACKAGE_ORCHESTRATION = "package_orchestration"

    # Cross-cutting
    NOTIFICATION = "notification"
    API_CALL = "api_call"
    HUMAN_REVIEW = "human_review"


class TaskPriority(int, Enum):
    """Task priority levels"""

    LOW = 1
    NORMAL = 5
    HIGH = 8
    URGENT = 10


class AITaskRequest(BaseModel):
    """AI task request model"""

    task_type: TaskType
    user_id: int
    input_data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    timeout_seconds: int = 300
    context: Optional[Dict[str, Any]] = None


class AITaskResult(BaseModel):
    """AI task result model"""

    task_id: str
    status: TaskStatus
    progress: int = Field(ge=0, le=100)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0


class WorkflowStep(BaseModel):
    """Individual workflow step definition"""

    step_name: str
    step_type: TaskType
    description: str
    estimated_duration: int  # seconds
    inputs: List[str]
    outputs: List[str]
    depends_on: Optional[List[str]] = None
    ai_task_config: Optional[Dict[str, Any]] = None


class WorkflowPackage(BaseModel):
    """AURA-style workflow package definition"""

    package_id: str
    name: str
    description: str
    category: str
    steps: List[WorkflowStep]
    estimated_duration: int
    context_data: Optional[Dict[str, Any]] = None


class AITaskOrchestrator:
    """
    Main orchestrator for AI tasks and AURA-style workflow packages.

    Features:
    - Async task queue management
    - Workflow package execution
    - Status tracking and notifications
    - Error handling and retries
    - Integration with existing AI services
    - SSE streaming for real-time progress
    - Intelligence content generation
    """

    def __init__(self, db_session_factory: Callable[[], Session]):
        self.db_session_factory = db_session_factory
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_processors: Dict[TaskType, Callable] = {}
        self.action_engine = ActionEngine() if ActionEngine else None

        # SSE streaming support
        self.progress_streams: Dict[str, List[asyncio.Queue]] = {}
        self.stream_lock = threading.Lock()

        # Thread pool for intensive tasks
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Register default task processors
        self._register_default_processors()

    def _register_default_processors(self):
        """Register default task processors for AURA features"""
        self.task_processors.update(
            {
                TaskType.CONTENT_GENERATION: self._process_content_generation,
                TaskType.CMA_GENERATION: self._process_cma_generation,
                TaskType.LISTING_STRATEGY: self._process_listing_strategy,
                TaskType.LEAD_SCORING: self._process_lead_scoring,
                TaskType.SOCIAL_MEDIA_POST: self._process_social_media_post,
                TaskType.WORKFLOW_EXECUTION: self._process_workflow_execution,
                TaskType.NOTIFICATION: self._process_notification,
            }
        )

    async def submit_task(self, request: AITaskRequest) -> str:
        """
        Submit a new AI task for processing.

        Args:
            request: AI task request with type, data, and configuration

        Returns:
            task_id: Unique identifier for tracking the task
        """
        task_id = str(uuid.uuid4())

        try:
            # Store task in database
            with self.db_session_factory() as db:
                db.execute(
                    text(
                        """
                    INSERT INTO ai_tasks (id, user_id, task_type, input_data, status, 
                                        priority, progress, retries, max_retries, created_at)
                    VALUES (:task_id, :user_id, :task_type, :input_data, :status, 
                           :priority, :progress, :retries, :max_retries, :created_at)
                """
                    ),
                    {
                        "task_id": task_id,
                        "user_id": request.user_id,
                        "task_type": request.task_type.value,
                        "input_data": json.dumps(request.input_data),
                        "status": TaskStatus.QUEUED.value,
                        "priority": request.priority.value,
                        "progress": 0,
                        "retries": 0,
                        "max_retries": request.max_retries,
                        "created_at": datetime.utcnow(),
                    },
                )
                db.commit()

            # Start async processing
            asyncio.create_task(self._process_task(task_id, request))

            logger.info(f"AI task {task_id} submitted for processing")
            return task_id

        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            raise

    async def get_task_status(self, task_id: str) -> AITaskResult:
        """Get current status of a task"""
        try:
            with self.db_session_factory() as db:
                result = db.execute(
                    text(
                        """
                    SELECT id, status, progress, output_data, error_message, 
                           started_at, completed_at, retries
                    FROM ai_tasks 
                    WHERE id = :task_id
                """
                    ),
                    {"task_id": task_id},
                )

                row = result.fetchone()
                if not row:
                    raise ValueError(f"Task {task_id} not found")

                return AITaskResult(
                    task_id=row.id,
                    status=TaskStatus(row.status),
                    progress=row.progress,
                    output_data=json.loads(row.output_data)
                    if row.output_data
                    else None,
                    error_message=row.error_message,
                    started_at=row.started_at,
                    completed_at=row.completed_at,
                    retries=row.retries,
                )

        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            raise

    async def execute_workflow_package(
        self, package: WorkflowPackage, user_id: int, context: Dict[str, Any]
    ) -> str:
        """
        Execute a complete AURA-style workflow package.

        Args:
            package: Workflow package definition
            user_id: User executing the package
            context: Initial context data (property details, client info, etc.)

        Returns:
            execution_id: Unique identifier for tracking the package execution
        """
        execution_id = str(uuid.uuid4())

        try:
            # Store package execution in database
            with self.db_session_factory() as db:
                db.execute(
                    text(
                        """
                    INSERT INTO package_executions (id, package_id, user_id, title, status, 
                                                   progress, context_data, started_at, created_at)
                    VALUES (:execution_id, :package_id, :user_id, :title, :status, 
                           :progress, :context_data, :started_at, :created_at)
                """
                    ),
                    {
                        "execution_id": execution_id,
                        "package_id": package.package_id,
                        "user_id": user_id,
                        "title": f"{package.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                        "status": "running",
                        "progress": 0,
                        "context_data": json.dumps(context),
                        "started_at": datetime.utcnow(),
                        "created_at": datetime.utcnow(),
                    },
                )
                db.commit()

            # Start async package execution
            asyncio.create_task(
                self._execute_package_steps(execution_id, package, user_id, context)
            )

            logger.info(
                f"Workflow package {package.name} started with execution ID {execution_id}"
            )
            return execution_id

        except Exception as e:
            logger.error(f"Failed to execute workflow package: {e}")
            raise

    async def _process_task(self, task_id: str, request: AITaskRequest):
        """Process a single AI task"""
        try:
            # Update task status to processing
            await self._update_task_status(task_id, TaskStatus.PROCESSING, 0)

            # Get appropriate processor
            processor = self.task_processors.get(request.task_type)
            if not processor:
                raise ValueError(
                    f"No processor registered for task type {request.task_type}"
                )

            # Process the task
            result = await processor(task_id, request)

            # Update task with results
            await self._update_task_completion(
                task_id, TaskStatus.COMPLETED, 100, result
            )

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            await self._handle_task_failure(task_id, request, str(e))

    async def _execute_package_steps(
        self,
        execution_id: str,
        package: WorkflowPackage,
        user_id: int,
        context: Dict[str, Any],
    ):
        """Execute all steps in a workflow package"""
        try:
            total_steps = len(package.steps)
            completed_steps = 0
            execution_context = context.copy()

            for step in package.steps:
                try:
                    # Create step record
                    step_id = await self._create_package_step(execution_id, step)

                    # Process the step
                    step_result = await self._process_package_step(
                        step_id, step, user_id, execution_context
                    )

                    # Update execution context with step outputs
                    if step_result:
                        execution_context.update(step_result)

                    completed_steps += 1
                    progress = int((completed_steps / total_steps) * 100)

                    # Update package execution progress
                    await self._update_package_execution(
                        execution_id, "running", progress, execution_context
                    )

                except Exception as step_error:
                    logger.error(f"Step {step.step_name} failed: {step_error}")
                    await self._update_package_execution(
                        execution_id,
                        "failed",
                        progress,
                        execution_context,
                        str(step_error),
                    )
                    return

            # Mark package as completed
            await self._update_package_execution(
                execution_id, "completed", 100, execution_context
            )
            logger.info(
                f"Workflow package execution {execution_id} completed successfully"
            )

        except Exception as e:
            logger.error(f"Package execution {execution_id} failed: {e}")
            await self._update_package_execution(
                execution_id, "failed", 0, context, str(e)
            )

    async def _process_package_step(
        self, step_id: str, step: WorkflowStep, user_id: int, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Process an individual package step"""
        try:
            # Update step status
            await self._update_package_step(step_id, "running", 0)

            if step.step_type == TaskType.HUMAN_REVIEW:
                # For human review steps, mark as pending and return
                await self._update_package_step(
                    step_id, "pending", 0, {"message": "Waiting for human review"}
                )
                return {"human_review_required": True, "step_id": step_id}

            # Create AI task request for the step
            task_request = AITaskRequest(
                task_type=step.step_type,
                user_id=user_id,
                input_data={
                    "step_name": step.step_name,
                    "step_context": context,
                    "step_config": step.ai_task_config or {},
                },
            )

            # Submit and wait for task completion
            task_id = await self.submit_task(task_request)

            # Poll for completion (with timeout)
            timeout = datetime.utcnow() + timedelta(seconds=step.estimated_duration * 2)
            while datetime.utcnow() < timeout:
                task_status = await self.get_task_status(task_id)

                if task_status.status == TaskStatus.COMPLETED:
                    await self._update_package_step(
                        step_id, "completed", 100, task_status.output_data
                    )
                    return task_status.output_data
                elif task_status.status == TaskStatus.FAILED:
                    await self._update_package_step(
                        step_id, "failed", 0, {"error": task_status.error_message}
                    )
                    raise Exception(f"Step task failed: {task_status.error_message}")

                await asyncio.sleep(2)  # Poll every 2 seconds

            raise TimeoutError(f"Step {step.step_name} timed out")

        except Exception as e:
            await self._update_package_step(step_id, "failed", 0, {"error": str(e)})
            raise

    # Task Processors for AURA Features
    async def _process_content_generation(
        self, task_id: str, request: AITaskRequest
    ) -> Dict[str, Any]:
        """Process content generation tasks (marketing copy, descriptions, etc.)"""
        await self._update_task_progress(task_id, 25)

        input_data = request.input_data
        content_type = input_data.get("content_type", "general")

        if content_type == "marketing_campaign":
            return await self._generate_marketing_campaign(input_data)
        elif content_type == "property_description":
            return await self._generate_property_description(input_data)
        else:
            return await self._generate_general_content(input_data)

    async def _process_cma_generation(
        self, task_id: str, request: AITaskRequest
    ) -> Dict[str, Any]:
        """Process CMA (Comparative Market Analysis) generation"""
        await self._update_task_progress(task_id, 20)

        property_data = request.input_data
        # Integrate with existing ML insights router
        cma_data = await self._generate_cma_analysis(property_data)

        await self._update_task_progress(task_id, 80)

        return {"cma_report": cma_data, "pdf_generated": True, "confidence_score": 0.85}

    async def _process_listing_strategy(
        self, task_id: str, request: AITaskRequest
    ) -> Dict[str, Any]:
        """Process listing strategy generation"""
        await self._update_task_progress(task_id, 30)

        property_data = request.input_data
        strategy = await self._generate_listing_strategy(property_data)

        await self._update_task_progress(task_id, 90)

        return {
            "listing_strategy": strategy,
            "target_audience": strategy.get("target_audience"),
            "marketing_timeline": strategy.get("timeline"),
        }

    async def _process_social_media_post(
        self, task_id: str, request: AITaskRequest
    ) -> Dict[str, Any]:
        """Process social media post generation"""
        await self._update_task_progress(task_id, 40)

        post_data = request.input_data
        platform = post_data.get("platform", "instagram")

        content = await self._generate_social_media_content(post_data, platform)

        await self._update_task_progress(task_id, 90)

        return {
            "platform": platform,
            "content": content,
            "hashtags": content.get("hashtags", []),
            "scheduled_time": None,
        }

    async def _process_lead_scoring(
        self, task_id: str, request: AITaskRequest
    ) -> Dict[str, Any]:
        """Process lead scoring and qualification tasks"""
        await self._update_task_progress(task_id, 20)

        lead_data = request.input_data
        client_info = lead_data.get("client_info", {})
        interaction_history = lead_data.get("interaction_history", [])

        await self._update_task_progress(task_id, 50)

        # Calculate lead score based on various factors
        score_factors = {
            "budget_score": self._calculate_budget_score(client_info.get("budget", 0)),
            "engagement_score": self._calculate_engagement_score(interaction_history),
            "timeline_score": self._calculate_timeline_score(
                client_info.get("timeline", "")
            ),
            "location_match_score": self._calculate_location_score(
                client_info.get("preferred_areas", [])
            ),
        }

        overall_score = sum(score_factors.values()) / len(score_factors)
        qualification_level = self._determine_qualification_level(overall_score)

        await self._update_task_progress(task_id, 90)

        return {
            "lead_score": round(overall_score, 2),
            "qualification_level": qualification_level,
            "score_breakdown": score_factors,
            "recommended_actions": self._get_recommended_actions(qualification_level),
            "priority": "high"
            if overall_score >= 7.5
            else "medium"
            if overall_score >= 5.0
            else "low",
        }

    def _calculate_budget_score(self, budget: float) -> float:
        """Calculate score based on client budget"""
        if budget >= 2000000:  # 2M+ AED
            return 10.0
        elif budget >= 1000000:  # 1M+ AED
            return 8.0
        elif budget >= 500000:  # 500K+ AED
            return 6.0
        elif budget >= 250000:  # 250K+ AED
            return 4.0
        else:
            return 2.0

    def _calculate_engagement_score(self, interactions: list) -> float:
        """Calculate score based on client engagement history"""
        if not interactions:
            return 5.0

        recent_interactions = len(
            [i for i in interactions if self._is_recent_interaction(i)]
        )
        response_rate = len(
            [i for i in interactions if i.get("client_responded", False)]
        ) / len(interactions)

        base_score = min(recent_interactions * 2, 6)
        engagement_bonus = response_rate * 4

        return min(base_score + engagement_bonus, 10.0)

    def _calculate_timeline_score(self, timeline: str) -> float:
        """Calculate score based on purchase timeline"""
        timeline_lower = timeline.lower()
        if any(term in timeline_lower for term in ["immediate", "asap", "urgent"]):
            return 10.0
        elif any(term in timeline_lower for term in ["1 month", "30 days", "soon"]):
            return 8.0
        elif any(term in timeline_lower for term in ["3 months", "quarter"]):
            return 6.0
        elif any(term in timeline_lower for term in ["6 months", "half year"]):
            return 4.0
        else:
            return 3.0

    def _calculate_location_score(self, preferred_areas: list) -> float:
        """Calculate score based on location preferences"""
        high_value_areas = [
            "palm jumeirah",
            "downtown dubai",
            "emirates hills",
            "jumeirah bay island",
        ]

        if not preferred_areas:
            return 5.0

        matches = sum(
            1
            for area in preferred_areas
            if any(hv in area.lower() for hv in high_value_areas)
        )
        return min(5.0 + (matches * 2.5), 10.0)

    def _determine_qualification_level(self, score: float) -> str:
        """Determine lead qualification level"""
        if score >= 8.0:
            return "hot"
        elif score >= 6.0:
            return "warm"
        elif score >= 4.0:
            return "qualified"
        else:
            return "cold"

    def _get_recommended_actions(self, qualification_level: str) -> list:
        """Get recommended actions based on qualification level"""
        actions = {
            "hot": [
                "Schedule immediate property viewing",
                "Prepare detailed CMA",
                "Connect with mortgage specialist",
                "Send premium property portfolio",
            ],
            "warm": [
                "Send targeted property recommendations",
                "Schedule consultation call",
                "Provide market insights",
                "Add to priority follow-up list",
            ],
            "qualified": [
                "Send introductory materials",
                "Add to regular newsletter",
                "Schedule follow-up in 2 weeks",
                "Provide general market updates",
            ],
            "cold": [
                "Add to long-term nurture campaign",
                "Send monthly market reports",
                "Minimal follow-up required",
            ],
        }
        return actions.get(qualification_level, [])

    def _is_recent_interaction(self, interaction: dict) -> bool:
        """Check if interaction is recent (within last 30 days)"""
        try:
            interaction_date = datetime.fromisoformat(interaction.get("date", ""))
            return (datetime.utcnow() - interaction_date).days <= 30
        except:
            return False

    async def _process_workflow_execution(
        self, task_id: str, request: AITaskRequest
    ) -> Dict[str, Any]:
        """Process workflow execution tasks"""
        await self._update_task_progress(task_id, 10)

        workflow_data = request.input_data
        workflow_type = workflow_data.get("workflow_type", "generic")
        steps = workflow_data.get("steps", [])

        await self._update_task_progress(task_id, 30)

        # Execute workflow steps sequentially
        results = []
        for i, step in enumerate(steps):
            step_result = await self._execute_workflow_step(step)
            results.append(step_result)

            # Update progress based on completed steps
            progress = 30 + (60 * (i + 1) / len(steps)) if steps else 90
            await self._update_task_progress(task_id, int(progress))

        await self._update_task_progress(task_id, 100)

        return {
            "workflow_type": workflow_type,
            "steps_completed": len(results),
            "results": results,
            "status": "completed",
            "execution_time": "estimated_duration",
        }

    async def _execute_workflow_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute individual workflow step"""
        step_type = step.get("type", "generic")
        step_data = step.get("data", {})

        # Simulate step execution based on type
        if step_type == "content_generation":
            return {"step_type": step_type, "result": "Content generated successfully"}
        elif step_type == "data_analysis":
            return {"step_type": step_type, "result": "Analysis completed"}
        elif step_type == "notification":
            return {"step_type": step_type, "result": "Notification sent"}
        else:
            return {"step_type": step_type, "result": "Step completed"}

    async def _process_notification(
        self, task_id: str, request: AITaskRequest
    ) -> Dict[str, Any]:
        """Process notification tasks"""
        await self._update_task_progress(task_id, 25)

        notification_data = request.input_data
        notification_type = notification_data.get("type", "general")
        recipients = notification_data.get("recipients", [])
        message = notification_data.get("message", "")
        channels = notification_data.get("channels", ["email"])

        await self._update_task_progress(task_id, 50)

        # Process notifications by channel
        sent_notifications = []
        for channel in channels:
            for recipient in recipients:
                notification_result = await self._send_notification(
                    channel, recipient, message, notification_type
                )
                sent_notifications.append(notification_result)

        await self._update_task_progress(task_id, 90)

        success_count = sum(1 for n in sent_notifications if n.get("status") == "sent")

        return {
            "notification_type": notification_type,
            "total_recipients": len(recipients),
            "channels_used": channels,
            "notifications_sent": success_count,
            "failed_notifications": len(sent_notifications) - success_count,
            "delivery_details": sent_notifications,
            "status": "completed" if success_count > 0 else "partial_failure",
        }

    async def _send_notification(
        self, channel: str, recipient: str, message: str, notification_type: str
    ) -> Dict[str, Any]:
        """Send individual notification"""
        # Simulate notification sending
        try:
            if channel == "email":
                # Email notification logic here
                return {
                    "recipient": recipient,
                    "channel": channel,
                    "status": "sent",
                    "message_id": f"email_{recipient}_{notification_type}_{datetime.utcnow().timestamp()}",
                    "sent_at": datetime.utcnow().isoformat(),
                }
            elif channel == "sms":
                # SMS notification logic here
                return {
                    "recipient": recipient,
                    "channel": channel,
                    "status": "sent",
                    "message_id": f"sms_{recipient}_{notification_type}_{datetime.utcnow().timestamp()}",
                    "sent_at": datetime.utcnow().isoformat(),
                }
            elif channel == "push":
                # Push notification logic here
                return {
                    "recipient": recipient,
                    "channel": channel,
                    "status": "sent",
                    "message_id": f"push_{recipient}_{notification_type}_{datetime.utcnow().timestamp()}",
                    "sent_at": datetime.utcnow().isoformat(),
                }
            else:
                return {
                    "recipient": recipient,
                    "channel": channel,
                    "status": "failed",
                    "error": f"Unsupported channel: {channel}",
                }
        except Exception as e:
            return {
                "recipient": recipient,
                "channel": channel,
                "status": "failed",
                "error": str(e),
            }

    # Intelligence-specific methods
    async def submit_intelligence_task(
        self,
        user_input: str,
        content_type: ContentType = None,
        user_id: int = None,
        context: Dict[str, Any] = None,
        quality_requirements: Dict[str, Any] = None,
    ) -> str:
        """
        Submit an intelligence content generation task.

        Args:
            user_input: User's content request
            content_type: Type of content to generate
            user_id: ID of requesting user
            context: Additional context data
            quality_requirements: Quality thresholds

        Returns:
            task_id: Unique identifier for tracking
        """
        task_id = str(uuid.uuid4())

        try:
            # Store intelligence task in database
            with self.db_session_factory() as db:
                db.execute(
                    text(
                        """
                    INSERT INTO ai_tasks (id, user_id, task_type, input_data, status, 
                                        priority, progress, retries, max_retries, created_at)
                    VALUES (:task_id, :user_id, :task_type, :input_data, :status, 
                           :priority, :progress, :retries, :max_retries, :created_at)
                """
                    ),
                    {
                        "task_id": task_id,
                        "user_id": user_id,
                        "task_type": "INTELLIGENCE_GENERATION",
                        "input_data": json.dumps(
                            {
                                "user_input": user_input,
                                "content_type": content_type.value
                                if content_type
                                else None,
                                "context": context or {},
                                "quality_requirements": quality_requirements or {},
                            }
                        ),
                        "status": TaskStatus.QUEUED.value,
                        "priority": TaskPriority.NORMAL.value,
                        "progress": 0,
                        "retries": 0,
                        "max_retries": 3,
                        "created_at": datetime.utcnow(),
                    },
                )
                db.commit()

            # Start async intelligence processing
            asyncio.create_task(
                self._process_intelligence_task(
                    task_id, user_input, content_type, context, quality_requirements
                )
            )

            logger.info(f"Intelligence task {task_id} submitted for user {user_id}")
            return task_id

        except Exception as e:
            logger.error(f"Failed to submit intelligence task: {e}")
            raise

    async def _process_intelligence_task(
        self,
        task_id: str,
        user_input: str,
        content_type: ContentType = None,
        context: Dict[str, Any] = None,
        quality_requirements: Dict[str, Any] = None,
    ):
        """Process an intelligence content generation task"""
        try:
            # Update task status to processing and publish progress
            await self._update_task_status_with_stream(
                task_id,
                TaskStatus.PROCESSING,
                0,
                "Initializing intelligence generation...",
            )

            if not ai_content_generator:
                raise ValueError("Intelligence content generator not available")

            # Progress: 10% - Starting generation
            await self._update_task_status_with_stream(
                task_id, TaskStatus.PROCESSING, 10, "Analyzing content requirements..."
            )

            # Auto-detect content type if not provided
            if not content_type:
                content_type = self._detect_content_type_from_input(user_input)

            # Progress: 30% - Content type determined
            await self._update_task_status_with_stream(
                task_id,
                TaskStatus.PROCESSING,
                30,
                f"Generating {content_type.value} content...",
            )

            if content_type == ContentType.PROPERTY_BROCHURE:
                if not PropertyBrochureService:
                    raise ValueError("Property brochure service is not available")
                listing_id = None
                if context:
                    listing_id = (
                        context.get("listing_id")
                        or context.get("listingId")
                        or context.get("target_listing_id")
                    )
                if not listing_id:
                    listing_id = "listing-downtown-dubai-apt"
                with self.db_session_factory() as db:
                    service = PropertyBrochureService(db)
                    service.ensure_listing(listing_id)
                    await self._update_task_status_with_stream(
                        task_id,
                        TaskStatus.PROCESSING,
                        55,
                        "Assembling property insights and marketing brief",
                    )
                    brochure_content = service.generate_brochure(task_id, listing_id)
                await self._update_task_status_with_stream(
                    task_id,
                    TaskStatus.PROCESSING,
                    85,
                    "Formatting brochure layout and visuals",
                )
                await self._store_intelligence_content(brochure_content)
                await self._update_task_completion_with_stream(
                    task_id,
                    TaskStatus.COMPLETED,
                    100,
                    {
                        "content_id": brochure_content.content_id,
                        "content_type": brochure_content.content_type.value,
                        "title": brochure_content.title,
                        "listing_id": listing_id,
                        "structured": brochure_content.generated_content.structured,
                    },
                    "Property brochure ready for review",
                )
                return

            # Generate content using AI
            intelligence_content = await ai_content_generator.generate_content(
                user_input=user_input,
                content_type=content_type,
                context=context,
                quality_requirements=quality_requirements,
            )

            # Progress: 80% - Content generated
            await self._update_task_status_with_stream(
                task_id, TaskStatus.PROCESSING, 80, "Finalizing and storing content..."
            )

            # Store generated content
            await self._store_intelligence_content(intelligence_content)

            # Progress: 100% - Complete
            await self._update_task_completion_with_stream(
                task_id,
                TaskStatus.COMPLETED,
                100,
                {
                    "content_id": intelligence_content.content_id,
                    "content_type": intelligence_content.content_type.value,
                    "title": intelligence_content.title,
                    "quality_score": intelligence_content.quality_scores.overall_score,
                },
                "Content generation completed successfully!",
            )

        except Exception as e:
            logger.error(f"Intelligence task {task_id} failed: {e}")
            await self._update_task_status_with_stream(
                task_id, TaskStatus.FAILED, 0, f"Error: {str(e)}"
            )

    def _detect_content_type_from_input(self, user_input: str) -> ContentType:
        """Auto-detect content type from user input"""
        input_lower = user_input.lower()

        if any(
            term in input_lower
            for term in ["cma", "comparative market", "market analysis", "valuation"]
        ):
            return ContentType.CMA_REPORT
        elif any(
            term in input_lower
            for term in ["social", "post", "instagram", "facebook", "twitter"]
        ):
            return ContentType.SOCIAL_POST
        elif any(
            term in input_lower
            for term in ["pitch", "presentation", "deck", "investor"]
        ):
            return ContentType.PITCH_DECK
        elif any(
            term in input_lower
            for term in ["market report", "market trend", "market overview"]
        ):
            return ContentType.MARKET_REPORT
        else:
            return ContentType.GENERAL

    async def _store_intelligence_content(self, content: IntelligenceContent):
        """Store intelligence content in database"""
        try:
            with self.db_session_factory() as db:
                db.execute(
                    text(
                        """
                    INSERT INTO intelligence_content (
                        content_id, task_id, content_type, title, enhanced,
                        quality_scores, memory_context, generated_content,
                        metadata, export_ready, version, created_at
                    ) VALUES (
                        :content_id, :task_id, :content_type, :title, :enhanced,
                        :quality_scores, :memory_context, :generated_content,
                        :metadata, :export_ready, :version, :created_at
                    )
                """
                    ),
                    {
                        "content_id": content.content_id,
                        "task_id": content.task_id,
                        "content_type": content.content_type.value,
                        "title": content.title,
                        "enhanced": content.enhanced,
                        "quality_scores": json.dumps(content.quality_scores.dict()),
                        "memory_context": json.dumps(content.memory_context.dict()),
                        "generated_content": json.dumps(
                            content.generated_content.dict()
                        ),
                        "metadata": json.dumps(content.metadata.dict()),
                        "export_ready": content.export_ready,
                        "version": content.version,
                        "created_at": datetime.utcnow(),
                    },
                )
                db.commit()

        except Exception as e:
            logger.error(f"Failed to store intelligence content: {e}")
            raise

    # SSE Streaming methods
    async def subscribe_to_task_progress(
        self, task_id: str
    ) -> AsyncGenerator[StreamProgressEvent, None]:
        """Subscribe to task progress updates via SSE"""
        queue = asyncio.Queue()

        with self.stream_lock:
            if task_id not in self.progress_streams:
                self.progress_streams[task_id] = []
            self.progress_streams[task_id].append(queue)

        try:
            while True:
                try:
                    # Wait for progress update or timeout
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield event

                    # If task is completed or failed, break
                    if event.status in [
                        IntelligenceTaskStatus.COMPLETED,
                        IntelligenceTaskStatus.FAILED,
                    ]:
                        break

                except asyncio.TimeoutError:
                    # Send keepalive event
                    yield StreamProgressEvent(
                        event="keepalive",
                        task_id=task_id,
                        status=IntelligenceTaskStatus.PROCESSING,
                        progress=0,
                        current_step="Keepalive ping",
                    )

        finally:
            # Cleanup: remove queue from streams
            with self.stream_lock:
                if task_id in self.progress_streams:
                    try:
                        self.progress_streams[task_id].remove(queue)
                        if not self.progress_streams[task_id]:
                            del self.progress_streams[task_id]
                    except ValueError:
                        pass

    async def _publish_progress_event(self, task_id: str, event: StreamProgressEvent):
        """Publish progress event to all subscribers"""
        with self.stream_lock:
            if task_id in self.progress_streams:
                for queue in self.progress_streams[task_id]:
                    try:
                        queue.put_nowait(event)
                    except asyncio.QueueFull:
                        logger.warning(f"Progress queue full for task {task_id}")

    async def _update_task_status_with_stream(
        self, task_id: str, status: TaskStatus, progress: int, current_step: str = None
    ):
        """Update task status and publish to streams"""
        # Update database
        await self._update_task_status(task_id, status, progress)

        # Publish to streams
        if StreamProgressEvent and IntelligenceTaskStatus:
            event = StreamProgressEvent(
                task_id=task_id,
                status=IntelligenceTaskStatus(status.value),
                progress=progress,
                current_step=current_step,
            )
            await self._publish_progress_event(task_id, event)

    async def _update_task_completion_with_stream(
        self,
        task_id: str,
        status: TaskStatus,
        progress: int,
        output_data: Dict[str, Any],
        current_step: str = None,
    ):
        """Update task completion and publish to streams"""
        # Update database
        await self._update_task_completion(task_id, status, progress, output_data)

        # Publish to streams
        if StreamProgressEvent and IntelligenceTaskStatus:
            event = StreamProgressEvent(
                task_id=task_id,
                status=IntelligenceTaskStatus(status.value),
                progress=progress,
                current_step=current_step,
                data=output_data,
            )
            await self._publish_progress_event(task_id, event)

    # Helper methods for database operations
    async def _update_task_status(
        self, task_id: str, status: TaskStatus, progress: int
    ):
        """Update task status and progress"""
        with self.db_session_factory() as db:
            db.execute(
                text(
                    """
                UPDATE ai_tasks 
                SET status = :status, progress = :progress,
                    started_at = CASE WHEN :status = 'processing' AND started_at IS NULL 
                                     THEN :now ELSE started_at END
                WHERE id = :task_id
            """
                ),
                {
                    "task_id": task_id,
                    "status": status.value,
                    "progress": progress,
                    "now": datetime.utcnow(),
                },
            )
            db.commit()

    async def _update_task_completion(
        self,
        task_id: str,
        status: TaskStatus,
        progress: int,
        output_data: Dict[str, Any],
    ):
        """Update task completion with results"""
        with self.db_session_factory() as db:
            db.execute(
                text(
                    """
                UPDATE ai_tasks 
                SET status = :status, progress = :progress, output_data = :output_data,
                    completed_at = :completed_at
                WHERE id = :task_id
            """
                ),
                {
                    "task_id": task_id,
                    "status": status.value,
                    "progress": progress,
                    "output_data": json.dumps(output_data),
                    "completed_at": datetime.utcnow(),
                },
            )
            db.commit()

    async def _handle_task_failure(
        self, task_id: str, request: AITaskRequest, error_message: str
    ):
        """Handle task failure with retry logic"""
        with self.db_session_factory() as db:
            # Get current retry count
            result = db.execute(
                text("SELECT retries, max_retries FROM ai_tasks WHERE id = :task_id"),
                {"task_id": task_id},
            )
            row = result.fetchone()

            if row and row.retries < row.max_retries:
                # Retry the task
                db.execute(
                    text(
                        """
                    UPDATE ai_tasks 
                    SET status = :status, retries = retries + 1, error_message = :error_message
                    WHERE id = :task_id
                """
                    ),
                    {
                        "task_id": task_id,
                        "status": TaskStatus.RETRYING.value,
                        "error_message": error_message,
                    },
                )
                db.commit()

                # Schedule retry after delay
                await asyncio.sleep(min(2**row.retries, 30))  # Exponential backoff
                asyncio.create_task(self._process_task(task_id, request))
            else:
                # Mark as permanently failed
                db.execute(
                    text(
                        """
                    UPDATE ai_tasks 
                    SET status = :status, error_message = :error_message, completed_at = :completed_at
                    WHERE id = :task_id
                """
                    ),
                    {
                        "task_id": task_id,
                        "status": TaskStatus.FAILED.value,
                        "error_message": error_message,
                        "completed_at": datetime.utcnow(),
                    },
                )
                db.commit()

    # Placeholder implementations for AI processing
    # These will integrate with your existing AI routers

    async def _generate_marketing_campaign(
        self, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate marketing campaign content"""
        # This would integrate with your existing AI assistant router
        return {
            "campaign_type": "just_listed",
            "content": {
                "headline": "Luxury Apartment in Dubai Marina",
                "description": "Stunning 2BR with marina views...",
                "call_to_action": "Schedule your viewing today!",
            },
        }

    async def _generate_cma_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CMA analysis"""
        # This would integrate with your ML insights router
        return {
            "comparable_properties": [],
            "price_recommendations": {
                "aggressive": 2500000,
                "standard": 2300000,
                "conservative": 2100000,
            },
            "market_conditions": "strong",
        }

    async def _generate_listing_strategy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate listing strategy"""
        return {
            "target_audience": "Luxury investors and families",
            "key_selling_points": [
                "Marina views",
                "Premium finishes",
                "Prime location",
            ],
            "timeline": "4-week marketing campaign",
        }

    async def _generate_social_media_content(
        self, data: Dict[str, Any], platform: str
    ) -> Dict[str, Any]:
        """Generate social media content"""
        return {
            "caption": "✨ JUST LISTED ✨ Luxury apartment in Dubai Marina...",
            "hashtags": ["#DubaiRealEstate", "#LuxuryLiving", "#PropertyPro"],
        }
