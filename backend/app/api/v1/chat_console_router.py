"""
Chat Console Router (shim)
Registers the chat endpoint explicitly under /api/v1/intelligence/chat
to avoid any prefix inconsistencies.
"""

from fastapi import APIRouter

# Reuse the existing chat endpoint from intelligence_router
from app.api.v1.intelligence_router import chat_endpoint

router = APIRouter(prefix="/intelligence", tags=["Intelligence Pipeline"])

# POST /api/v1/intelligence/chat
router.add_api_route("/chat", chat_endpoint, methods=["POST"], include_in_schema=False)
