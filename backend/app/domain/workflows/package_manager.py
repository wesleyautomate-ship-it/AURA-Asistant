"""
AURA Workflow Package Manager
===============================

Manages and executes multi-step AURA workflow packages that orchestrate
complex real estate processes across marketing, analytics, and social media.

This is the orchestration layer that ties together the individual AURA routers
into comprehensive workflow packages that agents can execute with one click.

Workflow Packages:
- New Listing Package: Complete marketing launch for new properties
- Lead Nurturing Package: Multi-touch lead conversion workflow
- Client Onboarding Package: Comprehensive client setup and communication
- Market Analysis Package: Deep dive property and area analysis
- Social Campaign Package: Multi-platform social media campaigns
"""

import logging
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from app.domain.ai.task_orchestrator import AITaskOrchestrator, TaskType, TaskPriority

logger = logging.getLogger(__name__)


class PackageStatus(Enum):
    """Workflow package execution statuses"""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Individual step statuses"""

    WAITING = "waiting"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Individual step in a workflow package"""

    step_id: str
    step_name: str
    step_type: str  # task_type from TaskType enum
    step_data: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    optional: bool = False
    timeout_minutes: int = 30
    retry_count: int = 3
    status: StepStatus = StepStatus.WAITING
    task_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowPackage:
    """Complete workflow package definition"""

    package_id: str
    package_name: str
    description: str
    category: str  # 'listing', 'lead_nurturing', 'client_onboarding', etc.
    steps: List[WorkflowStep] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    status: PackageStatus = PackageStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration_minutes: int = 60
    user_id: Optional[int] = None


