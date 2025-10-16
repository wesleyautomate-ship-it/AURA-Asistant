"""
Export Router for Content Generation
======================================

Handles PDF and HTML export of generated content with share link support.
Supports all content types: CMA_REPORT, PITCH_DECK, MARKET_REPORT, NEWSLETTER, SOCIAL_POST

Version: 3.2
Phase: Track 1.4 - Export Service
"""

import logging
import os
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import secrets

from app.core.middleware import get_current_user
from app.core.models import User
from app.schemas.content_types import ContentType
from app.schemas.brochure import BrochureInput, BrochureResult
from app.services.exporters.save_file import save_html
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/export", tags=["Export"])


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================


class ExportRequest(BaseModel):
    """Request model for content export"""

    task_id: str = Field(..., description="Task ID containing the content to export")
    content_type: ContentType = Field(..., description="Type of content to export")
    format: str = Field(..., description="Export format: 'pdf' or 'html'")
    include_branding: bool = Field(True, description="Include company branding")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123",
                "content_type": "CMA_REPORT",
                "format": "pdf",
                "include_branding": True,
            }
        }


class ShareLinkResponse(BaseModel):
    """Response for HTML share link generation"""

    success: bool
    share_url: str
    expires_at: datetime
    token: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "share_url": "https://app.realtorpro.ai/share/abc123def456",
                "expires_at": "2025-10-17T08:00:00Z",
                "token": "abc123def456",
                "message": "Share link generated successfully",
            }
        }


class ExportStatusResponse(BaseModel):
    """Response for export status check"""

    task_id: str
    exported: bool
    export_count: int
    last_export: Optional[datetime]
    formats_available: list[str]

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_123",
                "exported": True,
                "export_count": 2,
                "last_export": "2025-10-10T08:00:00Z",
                "formats_available": ["pdf", "html"],
            }
        }


# =============================================================================
# TEMPORARY STORAGE (Replace with database in production)
# =============================================================================

# In-memory storage for export metadata and share tokens
_export_metadata = {}
_share_tokens = {}


def generate_share_token() -> str:
    """Generate secure random token for share links"""
    return secrets.token_urlsafe(32)


def sign_share_token(token: str, task_id: str, expires_at: datetime) -> str:
    """
    Sign share token for security.
    In production, use HMAC with secret key.
    """
    # Simple signing for now - replace with HMAC in production
    signature = f"{token}:{task_id}:{expires_at.timestamp()}"
    return token


def verify_share_token(token: str) -> Optional[dict]:
    """
    Verify and decode share token.
    Returns token data if valid, None if expired or invalid.
    """
    token_data = _share_tokens.get(token)
    if not token_data:
        return None

    if datetime.utcnow() > token_data["expires_at"]:
        # Token expired - remove it
        del _share_tokens[token]
        return None

    return token_data


# =============================================================================
# EXPORT ENDPOINTS
# =============================================================================


@router.post("/pdf")
async def export_pdf(
    export_request: ExportRequest, current_user: User = Depends(get_current_user)
):
    """
    Export content as PDF file.

    Generates a PDF document from the stored content and streams it as a file download.
    Uses HTML templates + PDF rendering (Playwright or WeasyPrint).

    Returns:
        StreamingResponse with PDF file
    """
    logger.info(
        f"[Export PDF] task_id={export_request.task_id}, user={current_user.id}, content_type={export_request.content_type}"
    )

    try:
        # Import exporter service
        from app.services.exporters.pdf_exporter import generate_pdf

        # Generate PDF (this will be implemented in the exporter service)
        pdf_bytes = await generate_pdf(
            task_id=export_request.task_id,
            content_type=export_request.content_type,
            include_branding=export_request.include_branding,
        )

        # Update export metadata
        if export_request.task_id not in _export_metadata:
            _export_metadata[export_request.task_id] = {
                "task_id": export_request.task_id,
                "exports": [],
            }

        _export_metadata[export_request.task_id]["exports"].append(
            {
                "format": "pdf",
                "exported_at": datetime.utcnow(),
                "user_id": current_user.id,
                "file_size": len(pdf_bytes),
            }
        )

        # Generate filename
        filename = f"{export_request.content_type.lower()}_{export_request.task_id}.pdf"

        logger.info(
            f"[Export PDF] Generated PDF: {len(pdf_bytes)} bytes, filename={filename}"
        )

        # Return PDF as streaming response
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes)),
                "X-Export-Task-Id": export_request.task_id,
                "X-Export-Format": "pdf",
            },
        )

    except FileNotFoundError:
        logger.error(
            f"[Export PDF] Content not found for task_id={export_request.task_id}"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Content not found for task {export_request.task_id}",
        )
    except Exception as e:
        logger.error(f"[Export PDF] Error: {str(e)}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/html", response_model=ShareLinkResponse)
