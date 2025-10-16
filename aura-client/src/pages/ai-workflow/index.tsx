import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, FileText, BarChart3, Megaphone, ExternalLink } from 'lucide-react';
// import { useCommandStore } from '../../store/commandStore';
import { brochureDraftService } from '../../services/brochureDrafts';
import type { BrochureDraft } from '../../types/brochure';

export default function AIWorkflowIndex() {
  const navigate = useNavigate();
  const headingRef = useRef<HTMLHeadingElement>(null);
  // Reserved for future: intelligence content list
  const [brochureDrafts, setBrochureDrafts] = useState<BrochureDraft[]>([] as BrochureDraft[]);
  useEffect(() => {
    brochureDraftService.listDrafts().then((ds) => setBrochureDrafts(ds.slice(0, 5))).catch(() => setBrochureDrafts([]));
  }, []);

  useEffect(() => {
    document.title = 'AI Workflow — Aura';
    const t = setTimeout(() => headingRef.current?.focus(), 0);
    return () => clearTimeout(t);
  }, []);
  return (
    <div className="min-h-[100dvh] bg-gradient-to-b from-gray-50 via-white to-blue-50">
      <div className="max-w-4xl mx-auto px-4 pt-2 pb-[calc(64px+env(safe-area-inset-bottom))] sm:pt-4 sm:pb-6">
        {/* Header */}
        <header className="flex items-center gap-3 py-2 mb-2">
          <button
            onClick={() => navigate('/')}
            className="p-2 -ml-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Back to Dashboard"
          >
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>
          <div>
            <h1 ref={headingRef} tabIndex={-1} className="text-base sm:text-lg font-semibold text-gray-900 dark:text-neutral-100">AI Workflow</h1>
            <p className="text-xs text-gray-600 dark:text-neutral-400 truncate">Create brochure, CMA, or social content</p>
          </div>
        </header>

        {/* Body */}
        <div className="mt-2 space-y-4">
          {/* Quick Start */}
          <section>
            <h2 className="sr-only">Quick Start</h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4">
              <ActionCard
                size="compact"
                icon={<FileText className="w-5 h-5 text-blue-600 opacity-80" />}
                title="Brochure"
                caption="Generate a property brochure"
                onClick={() => navigate('/ai-workflow/brochure')}
              />
              <ActionCard
                size="compact"
                icon={<BarChart3 className="w-5 h-5 text-emerald-600 opacity-80" />}
                title="CMA Report"
                caption="Comparative market analysis"
                onClick={() => navigate('/ai-workflow/cma')}
              />
              <ActionCard
                size="compact"
                className="col-span-2 sm:col-span-1"
                icon={<Megaphone className="w-5 h-5 text-purple-600 opacity-80" />}
                title="Social Post"
                caption="Draft a social caption"
                onClick={() => navigate('/ai-workflow/social')}
              />
            </div>
          </section>

          {/* Recent Drafts (placeholder) */}
          <section className="mt-2 mb-2">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold text-gray-800 dark:text-neutral-200">Recent Drafts</h3>
            </div>
            {brochureDrafts.length > 0 ? (
              <ul className="space-y-2">
                {brochureDrafts.map((d) => (
                  <li key={d.id}>
                    <button
                      type="button"
                      className="w-full text-left rounded-xl border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 p-3 shadow-sm hover:shadow-md transition focus:outline-none focus:ring-2 focus:ring-blue-500"
                      onClick={() => navigate(`/ai-workflow/brochure/editor/${d.id}`)}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-gray-900 dark:text-neutral-100 truncate">{d.content?.title || 'Brochure Draft'}</p>
                          <p className="text-xs text-gray-600 dark:text-neutral-400 truncate">{d.template} · {d.status}</p>
                        </div>
                        <ExternalLink className="w-4 h-4 text-gray-400" />
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="rounded-2xl border border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 p-4 text-sm text-gray-600 dark:text-neutral-400">
                No drafts yet.
              </div>
            )}
          </section>

          {/* Learn/Help */}
          {import.meta.env.VITE_DOCS_URL ? (
            <div className="text-right">
              <a href={import.meta.env.VITE_DOCS_URL} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700 dark:text-neutral-400 dark:hover:text-neutral-200">
                Learn / Help
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

interface ActionCardProps {
  icon: React.ReactNode;
  title: string;
  caption?: string;
  onClick: () => void;
  size?: 'compact' | 'default';
  className?: string;
}

function ActionCard({ icon, title, caption, onClick, size = 'default', className = '' }: ActionCardProps) {
  const isCompact = size === 'compact';
  const baseClasses = "w-full text-left rounded-2xl bg-white dark:bg-neutral-900 shadow-md hover:shadow-lg transition border border-gray-100 dark:border-neutral-700 focus:outline-none focus:ring-2 focus:ring-blue-500";
  const compactClasses = "p-3 h-[118px] flex flex-col justify-between";
  const defaultClasses = "aspect-[4/3] p-4";
  const rootClasses = `${baseClasses} ${isCompact ? compactClasses : defaultClasses} sm:aspect-[4/3] sm:p-4 sm:h-auto ${className}`;

  const titleClasses = isCompact
    ? "text-[15px] font-semibold leading-tight text-gray-900 dark:text-neutral-100"
    : "text-base font-semibold text-gray-900 dark:text-neutral-100";
  const captionClasses = isCompact
    ? "text-[12px] text-gray-600 dark:text-neutral-400 leading-snug line-clamp-2"
    : "text-sm text-gray-600 dark:text-neutral-400";

  return (
    <button
      type="button"
      onClick={onClick}
      className={rootClasses}
      aria-label={title}
    >
      <div className={`flex h-full flex-col ${isCompact ? 'justify-between space-y-1.5' : 'justify-center space-y-2'}`}>
        <div>{icon}</div>
        <div className="space-y-1">
          <div className={titleClasses}>{title}</div>
          {caption && <div className={captionClasses}>{caption}</div>}
        </div>
      </div>
    </button>
  );
}