class WorkflowPackageManager:
    """
    Manages execution of AURA workflow packages

    This class orchestrates complex multi-step workflows by:
    1. Loading predefined package templates
    2. Managing step dependencies and execution order
    3. Coordinating with AI task orchestrator
    4. Handling errors and retries
    5. Providing progress tracking
    6. Supporting pause/resume functionality
    """

    def __init__(self, get_db: Callable, orchestrator: AITaskOrchestrator):
        self.get_db = get_db
        self.orchestrator = orchestrator
        self.active_packages: Dict[str, WorkflowPackage] = {}

        # Load predefined package templates
        self._load_package_templates()

    def _load_package_templates(self):
        """Load predefined AURA workflow package templates"""

        # New Listing Package - Complete marketing launch
        self.new_listing_package = WorkflowPackage(
            package_id="new_listing_v1",
            package_name="New Listing Package",
            description="Complete marketing launch for new property listings",
            category="listing",
            estimated_duration_minutes=45,
            steps=[
                WorkflowStep(
                    step_id="property_analysis",
                    step_name="Property Analysis",
                    step_type="property_analysis",
                    step_data={
                        "include_market_context": True,
                        "generate_highlights": True,
                    },
                ),
                WorkflowStep(
                    step_id="cma_report",
                    step_name="CMA Report Generation",
                    step_type="cma_analysis",
                    step_data={
                        "analysis_type": "listing",
                        "include_market_trends": True,
                    },
                    dependencies=["property_analysis"],
                ),
                WorkflowStep(
                    step_id="marketing_content",
                    step_name="Marketing Content Creation",
                    step_type="marketing_content",
                    step_data={
                        "content_types": ["description", "features", "highlights"]
                    },
                    dependencies=["property_analysis"],
                ),
                WorkflowStep(
                    step_id="marketing_campaigns",
                    step_name="Marketing Campaign Creation",
                    step_type="marketing_campaign",
                    step_data={
                        "campaign_types": ["postcard", "email_blast", "social_campaign"]
                    },
                    dependencies=["marketing_content", "cma_report"],
                ),
                WorkflowStep(
                    step_id="social_media_posts",
                    step_name="Social Media Content",
                    step_type="social_media_post",
                    step_data={
                        "platforms": ["instagram", "facebook", "linkedin"],
                        "content_type": "listing",
                    },
                    dependencies=["marketing_content"],
                ),
                WorkflowStep(
                    step_id="listing_optimization",
                    step_name="Listing Optimization",
                    step_type="listing_optimization",
                    step_data={"seo_optimization": True, "portal_optimization": True},
                    dependencies=["marketing_content"],
                ),
            ],
        )

        # Lead Nurturing Package - Multi-touch conversion workflow
        self.lead_nurturing_package = WorkflowPackage(
            package_id="lead_nurturing_v1",
            package_name="Lead Nurturing Package",
            description="Multi-touch lead conversion and follow-up workflow",
            category="lead_nurturing",
            estimated_duration_minutes=30,
            steps=[
                WorkflowStep(
                    step_id="lead_scoring",
                    step_name="Lead Scoring & Qualification",
                    step_type="lead_analysis",
                    step_data={
                        "scoring_model": "dubai_residential",
                        "qualification_criteria": "standard",
                    },
                ),
                WorkflowStep(
                    step_id="market_insights",
                    step_name="Personalized Market Insights",
                    step_type="market_analysis",
                    step_data={"personalization": True, "lead_preferences": True},
                    dependencies=["lead_scoring"],
                ),
                WorkflowStep(
                    step_id="property_recommendations",
                    step_name="Property Recommendations",
                    step_type="property_matching",
                    step_data={"recommendation_count": 5, "include_alternatives": True},
                    dependencies=["lead_scoring", "market_insights"],
                ),
                WorkflowStep(
                    step_id="follow_up_sequence",
                    step_name="Automated Follow-up Sequence",
                    step_type="communication_sequence",
                    step_data={"sequence_type": "lead_nurturing", "duration_days": 14},
                    dependencies=["property_recommendations"],
                ),
                WorkflowStep(
                    step_id="social_proof",
                    step_name="Social Proof Content",
                    step_type="social_media_post",
                    step_data={
                        "platforms": ["instagram", "linkedin"],
                        "content_type": "success_story",
                    },
                    optional=True,
                    dependencies=["follow_up_sequence"],
                ),
            ],
        )

        # Client Onboarding Package - Comprehensive client setup
        self.client_onboarding_package = WorkflowPackage(
            package_id="client_onboarding_v1",
            package_name="Client Onboarding Package",
            description="Comprehensive new client setup and communication workflow",
            category="client_onboarding",
            estimated_duration_minutes=20,
            steps=[
                WorkflowStep(
                    step_id="welcome_sequence",
                    step_name="Welcome Communication Sequence",
                    step_type="communication_sequence",
                    step_data={"sequence_type": "onboarding", "personalization": True},
                ),
                WorkflowStep(
                    step_id="market_briefing",
                    step_name="Market Briefing Report",
                    step_type="market_analysis",
                    step_data={"report_type": "client_briefing", "area_focus": True},
                    dependencies=["welcome_sequence"],
                ),
                WorkflowStep(
                    step_id="service_overview",
                    step_name="Service Overview Presentation",
                    step_type="presentation_generation",
                    step_data={
                        "presentation_type": "service_overview",
                        "client_specific": True,
                    },
                    dependencies=["welcome_sequence"],
                ),
                WorkflowStep(
                    step_id="communication_setup",
                    step_name="Communication Preferences Setup",
                    step_type="communication_setup",
                    step_data={
                        "channels": ["email", "sms", "whatsapp"],
                        "frequency_preferences": True,
                    },
                    dependencies=["service_overview"],
                ),
                WorkflowStep(
                    step_id="portal_access",
                    step_name="Client Portal Access Setup",
                    step_type="portal_setup",
                    step_data={
                        "portal_type": "client_dashboard",
                        "permissions": "standard",
                    },
                    dependencies=["communication_setup"],
                    optional=True,
                ),
            ],
        )

    async def execute_package(
        self, package_template: str, variables: Dict[str, Any], user_id: int
    ) -> str:
        """
        Execute a workflow package with provided variables

        Args:
            package_template: Package template ID ('new_listing', 'lead_nurturing', 'client_onboarding')
            variables: Package-specific variables (property_id, lead_id, client_id, etc.)
            user_id: User executing the package

        Returns:
            Package execution ID for tracking
        """
        try:
            # Get package template
            template = self._get_package_template(package_template)
            if not template:
                raise ValueError(f"Unknown package template: {package_template}")

            # Create package instance
            execution_id = (
                f"{package_template}_{user_id}_{int(datetime.utcnow().timestamp())}"
            )
            package = WorkflowPackage(
                package_id=execution_id,
                package_name=template.package_name,
                description=template.description,
                category=template.category,
                steps=[self._prepare_step(step, variables) for step in template.steps],
                variables=variables,
                estimated_duration_minutes=template.estimated_duration_minutes,
                user_id=user_id,
            )

            # Store active package
            self.active_packages[execution_id] = package

            # Start package execution
            await self._start_package_execution(execution_id)

            logger.info(f"Started workflow package {execution_id} for user {user_id}")

            return execution_id

        except Exception as e:
            logger.error(f"Failed to execute package {package_template}: {e}")
            raise

    def _get_package_template(self, template_id: str) -> Optional[WorkflowPackage]:
        """Get package template by ID"""
        templates = {
            "new_listing": self.new_listing_package,
            "lead_nurturing": self.lead_nurturing_package,
            "client_onboarding": self.client_onboarding_package,
        }
        return templates.get(template_id)

    def _prepare_step(
        self, step: WorkflowStep, variables: Dict[str, Any]
    ) -> WorkflowStep:
        """Prepare step with package variables"""
        prepared_step = WorkflowStep(
            step_id=step.step_id,
            step_name=step.step_name,
            step_type=step.step_type,
            step_data={**step.step_data, **variables},
            dependencies=step.dependencies[:],
            optional=step.optional,
            timeout_minutes=step.timeout_minutes,
            retry_count=step.retry_count,
        )
        return prepared_step

    async def _start_package_execution(self, execution_id: str):
        """Start executing a workflow package"""
        package = self.active_packages[execution_id]
        package.status = PackageStatus.RUNNING
        package.started_at = datetime.utcnow()

        # Execute ready steps
        await self._execute_ready_steps(execution_id)

    async def _execute_ready_steps(self, execution_id: str):
        """Execute all steps that are ready (dependencies satisfied)"""
        package = self.active_packages[execution_id]

        ready_steps = self._get_ready_steps(package)

        for step in ready_steps:
            try:
                await self._execute_step(execution_id, step)
            except Exception as e:
                logger.error(f"Failed to execute step {step.step_id}: {e}")
                step.status = StepStatus.FAILED
                step.error_message = str(e)

                # If step is not optional, fail the package
                if not step.optional:
                    package.status = PackageStatus.FAILED
                    return

    def _get_ready_steps(self, package: WorkflowPackage) -> List[WorkflowStep]:
        """Get steps that are ready to execute"""
        ready_steps = []

        for step in package.steps:
            if step.status != StepStatus.WAITING:
                continue

            # Check if all dependencies are completed
            dependencies_satisfied = True
            for dep_id in step.dependencies:
                dep_step = next((s for s in package.steps if s.step_id == dep_id), None)
                if not dep_step or dep_step.status != StepStatus.COMPLETED:
                    dependencies_satisfied = False
                    break

            if dependencies_satisfied:
                step.status = StepStatus.READY
                ready_steps.append(step)

        return ready_steps

    async def _execute_step(self, execution_id: str, step: WorkflowStep):
        """Execute an individual workflow step"""
        try:
            step.status = StepStatus.RUNNING
            step.started_at = datetime.utcnow()

            # Submit task to AI orchestrator
            task_id = await self.orchestrator.submit_task(
                task_type=step.step_type,
                task_data=step.step_data,
                user_id=self.active_packages[execution_id].user_id,
                priority=TaskPriority.MEDIUM,
            )

            step.task_id = task_id

            # Monitor task completion (this would be handled by a background process)
            # For now, we mark it as running and let the monitoring system handle completion

            logger.info(
                f"Submitted task {task_id} for step {step.step_id} in package {execution_id}"
            )

        except Exception as e:
            step.status = StepStatus.FAILED
            step.error_message = str(e)
            raise

    async def handle_step_completion(self, task_id: str, result: Dict[str, Any]):
        """Handle completion of a step task"""
        # Find the step by task_id
        execution_id = None
        step = None

        for exec_id, package in self.active_packages.items():
            for pkg_step in package.steps:
                if pkg_step.task_id == task_id:
                    execution_id = exec_id
                    step = pkg_step
                    break
            if step:
                break

        if not step or not execution_id:
            logger.warning(f"Could not find step for completed task {task_id}")
            return

        # Update step status
        step.status = StepStatus.COMPLETED
        step.completed_at = datetime.utcnow()
        step.result = result

        logger.info(f"Step {step.step_id} completed in package {execution_id}")

        # Check if more steps can be executed
        await self._execute_ready_steps(execution_id)

        # Check if package is complete
        await self._check_package_completion(execution_id)

    async def handle_step_failure(self, task_id: str, error: str):
        """Handle failure of a step task"""
        # Find the step by task_id
        execution_id = None
        step = None

        for exec_id, package in self.active_packages.items():
            for pkg_step in package.steps:
                if pkg_step.task_id == task_id:
                    execution_id = exec_id
                    step = pkg_step
                    break
            if step:
                break

        if not step or not execution_id:
            logger.warning(f"Could not find step for failed task {task_id}")
            return

        # Update step status
        step.status = StepStatus.FAILED
        step.error_message = error
        step.completed_at = datetime.utcnow()

        # Handle retry logic
        if step.retry_count > 0:
            step.retry_count -= 1
            step.status = StepStatus.READY
            logger.info(f"Retrying step {step.step_id} in package {execution_id}")
            await self._execute_step(execution_id, step)
        else:
            # If step is not optional, fail the package
            if not step.optional:
                package = self.active_packages[execution_id]
                package.status = PackageStatus.FAILED
                logger.error(
                    f"Package {execution_id} failed due to step {step.step_id}"
                )
            else:
                # Skip optional failed step and continue
                step.status = StepStatus.SKIPPED
                await self._execute_ready_steps(execution_id)
                await self._check_package_completion(execution_id)

    async def _check_package_completion(self, execution_id: str):
        """Check if package execution is complete"""
        package = self.active_packages[execution_id]

        # Check if all non-optional steps are completed or skipped
        incomplete_required_steps = [
            step
            for step in package.steps
            if not step.optional
            and step.status not in [StepStatus.COMPLETED, StepStatus.SKIPPED]
        ]

        if not incomplete_required_steps:
            package.status = PackageStatus.COMPLETED
            package.completed_at = datetime.utcnow()

            logger.info(f"Package {execution_id} completed successfully")

            # Notify user of completion
            await self._notify_package_completion(execution_id)

    async def _notify_package_completion(self, execution_id: str):
        """Notify user of package completion"""
        package = self.active_packages[execution_id]

        # Generate completion summary
        completed_steps = len(
            [s for s in package.steps if s.status == StepStatus.COMPLETED]
        )
        total_steps = len([s for s in package.steps if not s.optional])

        logger.info(
            f"Package {package.package_name} completed: {completed_steps}/{total_steps} steps"
        )

        # TODO: Send notification to user (email, in-app notification, etc.)

    def get_package_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow package"""
        if execution_id not in self.active_packages:
            return None

        package = self.active_packages[execution_id]

        return {
            "execution_id": execution_id,
            "package_name": package.package_name,
            "status": package.status.value,
            "progress": self._calculate_progress(package),
            "steps": [
                {
                    "step_id": step.step_id,
                    "step_name": step.step_name,
                    "status": step.status.value,
                    "started_at": step.started_at.isoformat()
                    if step.started_at
                    else None,
                    "completed_at": step.completed_at.isoformat()
                    if step.completed_at
                    else None,
                    "error_message": step.error_message,
                }
                for step in package.steps
            ],
            "started_at": package.started_at.isoformat()
            if package.started_at
            else None,
            "completed_at": package.completed_at.isoformat()
            if package.completed_at
            else None,
            "estimated_completion": self._calculate_estimated_completion(package),
        }

    def _calculate_progress(self, package: WorkflowPackage) -> float:
        """Calculate package completion progress (0-100)"""
        if not package.steps:
            return 0.0

        completed_steps = len(
            [
                s
                for s in package.steps
                if s.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]
            ]
        )
        total_steps = len(package.steps)

        return (completed_steps / total_steps) * 100

    def _calculate_estimated_completion(
        self, package: WorkflowPackage
    ) -> Optional[str]:
        """Calculate estimated completion time"""
        if package.status in [
            PackageStatus.COMPLETED,
            PackageStatus.FAILED,
            PackageStatus.CANCELLED,
        ]:
            return None

        if not package.started_at:
            return None

        # Simple estimation based on completed steps and original estimate
        progress = self._calculate_progress(package)
        if progress == 0:
            return None

        elapsed_minutes = (datetime.utcnow() - package.started_at).total_seconds() / 60
        estimated_total_minutes = (elapsed_minutes / progress) * 100
        estimated_completion = package.started_at + timedelta(
            minutes=estimated_total_minutes
        )

        return estimated_completion.isoformat()

    def list_available_packages(self) -> List[Dict[str, Any]]:
        """List all available workflow packages"""
        return [
            {
                "package_id": "new_listing",
                "package_name": self.new_listing_package.package_name,
                "description": self.new_listing_package.description,
                "category": self.new_listing_package.category,
                "estimated_duration_minutes": self.new_listing_package.estimated_duration_minutes,
                "required_variables": ["property_id"],
                "optional_variables": ["custom_message", "target_audience"],
            },
            {
                "package_id": "lead_nurturing",
                "package_name": self.lead_nurturing_package.package_name,
                "description": self.lead_nurturing_package.description,
                "category": self.lead_nurturing_package.category,
                "estimated_duration_minutes": self.lead_nurturing_package.estimated_duration_minutes,
                "required_variables": ["lead_id"],
                "optional_variables": ["nurturing_sequence", "personalization_level"],
            },
            {
                "package_id": "client_onboarding",
                "package_name": self.client_onboarding_package.package_name,
                "description": self.client_onboarding_package.description,
                "category": self.client_onboarding_package.category,
                "estimated_duration_minutes": self.client_onboarding_package.estimated_duration_minutes,
                "required_variables": ["client_id"],
                "optional_variables": ["service_level", "communication_preferences"],
            },
        ]

    async def pause_package(self, execution_id: str) -> bool:
        """Pause a running workflow package"""
        if execution_id not in self.active_packages:
            return False

        package = self.active_packages[execution_id]
        if package.status == PackageStatus.RUNNING:
            package.status = PackageStatus.PAUSED
            logger.info(f"Paused package {execution_id}")
            return True

        return False

    async def resume_package(self, execution_id: str) -> bool:
        """Resume a paused workflow package"""
        if execution_id not in self.active_packages:
            return False

        package = self.active_packages[execution_id]
        if package.status == PackageStatus.PAUSED:
            package.status = PackageStatus.RUNNING
            await self._execute_ready_steps(execution_id)
            logger.info(f"Resumed package {execution_id}")
            return True

        return False

    async def cancel_package(self, execution_id: str) -> bool:
        """Cancel a workflow package"""
        if execution_id not in self.active_packages:
            return False

        package = self.active_packages[execution_id]
        package.status = PackageStatus.CANCELLED
        package.completed_at = datetime.utcnow()

        # Cancel any running tasks
        for step in package.steps:
            if step.status == StepStatus.RUNNING and step.task_id:
                # TODO: Cancel task in orchestrator
                pass

        logger.info(f"Cancelled package {execution_id}")
        return True