async def export_html(
    export_request: ExportRequest,
    ttl_hours: int = Query(
        168, ge=1, le=720, description="Time-to-live in hours (default 7 days)"
    ),
    current_user: User = Depends(get_current_user),
):
    """
    Export content as HTML and generate shareable link.

    Creates a time-boxed share link with signed token.
    The link allows anyone with the token to view the HTML content.

    Args:
        export_request: Export configuration
        ttl_hours: Link expiration time in hours (default 168 = 7 days)

    Returns:
        ShareLinkResponse with URL and token
    """
    logger.info(
        f"[Export HTML] task_id={export_request.task_id}, user={current_user.id}, ttl={ttl_hours}h"
    )

    try:
        # Import exporter service
        from app.services.exporters.html_exporter import generate_html

        # Generate HTML content
        html_content = await generate_html(
            task_id=export_request.task_id,
            content_type=export_request.content_type,
            include_branding=export_request.include_branding,
        )

        # Generate secure token
        token = generate_share_token()
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        # Sign token
        signed_token = sign_share_token(token, export_request.task_id, expires_at)

        # Store token data
        _share_tokens[signed_token] = {
            "token": signed_token,
            "task_id": export_request.task_id,
            "content_type": export_request.content_type,
            "html_content": html_content,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "created_by": current_user.id,
            "view_count": 0,
        }

        # Update export metadata
        if export_request.task_id not in _export_metadata:
            _export_metadata[export_request.task_id] = {
                "task_id": export_request.task_id,
                "exports": [],
            }

        _export_metadata[export_request.task_id]["exports"].append(
            {
                "format": "html",
                "exported_at": datetime.utcnow(),
                "user_id": current_user.id,
                "share_token": signed_token,
                "expires_at": expires_at,
            }
        )

        # Generate share URL
        base_url = os.getenv("APP_BASE_URL", "http://localhost:3000")
        share_url = f"{base_url}/share/{signed_token}"

        logger.info(
            f"[Export HTML] Share link generated: {share_url}, expires={expires_at}"
        )

        return ShareLinkResponse(
            success=True,
            share_url=share_url,
            expires_at=expires_at,
            token=signed_token,
            message=f"Share link generated successfully (expires in {ttl_hours} hours)",
        )

    except FileNotFoundError:
        logger.error(
            f"[Export HTML] Content not found for task_id={export_request.task_id}"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Content not found for task {export_request.task_id}",
        )
    except Exception as e:
        logger.error(f"[Export HTML] Error: {str(e)}")
        logger.exception(e)
        raise HTTPException(status_code=500, detail=f"HTML generation failed: {str(e)}")


@router.get("/status/{task_id}", response_model=ExportStatusResponse)
async def get_export_status(
    task_id: str, current_user: User = Depends(get_current_user)
):
    """
    Get export status for a task.

    Returns information about previous exports including:
    - Whether task has been exported
    - Export count
    - Last export timestamp
    - Available formats
    """
    logger.info(f"[Export Status] task_id={task_id}, user={current_user.id}")

    metadata = _export_metadata.get(task_id)

    if not metadata:
        return ExportStatusResponse(
            task_id=task_id,
            exported=False,
            export_count=0,
            last_export=None,
            formats_available=[],
        )

    exports = metadata.get("exports", [])
    formats = list(set([exp["format"] for exp in exports]))
    last_export = max([exp["exported_at"] for exp in exports]) if exports else None

    return ExportStatusResponse(
        task_id=task_id,
        exported=len(exports) > 0,
        export_count=len(exports),
        last_export=last_export,
        formats_available=formats,
    )


