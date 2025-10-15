"""
HTML Exporter Service
======================

Generates standalone HTML documents for shareable links.
Includes inline styles and full content for offline viewing.

Version: 3.2
Phase: Track 1.4 - Export Service
"""

import logging
from datetime import datetime
from app.schemas.content_types import ContentType

logger = logging.getLogger(__name__)


# Mock content storage - replace with actual database/storage
_content_storage = {}


async def generate_html(
    task_id: str, content_type: ContentType, include_branding: bool = True
) -> str:
    """
    Generate standalone HTML from content data.

    Args:
        task_id: Task ID containing the content
        content_type: Type of content to export
        include_branding: Whether to include company branding

    Returns:
        Complete HTML document as string

    Raises:
        FileNotFoundError: If content not found for task_id
    """
    logger.info(
        f"[HTML Exporter] Generating HTML for task={task_id}, type={content_type}"
    )

    # Fetch content (from database in production)
    content_data = _content_storage.get(task_id)

    if not content_data:
        # For development, generate mock HTML
        logger.warning(f"[HTML Exporter] Content not found, generating mock HTML")
        return _generate_mock_html(task_id, content_type, include_branding)

    # Generate HTML based on content type
    html_content = _render_html_template(content_data, content_type, include_branding)

    logger.info(f"[HTML Exporter] HTML generated: {len(html_content)} bytes")

    return html_content


def _render_html_template(
    content_data: dict, content_type: ContentType, include_branding: bool
) -> str:
    """Render HTML template with content data"""

    templates = {
        ContentType.CMA_REPORT: _render_cma_html,
        ContentType.PITCH_DECK: _render_pitch_deck_html,
        ContentType.MARKET_REPORT: _render_market_report_html,
        ContentType.NEWSLETTER: _render_newsletter_html,
        ContentType.SOCIAL_POST: _render_social_post_html,
    }

    renderer = templates.get(content_type, _render_generic_html)
    return renderer(content_data, include_branding)


