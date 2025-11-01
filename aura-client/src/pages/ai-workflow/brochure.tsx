import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { brochureDraftService, mapTemplateIdToKey } from '../../services/brochureDrafts';
import { listTemplates, type BrochureTemplateOut } from '../../features/brochure/api/brochure';

export default function AIWorkflowBrochure() {
  const navigate = useNavigate();
  const headingRef = useRef<HTMLHeadingElement>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [templates, setTemplates] = useState<BrochureTemplateOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    document.title = 'Brochure Templates - Aura';
    const t = setTimeout(() => headingRef.current?.focus(), 0);
    (async () => {
      try {
        const data = await listTemplates();
        setTemplates(data);
      } catch (e: any) {
        setError(e?.message || 'Failed to load templates');
        setTemplates([]);
      }
    })();
    return () => clearTimeout(t);
  }, []);
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-blue-50">
      <div className="max-w-4xl mx-auto px-4 py-4 sm:py-6">
        <div className="flex items-center gap-3 mb-2">
          <button onClick={() => navigate('/ai-workflow')} className="p-2 -ml-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" aria-label="Back">
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>
          <div>
            <h1 ref={headingRef} tabIndex={-1} className="text-lg sm:text-xl font-semibold text-gray-900">Brochure Templates</h1>
            <p className="text-sm text-gray-600">Choose a template to start</p>
          </div>
        </div>
        <section className="mt-4 space-y-4">
          {error && <div className="rounded-xl border border-red-200 bg-red-50 text-red-700 p-3 text-sm">{error}</div>}
          {!templates && <div className="text-sm text-gray-600">Loading templates...</div>}
          {templates && templates.length === 0 && <div className="text-sm text-gray-600">No templates available.</div>}
          {templates && templates.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {templates.map(t => (
                <TemplateCard key={t.id} selected={selected === t.id} onSelect={() => setSelected(t.id)} title={t.name} desc={t.description || ''} />
              ))}
            </div>
          )}
          <div className="flex items-center gap-3">
            <button
              type="button"
              disabled={!selected}
              className={`inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white shadow-sm transition focus:outline-none focus:ring-2 focus:ring-blue-500 ${selected ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-300 cursor-not-allowed'}`}
              onClick={async () => {
                if (!selected) return;
                const templateKey = mapTemplateIdToKey(selected);
                const draft = await brochureDraftService.createDraft(templateKey);
                navigate(`/brochure/${draft.id}/property`);
              }}
            >
              Use Template
            </button>
            <button
              type="button"
              className="inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
              onClick={async () => {
                const draft = await brochureDraftService.createDraft('clean-minimal');
                navigate(`/brochure/${draft.id}/property`);
              }}
            >
              Start from Blank
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}

function TemplateCard({ title, desc, selected, onSelect }: { title: string; desc: string; selected: boolean; onSelect: () => void }) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full text-left rounded-2xl border ${selected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'} bg-white p-4 shadow-sm hover:shadow-md transition`}
      aria-pressed={selected}
    >
      <div className="h-24 mb-3 rounded-xl bg-gradient-to-br from-blue-50 to-white border border-blue-100" />
      <div className="space-y-1">
        <div className="text-sm font-semibold text-gray-900">{title}</div>
        <div className="text-xs text-gray-600">{desc}</div>
      </div>
    </button>
  );
}
