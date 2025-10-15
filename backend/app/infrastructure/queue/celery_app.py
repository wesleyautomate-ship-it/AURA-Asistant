"""
Celery Application for Dubai Real Estate RAG System

This module initializes the Celery application and imports all task modules.
"""

from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_celery_app():
    """Create and configure Celery application"""

    # Create Celery app
    app = Celery("rag_system")

    # Load configuration
    app.config_from_object("celeryconfig")

    # Auto-discover tasks
    app.autodiscover_tasks(
        [
            "tasks.ai_commands",
            "tasks.reports",
            "tasks.ml_training",
            "tasks.data_processing",
        ]
    )

    return app


# Create the Celery app instance
celery_app = create_celery_app()

# Import tasks to ensure they're registered
try:
    from tasks.ai_commands import *
    from tasks.reports import *
    from tasks.ml_training import *
    from tasks.data_processing import *

    print("✅ All Celery tasks imported successfully")
except ImportError as e:
    print(f"⚠️ Some Celery tasks could not be imported: {e}")

if __name__ == "__main__":
    celery_app.start()
