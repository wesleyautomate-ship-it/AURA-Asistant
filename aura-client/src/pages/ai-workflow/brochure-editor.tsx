import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { brochureDraftService } from '../../services/brochureDrafts';
import { listDrafts, type BrochureDraftOut } from '../../features/brochure/api/brochure';
import type { BrochureDraft } from '../../types/brochure';

export default function BrochureEditor() {
  const navigate = useNavigate();
  const { draftId } = useParams();
  const headingRef = useRef<HTMLHeadingElement>(null);
  const [draft, setDraft] = useState<BrochureDraft | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<BrochureDraftOut[] | null>(null);

  useEffect(() => {
    document.title = 'Brochure Editor — Aura';
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

  useEffect(() => {
    (async () => {
      try {
        const items = await listDrafts(10, 0);
        setHistory(items);
      } catch {
        setHistory([]);
      }
    })();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-blue-50">
      <div className="max-w-4xl mx-auto px-4 py-4 sm:py-6">
        <div className="flex items-center gap-3 mb-2">
          <button onClick={() => navigate('/ai-workflow/brochure')} className="p-2 -ml-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" aria-label="Back">
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>
          <div>
            <h1 ref={headingRef} tabIndex={-1} className="text-lg sm:text-xl font-semibold text-gray-900">Brochure Editor</h1>
            <p className="text-sm text-gray-600">Draft ID: {draftId}</p>
          </div>
        </div>

        <section className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 text-red-700 p-3 text-sm">{error}</div>
          )}
          {draft ? (
            <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="text-sm text-gray-700">Status: <span className="font-medium">{draft.status}</span></div>
              <div className="text-sm text-gray-700">Template: <span className="font-medium">{draft.template}</span></div>
              <div className="text-xs text-gray-500 mt-2">Created: {new Date(draft.createdAt).toLocaleString()}</div>
              <div className="text-xs text-gray-500">Updated: {new Date(draft.updatedAt).toLocaleString()}</div>
              <div className="mt-4 text-sm text-gray-500">Editor coming soon…</div>
            </div>
          ) : !error ? (
            <div className="text-sm text-gray-600">Loading draft…</div>
          ) : null}
          </div>
          <aside className="md:col-span-1">
            <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="text-sm font-semibold text-gray-900 mb-2">Recent Brochures</div>
              {!history && <div className="text-xs text-gray-600">Loading…</div>}
              {history && history.length === 0 && <div className="text-xs text-gray-600">No recent drafts.</div>}
              {history && history.length > 0 && (
                <ul className="space-y-2">
                  {history.map(h => (
                    <li key={h.id} className="text-xs text-gray-700 flex items-center justify-between">
                      <span className="truncate" title={h.id}>{h.id.slice(0, 8)}…</span>
                      <span className={`ml-2 px-2 py-0.5 rounded ${h.status === 'ready' ? 'bg-green-50 text-green-700' : h.status === 'rendering' ? 'bg-blue-50 text-blue-700' : h.status === 'error' ? 'bg-red-50 text-red-700' : 'bg-gray-50 text-gray-700'}`}>{h.status}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </aside>
        </section>
      </div>
    </div>
  );
}
