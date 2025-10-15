#!/usr/bin/env python3
"""
Safe Backend Startup Script
============================

This script ensures the backend always starts with the correct Python environment:
- Validates that .venv is being used
- Checks for required dependencies
- Starts the backend with proper Python interpreter
"""

import sys
import os
import subprocess
from pathlib import Path

# Get project root (parent of scripts directory)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
VENV_PATH = PROJECT_ROOT / ".venv"
BACKEND_DIR = PROJECT_ROOT / "backend"


def check_environment():
    """Check if we're running in the correct virtual environment"""
    print("\n" + "=" * 60)
    print("Backend Environment Validation")
    print("=" * 60 + "\n")

    # Check if .venv exists
    if not VENV_PATH.exists():
        print(f"[ERROR] Virtual environment not found at: {VENV_PATH}")
        print("\n[FIX] Create virtual environment:")
        print(f"  python -m venv {VENV_PATH}")
        print(f"  {VENV_PATH / 'Scripts' / 'pip.exe'} install -r requirements.txt")
        sys.exit(1)

    print(f"[OK] Virtual environment found: {VENV_PATH}")

    # Check if we're using the venv Python
    current_python = Path(sys.executable)
    venv_python = VENV_PATH / "Scripts" / "python.exe"

    if not current_python.resolve() == venv_python.resolve():
        print(f"\n[WARN] Not using virtual environment Python!")
        print(f"  Current: {current_python}")
        print(f"  Expected: {venv_python}")
        print("\n[FIX] Restarting with correct Python interpreter...")

        # Restart with correct Python
        cmd = [str(venv_python), __file__]
        os.execv(str(venv_python), cmd)

    print(f"[OK] Using correct Python: {current_python}")

    # Check Python version
    py_version = sys.version_info
    print(f"[OK] Python version: {py_version.major}.{py_version.minor}.{py_version.micro}")

    # Check critical dependencies
    print("\n[INFO] Checking dependencies...")
    critical_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
    ]

    missing = []
    for package in critical_packages:
        try:
            __import__(package)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [MISSING] {package}")
            missing.append(package)

    if missing:
        print(f"\n[ERROR] Missing dependencies: {', '.join(missing)}")
        print("\n[FIX] Install dependencies:")
        print(f"  {venv_python} -m pip install -r requirements.txt")
        sys.exit(1)

    print("\n[OK] All critical dependencies installed")

    # Check .env file
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        print(f"\n[WARN] .env file not found: {env_file}")
        print("  Backend will use default/mock configuration")
    else:
        print(f"[OK] Environment config found: {env_file}")

    print("\n" + "=" * 60)
    print("[SUCCESS] Environment validation passed!")
    print("=" * 60 + "\n")


def start_backend():
    """Start the backend server"""
    print("[INFO] Starting backend server...")
    print(f"[INFO] Backend directory: {BACKEND_DIR}")

    # Get the Python executable from current environment
    python_exe = sys.executable

    # Start uvicorn
    cmd = [
        python_exe,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
    ]

    print(f"[CMD] {' '.join(cmd)}")
    print("\n" + "=" * 60)
    print("Backend server starting on http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    # Change to backend directory and start
    os.chdir(BACKEND_DIR)
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n[INFO] Backend server stopped")
    except Exception as e:
        print(f"\n[ERROR] Failed to start backend: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_environment()
    start_backend()