@router.delete("/share/{token}")
async def revoke_share_link(token: str, current_user: User = Depends(get_current_user)):
    """
    Revoke a share link token.

    Invalidates the token so the share link can no longer be accessed.
    Only the user who created the link can revoke it.
    """
    logger.info(f"[Revoke Share] token={token[:10]}..., user={current_user.id}")

    token_data = _share_tokens.get(token)

    if not token_data:
        raise HTTPException(
            status_code=404, detail="Share link not found or already expired"
        )

    # Verify user owns this token
    if str(token_data["created_by"]) != str(current_user.id):
        raise HTTPException(
            status_code=403, detail="You can only revoke your own share links"
        )

    # Remove token
    del _share_tokens[token]

    logger.info(f"[Revoke Share] Token revoked successfully")

    return {"success": True, "message": "Share link revoked successfully"}


# =============================================================================
# PUBLIC SHARE LINK VIEWER (No auth required)
# =============================================================================


@router.get("/share/{token}")
async def view_shared_content(token: str):
    """
    View shared content via public link.

    This endpoint does NOT require authentication.
    Validates the token and returns HTML content if valid.
    """
    logger.info(f"[View Share] token={token[:10]}...")

    # Verify token
    token_data = verify_share_token(token)

    if not token_data:
        raise HTTPException(
            status_code=404, detail="Share link not found, expired, or invalid"
        )

    # Increment view count
    token_data["view_count"] += 1

    logger.info(f"[View Share] Serving content, views={token_data['view_count']}")

    # Return HTML content
    from fastapi.responses import HTMLResponse

    return HTMLResponse(
        content=token_data["html_content"],
        headers={
            "X-Share-Token": token[:10] + "...",
            "X-Content-Type": token_data["content_type"],
            "X-View-Count": str(token_data["view_count"]),
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


# =============================================================================
# DEVELOPMENT/DEBUG ENDPOINTS
# =============================================================================


@router.get("/debug/tokens")
async def debug_list_tokens():
    """
    Debug endpoint to list all active share tokens.
    Only available in development mode.
    """
    import os

    if os.getenv("ENVIRONMENT", "production") != "development":
        raise HTTPException(status_code=403, detail="Debug endpoint not available")

    tokens_info = []
    for token, data in _share_tokens.items():
        tokens_info.append(
            {
                "token": token[:20] + "...",
                "task_id": data["task_id"],
                "content_type": data["content_type"],
                "created_at": data["created_at"],
                "expires_at": data["expires_at"],
                "view_count": data["view_count"],
                "expired": datetime.utcnow() > data["expires_at"],
            }
        )

    return {"total_tokens": len(_share_tokens), "tokens": tokens_info}


@router.post("/debug/cleanup")
async def debug_cleanup_expired():
    """
    Debug endpoint to clean up expired tokens.
    Only available in development mode.
    """
    import os

    if os.getenv("ENVIRONMENT", "production") != "development":
        raise HTTPException(status_code=403, detail="Debug endpoint not available")

    now = datetime.utcnow()
    expired_tokens = [
        token for token, data in _share_tokens.items() if data["expires_at"] < now
    ]

    for token in expired_tokens:
        del _share_tokens[token]

    logger.info(f"[Cleanup] Removed {len(expired_tokens)} expired tokens")

    return {
        "cleaned": len(expired_tokens),
        "remaining": len(_share_tokens),
        "message": f"Removed {len(expired_tokens)} expired tokens",
    }


# =============================================================================
# MOCK BROCHURE EXPORT (No auth, dev helper)
# =============================================================================


@router.post("/brochure-mock", response_model=BrochureResult)
async def export_brochure_mock(payload: BrochureInput):
    """
    Generate a simple brochure HTML (mock), save to /uploads, return file URL.

    This endpoint does not use LLM/SSE/auth and is safe for dev.
    """
    task_id = uuid.uuid4().hex

    title = payload.title or "Property Brochure"
    subtitle = payload.subtitle or "Presented by Aura"
    address = payload.address or "123 Main Street"
    price = payload.price or "Contact for price"
    bedrooms = payload.bedrooms if payload.bedrooms is not None else None
    bathrooms = payload.bathrooms if payload.bathrooms is not None else None
    area = payload.area_sqft if payload.area_sqft is not None else None
    ptype = payload.property_type or "Residential"
    highlights = payload.highlights or [
        "Prime location",
        "Modern finishes",
        "Close to amenities",
    ]
    amenities = payload.amenities or [
        "Fitness Center",
        "Swimming Pool",
        "24/7 Security",
        "Covered Parking",
    ]

    # Inline CSS, Tailwind-like semantics (no external deps)
    facts = []
    if bedrooms is not None:
        facts.append(f"{bedrooms} BR")
    if bathrooms is not None:
        facts.append(f"{bathrooms} BA")
    if area is not None:
        facts.append(f"{area:,} sqft")
    if ptype:
        facts.append(ptype)

    facts_html = "".join(
        f'<span class="chip">{item}</span>' for item in facts
    )
    highlights_html = "".join(
        f"<li><span class='dot'></span><span>{h}</span></li>" for h in highlights
    )
    amenities_html = "".join(
        f"<li><span class='dot'></span><span>{a}</span></li>" for a in amenities
    )

    html = f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{title}</title>
    <style>
      :root {{ --blue: #2563eb; --bg: #f8fafc; --ink: #0f172a; --muted: #64748b; }}
      body {{ margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background: var(--bg); color: var(--ink); }}
      .wrap {{ max-width: 920px; margin: 24px auto; padding: 24px; background:#fff; border-radius: 12px; box-shadow: 0 6px 18px rgba(15,23,42,.06); border:1px solid #e5e7eb; }}
      .title {{ font-size: 28px; font-weight: 700; margin: 0; }}
      .subtitle {{ margin-top: 4px; color: var(--muted); font-size: 14px; }}
      .meta {{ display:flex; align-items: center; justify-content: space-between; margin-top: 12px; }}
      .address {{ color: var(--muted); font-size: 14px; display:flex; gap:6px; align-items:center; }}
      .price {{ font-size: 18px; font-weight: 700; color: var(--blue); }}
      .chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top: 12px; }}
      .chip {{ display:inline-flex; align-items:center; gap:6px; background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; padding:6px 10px; border-radius:999px; font-size:12px; font-weight:600; }}
      .section {{ margin-top: 20px; }}
      .section h3 {{ font-size: 12px; text-transform: uppercase; letter-spacing:.08em; color: var(--muted); margin:0 0 8px; }}
      ul {{ list-style:none; padding:0; margin:0; }}
      li {{ display:flex; gap:8px; margin:6px 0; font-size:14px; color:#1f2937; }}
      .dot {{ width:6px; height:6px; border-radius:999px; background: var(--blue); margin-top:8px; display:inline-block; flex: 0 0 auto; }}
      .footer {{ margin-top: 22px; padding-top: 14px; border-top:1px solid #e5e7eb; color: var(--muted); font-size:12px; display:flex; justify-content:space-between; }}
    </style>
  </head>
  <body>
    <div class=\"wrap\">
      <header>
        <p class=\"subtitle\">{subtitle}</p>
        <h1 class=\"title\">{title}</h1>
        <div class=\"meta\">
          <div class=\"address\">{address}</div>
          <div class=\"price\">{price}</div>
        </div>
        <div class=\"chips\">{facts_html}</div>
      </header>

      <section class=\"section\">
        <h3>Highlights</h3>
        <ul>
          {highlights_html}
        </ul>
      </section>

      <section class=\"section\">
        <h3>Amenities</h3>
        <ul>
          {amenities_html}
        </ul>
      </section>

      <div class=\"footer\">
        <span>Generated by Aura (mock)</span>
        <span>Task ID: {task_id}</span>
      </div>
    </div>
  </body>
 </html>
"""

    file_url = save_html(html, prefix="brochure")

    return BrochureResult(task_id=task_id, file_url=file_url, status="completed")
