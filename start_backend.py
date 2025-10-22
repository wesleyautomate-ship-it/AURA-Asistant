#!/usr/bin/env python3
"""
Simple backend startup script to handle import path issues
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == '__main__':
    try:
        import uvicorn
        from multiprocessing import freeze_support
        freeze_support()
        
        print("Starting backend server...")
        uvicorn.run(
            "backend.app.main:app",
            host="127.0.0.1", 
            port=8000,
            reload=False,  # Disable reload to avoid multiprocessing issues
        )
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install missing dependencies with: pip install fastapi uvicorn sqlalchemy")
    except Exception as e:
        print(f"Error starting backend: {e}")
        print("Make sure you're in the correct directory and all dependencies are installed.")
