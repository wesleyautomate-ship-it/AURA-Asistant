import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Megaphone } from 'lucide-react';

export default function AIWorkflowSocial() {
  const navigate = useNavigate();
  const headingRef = useRef<HTMLHeadingElement>(null);
  const [selected, setSelected] = useState<string | null>(null);
  useEffect(() => {
    document.title = 'Social Templates — Aura';
    const t = setTimeout(() => headingRef.current?.focus(), 0);
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
            <h1 ref={headingRef} tabIndex={-1} className="text-lg sm:text-xl font-semibold text-gray-900">Social Templates</h1>
            <p className="text-sm text-gray-600">Choose a template to start</p>
          </div>
        </div>
        <section className="mt-4 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {SOCIAL_TEMPLATES.map(t => (
              <TemplateCard key={t.id} selected={selected === t.id} onSelect={() => setSelected(t.id)} title={t.title} desc={t.desc} />
            ))}
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              disabled={!selected}
              className={`inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white shadow-sm transition focus:outline-none focus:ring-2 focus:ring-purple-500 ${selected ? 'bg-purple-600 hover:bg-purple-700' : 'bg-purple-300 cursor-not-allowed'}`}
              onClick={() => { /* TODO: create draft */ navigate('/requests'); }}
            >
              Use Template
            </button>
            <button
              type="button"
              className="inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
              onClick={() => navigate('/requests')}
            >
              Start from Blank
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}

const SOCIAL_TEMPLATES = [
  { id: 'listing', title: 'Listing Spotlight', desc: 'Showcase a property with a CTA.' },
  { id: 'market', title: 'Market Update', desc: 'Trends and insights post.' },
  { id: 'story', title: 'Agent Story', desc: 'Personalized narrative format.' },
];

function TemplateCard({ title, desc, selected, onSelect }: { title: string; desc: string; selected: boolean; onSelect: () => void }) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full text-left rounded-2xl border ${selected ? 'border-purple-500 ring-2 ring-purple-200' : 'border-gray-200'} bg-white p-4 shadow-sm hover:shadow-md transition`}
      aria-pressed={selected}
    >
      <div className="h-24 mb-3 rounded-xl bg-gradient-to-br from-purple-50 to-white border border-purple-100" />
      <div className="space-y-1">
        <div className="text-sm font-semibold text-gray-900">{title}</div>
        <div className="text-xs text-gray-600">{desc}</div>
      </div>
    </button>
  );
}
