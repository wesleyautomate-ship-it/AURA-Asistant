#!/usr/bin/env python3
"""
Simple backend runner for PropertyPro AI
Skips problematic imports and starts with minimal configuration
"""

import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PropertyPro AI Backend",
    description="Real Estate Assistant API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "PropertyPro AI Backend is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "PropertyPro AI Backend"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting PropertyPro AI Backend on http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)