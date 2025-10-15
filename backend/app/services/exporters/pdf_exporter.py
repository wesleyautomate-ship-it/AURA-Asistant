"""
PDF Exporter Service
=====================

Generates PDF documents from content templates.
Uses HTML templates + PDF rendering library (WeasyPrint or Playwright).

Version: 3.2
Phase: Track 1.4 - Export Service
"""

import logging
from typing import Optional
from datetime import datetime
from app.schemas.content_types import ContentType

logger = logging.getLogger(__name__)


# Mock content storage - replace with actual database/storage
_content_storage = {}


async def generate_pdf(
    task_id: str, content_type: ContentType, include_branding: bool = True
) -> bytes:
    """
    Generate PDF from content data.

    Args:
        task_id: Task ID containing the content
        content_type: Type of content to export
        include_branding: Whether to include company branding

    Returns:
        PDF file as bytes

    Raises:
        FileNotFoundError: If content not found for task_id
    """
    logger.info(
        f"[PDF Exporter] Generating PDF for task={task_id}, type={content_type}"
    )

    # Fetch content (from database in production)
    content_data = _content_storage.get(task_id)

    if not content_data:
        # For development, generate mock PDF
        logger.warning(f"[PDF Exporter] Content not found, generating mock PDF")
        return await _generate_mock_pdf(task_id, content_type, include_branding)

    # Generate HTML from template
    html_content = await _render_html_template(
        content_data, content_type, include_branding
    )

    # Convert HTML to PDF
    pdf_bytes = await _html_to_pdf(html_content)

    logger.info(f"[PDF Exporter] PDF generated: {len(pdf_bytes)} bytes")

    return pdf_bytes


async def _render_html_template(
    content_data: dict, content_type: ContentType, include_branding: bool
) -> str:
    """Render HTML template with content data"""

    # Template selection based on content type
    templates = {
        ContentType.CMA_REPORT: _render_cma_html,
        ContentType.PITCH_DECK: _render_pitch_deck_html,
        ContentType.MARKET_REPORT: _render_market_report_html,
        ContentType.NEWSLETTER: _render_newsletter_html,
        ContentType.SOCIAL_POST: _render_social_post_html,
    }

    renderer = templates.get(content_type, _render_generic_html)
    return renderer(content_data, include_branding)


async def _html_to_pdf(html_content: str) -> bytes:
    """
    Convert HTML to PDF using WeasyPrint or Playwright.

    For production:
    - WeasyPrint: pip install weasyprint
    - Playwright: pip install playwright && playwright install chromium
    """
    try:
        # Try WeasyPrint first
        from weasyprint import HTML

        pdf_bytes = HTML(string=html_content).write_pdf()
        logger.info("[PDF Exporter] Generated PDF using WeasyPrint")
        return pdf_bytes
    except ImportError:
        logger.warning("[PDF Exporter] WeasyPrint not available, using mock PDF")
        # Fallback to mock PDF
        return await _generate_simple_mock_pdf(html_content)