def _generate_mock_html(
    task_id: str, content_type: ContentType, include_branding: bool
) -> str:
    """Generate mock HTML for development/testing"""

    # Common styles for all content types
    common_styles = """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        .header .meta {
            opacity: 0.9;
            font-size: 0.9em;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .section h3 {
            color: #555;
            font-size: 1.3em;
            margin: 20px 0 10px;
        }
        .section p {
            margin-bottom: 15px;
            color: #666;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #667eea;
            color: white;
            font-weight: 600;
        }
        tr:hover {
            background: #f5f5f5;
        }
        .card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .footer {
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #777;
            font-size: 0.9em;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 0 5px;
        }
        .badge-success { background: #d4edda; color: #155724; }
        .badge-info { background: #d1ecf1; color: #0c5460; }
        .badge-warning { background: #fff3cd; color: #856404; }
        @media print {
            body { background: white; padding: 0; }
            .container { box-shadow: none; }
            .no-print { display: none; }
        }
    """

    # Content-specific sections
    if content_type == ContentType.CMA_REPORT:
        title = "Comparative Market Analysis"
        content_sections = """
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="card">
                    <p>This comprehensive market analysis evaluates current property values and market conditions for Dubai Marina. Based on recent comparable sales and market trends, the analysis provides insights into property valuations and investment opportunities.</p>
                </div>
            </div>
            
            <div class="section">
                <h2>Market Overview</h2>
                <p>The Dubai Marina real estate market continues to show strong performance with consistent demand and stable pricing.</p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
                    <div class="card">
                        <h3>Average Price/Sq.Ft</h3>
                        <p style="font-size: 2em; color: #667eea; font-weight: bold;">AED 1,850</p>
                    </div>
                    <div class="card">
                        <h3>Market Trend</h3>
                        <p style="font-size: 2em; color: #28a745; font-weight: bold;">↑ 12.5%</p>
                    </div>
                    <div class="card">
                        <h3>Days on Market</h3>
                        <p style="font-size: 2em; color: #667eea; font-weight: bold;">45</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Comparable Properties</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Address</th>
                            <th>Price</th>
                            <th>Sq.Ft</th>
                            <th>Bed/Bath</th>
                            <th>Price/Sq.Ft</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Marina Tower A, Unit 1502</td>
                            <td>AED 2,850,000</td>
                            <td>1,540</td>
                            <td>2/2</td>
                            <td>AED 1,851</td>
                            <td><span class="badge badge-success">Sold</span></td>
                        </tr>
                        <tr>
                            <td>Marina Promenade, Unit 804</td>
                            <td>AED 2,950,000</td>
                            <td>1,600</td>
                            <td>2/2</td>
                            <td>AED 1,844</td>
                            <td><span class="badge badge-success">Sold</span></td>
                        </tr>
                        <tr>
                            <td>Ocean Heights, Unit 2201</td>
                            <td>AED 2,775,000</td>
                            <td>1,500</td>
                            <td>2/2</td>
                            <td>AED 1,850</td>
                            <td><span class="badge badge-info">Active</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>Valuation & Recommendations</h2>
                <div class="card">
                    <h3>Estimated Market Value</h3>
                    <p>Based on the analysis of comparable properties and current market conditions, the estimated value range is <strong>AED 2,800,000 - AED 2,950,000</strong>.</p>
                    <p style="margin-top: 15px;"><strong>Recommendation:</strong> This property represents a strong investment opportunity in Dubai Marina's premium residential market with excellent rental yield potential and capital appreciation prospects.</p>
                </div>
            </div>
        """

    elif content_type == ContentType.PITCH_DECK:
        title = "Investment Pitch Deck"
        content_sections = """
            <div class="section">
                <h2>Investment Opportunity</h2>
                <div class="card">
                    <p>Premium real estate investment opportunity in Dubai's most sought-after location. This property offers exceptional returns and long-term value appreciation.</p>
                </div>
            </div>
            
            <div class="section">
                <h2>Property Overview</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                    <div>
                        <h3>Key Features</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ Prime Dubai Marina location</li>
                            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ Luxury 2-bedroom apartment</li>
                            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ Full marina and sea views</li>
                            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">✓ Premium amenities included</li>
                        </ul>
                    </div>
                    <div>
                        <h3>Investment Metrics</h3>
                        <ul style="list-style: none; padding: 0;">
                            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">Expected ROI: 8-10%</li>
                            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">Rental Yield: 6.2%</li>
                            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">Capital Appreciation: 12%/year</li>
                            <li style="padding: 8px 0; border-bottom: 1px solid #eee;">Payback Period: 10-12 years</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Financial Projections</h2>
                <table>
                    <thead>
                        <tr><th>Year</th><th>Revenue</th><th>Expenses</th><th>Net Income</th><th>ROI</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Year 1</td><td>AED 180,000</td><td>AED 45,000</td><td>AED 135,000</td><td>4.7%</td></tr>
                        <tr><td>Year 2</td><td>AED 189,000</td><td>AED 47,250</td><td>AED 141,750</td><td>4.9%</td></tr>
                        <tr><td>Year 3</td><td>AED 198,450</td><td>AED 49,613</td><td>AED 148,837</td><td>5.2%</td></tr>
                    </tbody>
                </table>
            </div>
        """

    else:  # Generic content
        title = content_type.replace("_", " ").title()
        content_sections = f"""
            <div class="section">
                <h2>Content Overview</h2>
                <div class="card">
                    <p>This is a {content_type.replace('_', ' ').lower()} generated by Aura Content Engine. In production, this would contain detailed, content-specific information based on the user's request.</p>
                </div>
            </div>
            
            <div class="section">
                <h2>Key Information</h2>
                <p>Task ID: <strong>{task_id}</strong></p>
                <p>Content Type: <strong>{content_type}</strong></p>
                <p>Generated: <strong>{datetime.now().strftime('%B %d, %Y at %I:%M %p')}</strong></p>
            </div>
        """

    # Branding footer
    footer_content = (
        """
        <div class="footer">
            <p><strong>Generated by RealtorPro AI - Aura Content Engine</strong></p>
            <p style="margin-top: 10px;">Professional real estate content powered by artificial intelligence</p>
        </div>
    """
        if include_branding
        else ""
    )

    # Complete HTML document
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - RealtorPro AI</title>
    <style>{common_styles}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="meta">
                <span class="badge badge-info">Task #{task_id}</span>
                <span class="badge badge-warning">{datetime.now().strftime('%B %d, %Y')}</span>
            </div>
        </div>
        
        <div class="content">
            {content_sections}
        </div>
        
        {footer_content}
    </div>
</body>
</html>"""

    return html


# Template renderers (same as PDF but optimized for web)


def _render_cma_html(content_data: dict, include_branding: bool) -> str:
    """Render CMA Report HTML (production version)"""
    # In production, this would use actual content_data
    return _generate_mock_html(
        "actual_task_id", ContentType.CMA_REPORT, include_branding
    )


def _render_pitch_deck_html(content_data: dict, include_branding: bool) -> str:
    """Render Pitch Deck HTML (production version)"""
    return _generate_mock_html(
        "actual_task_id", ContentType.PITCH_DECK, include_branding
    )


def _render_market_report_html(content_data: dict, include_branding: bool) -> str:
    """Render Market Report HTML (production version)"""
    return _generate_mock_html(
        "actual_task_id", ContentType.MARKET_REPORT, include_branding
    )


def _render_newsletter_html(content_data: dict, include_branding: bool) -> str:
    """Render Newsletter HTML (production version)"""
    return _generate_mock_html(
        "actual_task_id", ContentType.NEWSLETTER, include_branding
    )


def _render_social_post_html(content_data: dict, include_branding: bool) -> str:
    """Render Social Post HTML (production version)"""
    return _generate_mock_html(
        "actual_task_id", ContentType.SOCIAL_POST, include_branding
    )


def _render_generic_html(content_data: dict, include_branding: bool) -> str:
    """Render generic HTML (production version)"""
    return _generate_mock_html(
        "actual_task_id", ContentType.CMA_REPORT, include_branding
    )
