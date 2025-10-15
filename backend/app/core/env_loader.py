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
    if os.getenv("ENVIRONMENT") == "docker":
        print("[OK] Running in Docker environment - using environment variables")
        return

    # Get the backend directory (2 levels up from this file)
    backend_dir = Path(__file__).parent.parent.parent

    # Try multiple .env file locations in priority order:
    env_files = [
        backend_dir / ".env.development",  # Backend development config
        backend_dir / ".env",  # Backend general config
        backend_dir.parent / ".env",  # Project root config
    ]

    loaded = False
    for env_file in env_files:
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            print(f"[OK] Loaded environment from: {env_file}")
            loaded = True
            break

    if not loaded:
        print(
            f"[WARN] No .env file found in any of these locations: {[str(f) for f in env_files]}"
        )
        # Fallback to current directory
        load_dotenv()


# Load environment when module is imported
load_env()
