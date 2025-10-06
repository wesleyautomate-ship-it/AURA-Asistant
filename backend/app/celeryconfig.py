"""
Celery Configuration for Dubai Real Estate RAG System

This module configures Celery for asynchronous task processing, including:
- AI command execution
- Report generation
- ML model training
- Background data processing
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Celery Configuration
broker_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
result_backend = os.getenv('REDIS_URL', 'redis://redis:6379/0')

# Task Configuration
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Task Routing
task_routes = {
    'tasks.ai_commands.*': {'queue': 'ai_commands'},
    'tasks.reports.*': {'queue': 'reports'},
    'tasks.ml_training.*': {'queue': 'ml_training'},
    'tasks.data_processing.*': {'queue': 'data_processing'},
}

# Queue Configuration
task_default_queue = 'default'
task_queues = {
    'default': {},
    'ai_commands': {
        'exchange': 'ai_commands',
        'routing_key': 'ai_commands',
    },
    'reports': {
        'exchange': 'reports',
        'routing_key': 'reports',
    },
    'ml_training': {
        'exchange': 'ml_training',
        'routing_key': 'ml_training',
    },
    'data_processing': {
        'exchange': 'data_processing',
        'routing_key': 'data_processing',
    },
}

# Worker Configuration
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_disable_rate_limits = False

# Task Execution
task_always_eager = False  # Set to True for testing without Celery
task_eager_propagates = True
task_ignore_result = False

# Result Configuration
result_expires = 3600  # 1 hour
result_persistent = True

# Monitoring
worker_send_task_events = True
task_send_sent_event = True

# Error Handling
task_acks_late = True
worker_prefetch_multiplier = 1

# Logging
worker_log_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
worker_task_log_format = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