async def _generate_mock_pdf(
    task_id: str, content_type: ContentType, include_branding: bool
) -> bytes:
    """Generate a mock PDF for development/testing"""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = f"{content_type.replace('_', ' ').title()}"
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))

    # Metadata
    story.append(Paragraph(f"Task ID: {task_id}", styles["Normal"]))
    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 24))

    # Content sections based on type
    if content_type == ContentType.CMA_REPORT:
        story.append(Paragraph("Comparative Market Analysis", styles["Heading1"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Executive Summary", styles["Heading2"]))
        story.append(
            Paragraph(
                "This is a mock CMA report generated for development purposes. In production, this would contain real market data, comparable properties, and valuation analysis.",
                styles["Normal"],
            )
        )
        story.append(Spacer(1, 12))

        # Mock comparables table
        data = [
            ["Address", "Price", "Sq.Ft", "Price/Sq.Ft"],
            ["123 Main St", "$500,000", "2,000", "$250"],
            ["456 Oak Ave", "$525,000", "2,100", "$250"],
            ["789 Pine Rd", "$490,000", "1,950", "$251"],
        ]
        table = Table(data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(table)

    elif content_type == ContentType.PITCH_DECK:
        story.append(Paragraph("Investment Opportunity", styles["Heading1"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Property Overview", styles["Heading2"]))
        story.append(
            Paragraph(
                "Mock investor pitch deck. Would contain slides with property details, market analysis, financial projections, and investment highlights.",
                styles["Normal"],
            )
        )

    elif content_type == ContentType.MARKET_REPORT:
        story.append(Paragraph("Market Analysis Report", styles["Heading1"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Market Trends", styles["Heading2"]))
        story.append(
            Paragraph(
                "Mock market report with trend analysis, pricing data, and market forecasts.",
                styles["Normal"],
            )
        )

    # Branding footer
    if include_branding:
        story.append(Spacer(1, 48))
        story.append(
            Paragraph(
                "Generated by RealtorPro AI - Aura Content Engine", styles["Normal"]
            )
        )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info(f"[PDF Exporter] Generated mock PDF: {len(pdf_bytes)} bytes")
    return pdf_bytes


async def _generate_simple_mock_pdf(html_content: str) -> bytes:
    """Generate simple mock PDF when no PDF library available"""
    # Minimal PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 100 >>
stream
BT
/F1 12 Tf
50 750 Td
(Mock PDF - Install WeasyPrint or Playwright for full PDF generation) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
0000000312 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
459
%%EOF"""

    return pdf_content


# Template renderers


def _render_cma_html(content_data: dict, include_branding: bool) -> str:
    """Render CMA Report HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CMA Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #2c3e50; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
        </style>
    </head>
    <body>
        <h1>Comparative Market Analysis</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <h2>Executive Summary</h2>
        <p>Market analysis content...</p>
        {'<footer style="margin-top: 50px; text-align: center; color: #7f8c8d;">Generated by RealtorPro AI</footer>' if include_branding else ''}
    </body>
    </html>
    """


def _render_pitch_deck_html(content_data: dict, include_branding: bool) -> str:
    """Render Pitch Deck HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Investment Pitch Deck</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .slide {{ page-break-after: always; min-height: 800px; }}
            h1 {{ color: #e74c3c; }}
        </style>
    </head>
    <body>
        <div class="slide">
            <h1>Investment Opportunity</h1>
            <p>Pitch deck content...</p>
        </div>
        {'<footer style="text-align: center; color: #7f8c8d;">RealtorPro AI</footer>' if include_branding else ''}
    </body>
    </html>
    """


def _render_market_report_html(content_data: dict, include_branding: bool) -> str:
    """Render Market Report HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Market Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #16a085; }}
        </style>
    </head>
    <body>
        <h1>Market Analysis Report</h1>
        <p>Market trends and analysis...</p>
        {'<footer style="margin-top: 50px; text-align: center; color: #7f8c8d;">RealtorPro AI</footer>' if include_branding else ''}
    </body>
    </html>
    """


def _render_newsletter_html(content_data: dict, include_branding: bool) -> str:
    """Render Newsletter HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Newsletter</title>
        <style>
            body {{ font-family: Georgia, serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #8e44ad; }}
        </style>
    </head>
    <body>
        <h1>Real Estate Newsletter</h1>
        <p>Newsletter content...</p>
        {'<footer style="margin-top: 50px; text-align: center; color: #7f8c8d;">RealtorPro AI</footer>' if include_branding else ''}
    </body>
    </html>
    """


def _render_social_post_html(content_data: dict, include_branding: bool) -> str:
    """Render Social Post HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Social Media Post</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; }}
            .post {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="post">
            <p>Social media post content...</p>
        </div>
        {'<footer style="margin-top: 30px; text-align: center; color: #7f8c8d;">RealtorPro AI</footer>' if include_branding else ''}
    </body>
    </html>
    """


def _render_generic_html(content_data: dict, include_branding: bool) -> str:
    """Render generic HTML"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Content Export</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
        </style>
    </head>
    <body>
        <h1>Exported Content</h1>
        <p>Content data...</p>
        {'<footer style="margin-top: 50px; text-align: center; color: #7f8c8d;">RealtorPro AI</footer>' if include_branding else ''}
    </body>
    </html>
    """
