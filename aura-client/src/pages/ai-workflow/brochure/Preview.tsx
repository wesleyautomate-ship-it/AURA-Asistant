import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ChevronLeft, Share2, Download, Save } from 'lucide-react';
import { brochureDraftService } from '../../../services/brochureDrafts';
import type { BrochureDraft } from '../../../types/brochure';
import { useCommandStore, type RequestType } from '../../../store/commandStore';
import { createRequest } from '../../../services/requestsApi';

export default function BrochurePreview() {
  const navigate = useNavigate();
  const { draftId } = useParams();
  const headingRef = useRef<HTMLHeadingElement>(null);
  const [draft, setDraft] = useState<BrochureDraft | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    document.title = 'Brochure Preview — Aura';
    const t = setTimeout(() => headingRef.current?.focus(), 0);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    (async () => {
      try {
        if (!draftId) return;
        const d = await brochureDraftService.getDraft(draftId);
        setDraft(d);
      } catch (e: any) {
        setError(e?.message || 'Failed to load draft');
      }
    })();
  }, [draftId]);

  const addRequest = useCommandStore((s) => s.addRequest);
  const updateRequestStatus = useCommandStore((s) => s.updateRequestStatus);
  const [toast, setToast] = useState<{ open: boolean; text: string }>(() => ({ open: false, text: '' }));

  const onSaveToRequests = async () => {
    if (!draftId) return;
    // POST stub
    const resp = await createRequest({ type: 'brochure', draftId, pdfUrl: draft?.output?.pdfUrl });
    // Mirror to local requests list so it appears immediately
    const title = `Brochure: ${draft?.content?.title || draft?.listingData?.title || draft?.id}`;
    const localId = addRequest(title, 'PROPERTY_BROCHURE' as RequestType, { draftId, pdfUrl: draft?.output?.pdfUrl });
    if (resp.status === 'Ready') {
      updateRequestStatus(localId, 'Complete');
    }
    setToast({ open: true, text: 'Saved to Requests' });
    setTimeout(() => setToast({ open: false, text: '' }), 2000);
  };

  const onShare = async () => {
    const shareUrl = window.location.href;
    const text = `Brochure preview: ${draft?.content?.title || ''}`;
    // try web share
    if ((navigator as any).share) {
      try {
        await (navigator as any).share({ title: 'Brochure Preview', text, url: shareUrl });
        return;
      } catch {}
    }
    // fallback copy
    try {
      await navigator.clipboard.writeText(shareUrl);
      alert('Link copied to clipboard');
    } catch {}
  };

  return (
    <div className="min-h-[100dvh] bg-slate-50">
      <div className="max-w-5xl mx-auto px-4 pt-2 pb-[calc(80px+env(safe-area-inset-bottom))]">
        <div className="flex items-center gap-3 py-2 mb-2">
          <button onClick={() => navigate('/ai-workflow/brochure')} className="p-2 -ml-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" aria-label="Back">
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>
          <div>
            <h1 ref={headingRef} tabIndex={-1} className="text-base sm:text-lg font-semibold text-gray-900">Brochure Preview</h1>
            <p className="text-xs text-gray-600">Draft ID: {draftId}</p>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 text-red-700 p-3 text-sm">{error}</div>
        )}

        <div className="rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden">
          <div className="p-4 sm:p-6">
            <h2 className="text-lg font-semibold text-gray-900">{draft?.content?.title || draft?.listingData?.title || 'Property Brochure'}</h2>
            <p className="text-sm text-gray-600">{draft?.content?.description || `Discover ${draft?.listingData?.title || 'this property'}.`}</p>
            <div className="mt-4">
              <h3 className="text-xs uppercase tracking-wide text-gray-500">Highlights</h3>
              <ul className="list-disc pl-5 text-sm text-gray-700">
                {(draft?.content?.highlights || ['Prime location','Modern amenities','Spacious layout']).map((h, i) => (
                  <li key={i}>{h}</li>
                ))}
              </ul>
            </div>
            <div className="mt-4">
              <h3 className="text-xs uppercase tracking-wide text-gray-500">Amenities</h3>
              <ul className="list-disc pl-5 text-sm text-gray-700">
                {(draft?.listingData?.amenities || []).slice(0,5).map((a: any, i: number) => (<li key={i}>{String(a)}</li>))}
              </ul>
            </div>
            <div className="mt-4">
              <h3 className="text-xs uppercase tracking-wide text-gray-500">Agent</h3>
              <p className="text-sm text-gray-700">{draft?.brand ? 'Branded' : 'Unbranded'}</p>
            </div>
          </div>
        </div>
    </div>

    {/* Sticky actions */}
    <div className="fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-md border-t border-gray-200 px-4 py-2 pb-[calc(10px+env(safe-area-inset-bottom))] z-40">
      <div className="max-w-5xl mx-auto flex items-center justify-between gap-3">
        <div className="text-xs text-gray-500">Preview • {draft?.status}</div>
        <div className="flex items-center gap-2">
            <a
              href={draft?.output?.pdfUrl || '#'}
              download
              className={`inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold ${draft?.output?.pdfUrl ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-blue-300 text-white cursor-not-allowed'}`}
              aria-disabled={!draft?.output?.pdfUrl}
              onClick={(e) => { if (!draft?.output?.pdfUrl) e.preventDefault(); }}
            >
              <Download className="w-4 h-4" /> Download PDF
            </a>
            <button onClick={onShare} className="inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold border border-gray-300 hover:bg-gray-50">
              <Share2 className="w-4 h-4" /> Share
            </button>
          <button onClick={onSaveToRequests} className="inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold border border-gray-300 hover:bg-gray-50">
            <Save className="w-4 h-4" /> Save to Requests
          </button>
          </div>
      </div>
    </div>

    {/* Lightweight toast */}
    {toast.open && (
      <div className="fixed bottom-16 left-1/2 -translate-x-1/2 z-50">
        <div className="px-3 py-2 rounded-xl text-sm font-medium text-white bg-gray-900/90 shadow-md">
          {toast.text} · <a href="/requests" className="underline text-blue-200">View</a>
        </div>
      </div>
    )}
  </div>
  );
}
