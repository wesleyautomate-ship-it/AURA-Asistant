#!/usr/bin/env python3
"""
Centralized environment variable loader
Ensures all modules use the root .env file or Docker environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    """Load environment variables from root .env file or use Docker environment"""
    # Check if we're running in Docker
    if os.getenv('ENVIRONMENT') == 'docker':
        print("✅ Running in Docker environment - using environment variables")
        return
    
    # Get the project root directory (2 levels up from backend)
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)

    else:
        print(f"⚠️ .env file not found at: {env_file}")
        # Fallback to current directory
        load_dotenv()

# Load environment when module is imported
load_env()