import type { BrochureDraft } from '../types/brochure';
import { saveHtml } from '../api/documents';

function escapeHtml(input: string | undefined): string {
  if (!input) return '';
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export async function generateBrochureHTML(draft: BrochureDraft): Promise<string> {
  const brandPrimary = draft.brand?.primary || '#1D4ED8';
  const brandSecondary = draft.brand?.secondary || '#9333EA';
  const title = draft.content?.title || draft.listingData?.title || 'Property Brochure';
  const description = draft.content?.description || `Discover ${draft.listingData?.title || 'this property'}.`;
  const highlights = draft.content?.highlights || [];
  const location = draft.listingData?.location || '';

  const logoImg = draft.brand?.logoUrl
    ? `<img src="${draft.brand.logoUrl}" alt="Brand Logo" style="height:40px;border-radius:8px;border:1px solid #e5e7eb;"/>`
    : '';

  const html = `<!doctype html>
  <html>
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>${escapeHtml(title)}</title>
      <style>
        :root { --primary: ${brandPrimary}; --secondary: ${brandSecondary}; }
        body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; margin: 0; background: #f8fafc; color: #0f172a; }
        .wrap { max-width: 800px; margin: 0 auto; padding: 24px; }
        .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; box-shadow: 0 6px 20px rgba(2,6,23,0.06); overflow: hidden; }
        .header { display:flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #eef2f7; }
        .title { font-size: 22px; font-weight: 700; color: #0f172a; }
        .subtitle { color: #475569; font-size: 14px; margin-top: 2px; }
        .badge { display:inline-block; background: var(--primary); color: #fff; padding: 2px 10px; border-radius: 999px; font-size: 12px; }
        .content { padding: 20px; display:grid; gap: 16px; }
        .section-title { font-size: 14px; font-weight: 600; color: #0f172a; margin-bottom: 8px; }
        .desc { font-size: 14px; color: #334155; line-height: 1.5; }
        ul { margin: 0; padding-left: 18px; color: #334155; }
        li { margin: 4px 0; }
        .footer { padding: 16px 20px; border-top: 1px solid #eef2f7; display:flex; justify-content: space-between; align-items:center; }
        .cta { background: var(--secondary); color:#fff; padding: 10px 14px; border-radius: 10px; text-decoration: none; font-weight: 600; }
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="card">
          <div class="header">
            <div>
              <div class="title">${escapeHtml(title)}</div>
              ${location ? `<div class="subtitle">${escapeHtml(location)}</div>` : ''}
            </div>
            ${logoImg}
          </div>
          <div class="content">
            <div>
              <div class="section-title">About this property</div>
              <div class="desc">${escapeHtml(description)}</div>
            </div>
            ${highlights.length ? `<div>
              <div class="section-title">Highlights</div>
              <ul>${highlights.map(h => `<li>${escapeHtml(h)}</li>`).join('')}</ul>
            </div>` : ''}
          </div>
          <div class="footer">
            <span class="badge">${escapeHtml(draft.template || 'clean-minimal')}</span>
            <a class="cta" href="#">Contact Agent</a>
          </div>
        </div>
      </div>
    </body>
  </html>`;

  return html;
}

// Save generated HTML via backend and return a stable file URL (mapped as pdfUrl for UI)
export async function exportBrochureFile(html: string): Promise<{ pdfUrl: string }> {
  const data = await saveHtml({ html, prefix: 'brochure' });
  return { pdfUrl: data.file_url };
}

export async function exportBrochurePDF(html: string): Promise<{ pdfUrl: string }> {
  // Mock client-side PDF export: create a Blob with placeholder content.
  // In production, POST to backend service to render HTML → PDF, return URL.
  const mockPdfBlob = new Blob([`Mock PDF generated at ${new Date().toISOString()}\n\n---\n${html}`], { type: 'application/pdf' });
  const pdfUrl = URL.createObjectURL(mockPdfBlob);
  return { pdfUrl };
}
