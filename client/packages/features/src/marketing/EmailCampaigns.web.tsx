import React, { useMemo, useState } from 'react';

export interface EmailTemplateData {
  subject: string;
  preheader?: string;
  bodyHtml: string;
}

export interface EmailCampaignProps {
  property?: {
    title?: string;
    address?: string;
    price?: number | string;
    beds?: number;
    baths?: number;
    sqft?: number;
    imageUrl?: string;
  } | null;
  brandColor?: string; // default purple
}

const defaultStyles = `
  .btn{background:#7c3aed;color:#fff;padding:12px 18px;border-radius:8px;text-decoration:none;display:inline-block}
  .card{border:1px solid #e5e7eb;border-radius:16px;overflow:hidden}
  .muted{color:#6b7280}
`;

const EmailCampaigns: React.FC<EmailCampaignProps> = ({ property, brandColor = '#7c3aed' }) => {
  const [subject, setSubject] = useState<string>('New Listing: Stunning Property Available Now');
  const [preheader, setPreheader] = useState<string>('Explore this beautiful home with top amenities.');

  const emailHtml = useMemo(() => {
    const price = typeof property?.price === 'number' ? `$${property?.price?.toLocaleString()}` : (property?.price || '');
    const img = property?.imageUrl || 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&q=80&auto=format&fit=crop';
    const titleLine = property?.title || 'Premium Residence';
    const addr = property?.address || 'Dubai, UAE';
    const facts = `${property?.beds ?? 0} bed · ${property?.baths ?? 0} bath · ${(property?.sqft ?? 0).toLocaleString()} sqft`;

    return `
      <div style="font-family:Inter,Segoe UI,Arial,sans-serif;background:#f9fafb;padding:24px;">
        <style>${defaultStyles.replace('#7c3aed', brandColor)}</style>
        <div class="card" style="background:#fff">
          <img src="${img}" alt="Property" style="width:100%;height:260px;object-fit:cover" />
          <div style="padding:20px">
            <div style="color:${brandColor};font-weight:700;font-size:14px;margin-bottom:8px">Featured Listing</div>
            <h1 style="margin:0 0 8px 0;font-size:22px;line-height:1.3">${titleLine}</h1>
            <div class="muted" style="margin-bottom:12px">${addr}</div>
            <div style="font-weight:700;font-size:18px;margin-bottom:8px">${price}</div>
            <div class="muted" style="margin-bottom:16px">${facts}</div>
            <p style="margin:0 0 16px 0">Experience luxury living with modern finishes, open-concept design, and breathtaking views. Schedule a private viewing today.</p>
            <a class="btn" href="#" style="background:${brandColor}">Request a Viewing</a>
          </div>
        </div>
        <p class="muted" style="font-size:12px;margin-top:12px">You are receiving this email because you subscribed to PropertyPro AI updates.</p>
      </div>
    `;
  }, [property, brandColor]);

  const previewSubject = subject || 'New Listing Available';
  const previewPreheader = preheader || '';

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
      <div className="p-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-800">Email Campaign</h3>
        <div className="text-xs text-gray-500">Auto-populates from selected property</div>
      </div>
      <div className="px-4 pb-4 space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input value={subject} onChange={e=>setSubject(e.target.value)} className="border rounded-md px-3 py-2 text-sm" placeholder="Email subject" />
          <input value={preheader} onChange={e=>setPreheader(e.target.value)} className="border rounded-md px-3 py-2 text-sm" placeholder="Preheader (optional)" />
        </div>
        <div className="border rounded-xl overflow-hidden">
          <div className="px-4 py-2 bg-gray-50 border-b text-xs text-gray-600">
            <div><span className="font-medium">Subject:</span> {previewSubject}</div>
            {previewPreheader && <div><span className="font-medium">Preheader:</span> {previewPreheader}</div>}
          </div>
          <iframe title="email-preview" srcDoc={emailHtml} className="w-full h-[380px]" />
        </div>
        <div className="flex items-center justify-end gap-2">
          <button className="px-3 py-2 text-xs rounded-md bg-purple-600 text-white hover:bg-purple-700">Export HTML</button>
          <button className="px-3 py-2 text-xs rounded-md bg-gray-100 text-gray-800 hover:bg-gray-200">Send Test (stub)</button>
        </div>
      </div>
    </div>
  );
};

export default EmailCampaigns;
