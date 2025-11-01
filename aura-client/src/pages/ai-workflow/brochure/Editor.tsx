import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ChevronLeft, Search, CheckCircle2, Check, Loader2 } from 'lucide-react';
import { brochureDraftService } from '../../../services/brochureDrafts';
import { renderDraft as apiRenderDraft } from '../../../features/brochure/api/brochure';
import { useBrochureDraft } from '../../../features/brochure/hooks/useBrochureDraft';
import type { BrochureDraft } from '../../../types/brochure';
import { seededListings, type SeededListing } from '../../../data/seededListings';

type StepKey = 'property' | 'content' | 'branding' | 'review';
const STEPS: { key: StepKey; label: string }[] = [
  { key: 'property', label: 'Property' },
  { key: 'content', label: 'Content' },
  { key: 'branding', label: 'Branding' },
  { key: 'review', label: 'Review' },
];

function useDebouncedCallback<T extends any[]>(fn: (...args: T) => void, delay = 300) {
  const timeoutRef = useRef<number | null>(null);
  return (...args: T) => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    timeoutRef.current = window.setTimeout(() => fn(...args), delay);
  };
}

export default function BrochureEditor() {
  const navigate = useNavigate();
  const params = useParams();
  const draftId = (params.draftId as string) || (params.id as string);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const { draft, setDraft, error, saving, savedVisible, update } = useBrochureDraft(draftId);
  const [stepIndex, setStepIndex] = useState(0);
  const [genError, setGenError] = useState<string | null>(null);
  const [autoGenerating, setAutoGenerating] = useState(false);

  useEffect(() => {
    document.title = 'Brochure Editor - Aura';
    const t = setTimeout(() => headingRef.current?.focus(), 0);
    return () => clearTimeout(t);
  }, []);

  // saving and savedVisible handled by hook

  const onBack = () => {
    if (autoGenerating) return;
    setStepIndex((i) => Math.max(0, i - 1));
  };
  const onNext = () => {
    if (autoGenerating) return;
    setStepIndex((i) => Math.min(STEPS.length - 1, i + 1));
  };

  const canNext = (() => {
    if (stepIndex === 0) return Boolean(draft?.propertyId);
    if (stepIndex === 1) return Boolean(draft?.content?.title || draft?.content?.description);
    return true;
  })();

  const progress = Math.round(((stepIndex + 1) / STEPS.length) * 100);

  const buildListingData = (listing: SeededListing) => ({
    id: listing.listingId,
    title: listing.title,
    community: listing.location,
    location: listing.location,
    price_aed: listing.priceAED,
    highlights: [
      'Prime location in the heart of Dubai',
      'Modern interiors and expansive living spaces',
      'Close to lifestyle destinations and transport links',
    ],
  });

  const buildListingContent = (listing: SeededListing) => ({
    title: listing.title,
    description: `Experience ${listing.title} located in ${listing.location}. This residence combines elegant design with modern convenience for discerning buyers.`,
    highlights: [
      'Generous floor plan with natural light',
      'Premium finishes and contemporary styling',
      `Asking price AED ${listing.priceAED.toLocaleString()}`,
    ],
  });

  const buildListingBrand = () => ({
    primary: '#2563EB',
    secondary: '#7C3AED',
    logoUrl: '',
  });

  const autoGenerateFromListing = useCallback(
    async (listing: SeededListing) => {
      if (!draftId) return;
      setAutoGenerating(true);
      setGenError(null);
      try {
        const listingData = buildListingData(listing);
        const content = buildListingContent(listing);
        const brand = buildListingBrand();

        const updated = await brochureDraftService.updateDraft(draftId, {
          propertyId: listing.listingId,
          listingData,
          content,
          brand,
          status: 'generating',
        });
        setDraft(updated);
        setStepIndex(3);

        await apiRenderDraft(draftId);

        const timeoutMs = 60000;
        const start = Date.now();
        let latest = updated;

        while (Date.now() - start < timeoutMs) {
          await new Promise((resolve) => setTimeout(resolve, 900));
          latest = await brochureDraftService.getDraft(draftId);
          setDraft(latest);
          if (latest.status === 'ready') {
            navigate(`/ai-workflow/brochure/preview/${draftId}`);
            return;
          }
          if (latest.status === 'error') {
            throw new Error(latest.error || 'Brochure rendering failed');
          }
        }
        throw new Error('Brochure rendering timed out.');
      } catch (err: any) {
        setGenError(err?.message || 'Failed to generate brochure automatically.');
        setStepIndex(3);
      } finally {
        setAutoGenerating(false);
      }
    },
    [draftId, navigate, setDraft]
  );

  return (
    <div className="min-h-[100dvh] bg-gradient-to-b from-gray-50 via-white to-blue-50">
      <div className="max-w-4xl mx-auto px-4 pt-2 pb-[calc(80px+env(safe-area-inset-bottom))] sm:pt-4">
        {/* Header */}
        <div className="flex items-center gap-3 py-2 mb-2">
          <button
            onClick={() => navigate('/ai-workflow/brochure')}
            className="p-2 -ml-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Back"
            disabled={autoGenerating}
          >
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </button>
          <div>
            <h1 ref={headingRef} tabIndex={-1} className="text-base sm:text-lg font-semibold text-gray-900">Brochure Editor</h1>
            <p className="text-xs text-gray-600">Draft ID: {draftId}</p>
          </div>
        </div>

        {/* Step tabs */}
        <nav className="flex items-center gap-2 overflow-x-auto scrollbar-hide py-1 mb-3">
          {STEPS.map((s, i) => (
            <button
              key={s.key}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border transition ${
                i === stepIndex ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
              } ${autoGenerating ? 'opacity-60 cursor-not-allowed' : ''}`}
              onClick={() => !autoGenerating && setStepIndex(i)}
              disabled={autoGenerating}
            >
              {s.label}
            </button>
          ))}
        </nav>

        {/* Steps */}
        <div className="space-y-3">
          {stepIndex === 0 && (
            <PropertyStep
              draft={draft}
              busy={autoGenerating}
              onSelect={async (listing) => {
                await autoGenerateFromListing(listing);
              }}
            />
          )}
          {stepIndex === 1 && (
            <ContentStep draft={draft} onChange={(content) => update({ content })} />
          )}
          {stepIndex === 2 && (
            <BrandingStep draft={draft} onChange={(brand) => update({ brand })} />
          )}
          {stepIndex === 3 && (
            <ReviewStep draft={draft} error={genError} onGenerate={async () => {
              if (!draftId) return;
              try {
                setGenError(null);
                setDraft((d) => (d ? { ...d, status: 'generating' } : d));
                await brochureDraftService.updateDraft(draftId, { status: 'generating' });
                await apiRenderDraft(draftId);
                // poll until ready
                const start = Date.now();
                const timeoutMs = 60000;
                while (Date.now() - start < timeoutMs) {
                  const refreshed = await brochureDraftService.getDraft(draftId);
                  setDraft(refreshed);
                  if (refreshed.status === 'ready') break;
                  await new Promise(r => setTimeout(r, 900));
                }
              } catch (e: any) {
                const msg = e?.message || 'Failed to generate brochure';
                setGenError(msg);
                const errored = await brochureDraftService.updateDraft(draftId, { status: 'error', error: msg });
                setDraft(errored);
              }
            }} onRetry={async () => {
              // Retry generation using same flow
              if (!draftId) return;
              setGenError(null);
            }} />
          )}

          {error && (
            <div className="rounded-xl border border-red-200 bg-red-50 text-red-700 p-3 text-sm">{error}</div>
          )}
        </div>
      </div>

      {/* Sticky footer nav */}
      <div className="fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-md border-t border-gray-200 px-4 py-2 pb-[calc(10px+env(safe-area-inset-bottom))] z-40">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between gap-3">
            <div className="flex-1">
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-blue-600" style={{ width: `${progress}%` }} />
              </div>
              <div className="flex items-center justify-between mt-1">
                <div className="text-[11px] text-gray-500">Step {stepIndex + 1} of {STEPS.length}</div>
                <div className="text-[11px] text-gray-500 flex items-center gap-1 min-h-[16px]">
                  {saving && <span>Saving...</span>}
                  {!saving && savedVisible && (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Saved</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={onBack} disabled={stepIndex === 0} className={`px-4 py-2 rounded-xl text-sm font-semibold border ${stepIndex === 0 ? 'text-gray-400 border-gray-200 cursor-not-allowed' : 'text-gray-700 border-gray-300 hover:bg-gray-50'}`}>Back</button>
              <button onClick={onNext} disabled={stepIndex === STEPS.length - 1 || !canNext} className={`px-4 py-2 rounded-xl text-sm font-semibold ${(stepIndex === STEPS.length - 1 || !canNext) ? 'bg-blue-300 text-white cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700'}`}>Next</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PropertyStep({ draft, onSelect, busy }: { draft: BrochureDraft | null; onSelect: (l: SeededListing) => void; busy: boolean }) {
  const [query, setQuery] = useState('');
  const listings = useMemo(() => {
    const q = query.trim().toLowerCase();
    const all = seededListings;
    return q
      ? all.filter((l) => l.title.toLowerCase().includes(q) || l.location.toLowerCase().includes(q) || l.listingId.toLowerCase().includes(q))
      : all;
  }, [query]);

  const selectedId = draft?.propertyId;

  return (
    <section className="space-y-3" aria-busy={busy}>
      {busy && (
        <div className="flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-700">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Generating...</span>
        </div>
      )}
      <div className="relative">
        <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by title, area, or ID"
          disabled={busy}
          aria-disabled={busy}
          className={`w-full pl-9 pr-3 py-2 rounded-xl border border-gray-300 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${busy ? 'opacity-60 cursor-not-allowed' : ''}`}
        />
      </div>
      <ul className="divide-y divide-gray-200 rounded-2xl border border-gray-200 bg-white overflow-hidden shadow-sm">
        {listings.map((l) => (
          <li key={l.listingId}>
            <button
              type="button"
              onClick={() => {
                if (busy) return;
                onSelect(l);
              }}
              disabled={busy}
              className={`w-full text-left px-3 py-3 flex items-center justify-between gap-3 ${selectedId === l.listingId ? 'bg-blue-50' : ''} ${busy ? 'cursor-not-allowed opacity-70' : ''}`}
            >
              <div className="min-w-0">
                <div className="text-sm font-semibold text-gray-900 truncate">{l.title}</div>
                <div className="text-xs text-gray-600 truncate">{l.location} / {l.listingId}</div>
              </div>
              {selectedId === l.listingId && (
                busy ? (
                  <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-5 h-5 text-blue-600" />
                )
              )}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
function ContentStep({ draft, onChange }: { draft: BrochureDraft | null; onChange: (c: NonNullable<BrochureDraft['content']>) => void }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [highlights, setHighlights] = useState<string>('');

  // Prefill when draft changes
  useEffect(() => {
    const d = draft;
    const ld = (d?.listingData || {}) as Partial<SeededListing>;
    const content = d?.content || {};
    const defaultTitle = content.title ?? (ld.title ? `${ld.title}` : 'Property Brochure');
    const defaultDesc = content.description ?? (ld.location ? `Discover ${ld.title} in ${ld.location}.` : '');
    const defaultHighlights = (content.highlights && content.highlights.length > 0)
      ? content.highlights.join('\n')
      : ['Prime location', 'Modern amenities', 'Spacious layout'].join('\n');
    setTitle(defaultTitle);
    setDescription(defaultDesc);
    setHighlights(defaultHighlights);
  }, [draft?.id]);

  const debouncedPush = useDebouncedCallback(() => {
    onChange({ title, description, highlights: highlights.split('\n').map((s) => s.trim()).filter(Boolean) });
  }, 300);

  useEffect(() => {
    debouncedPush();
  }, [title, description, highlights]);

  return (
    <section className="space-y-3">
      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm space-y-3">
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Title</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Description</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4} className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Highlights (one per line)</label>
          <textarea value={highlights} onChange={(e) => setHighlights(e.target.value)} rows={4} className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
    </section>
  );
}

function BrandingStep({ draft, onChange }: { draft: BrochureDraft | null; onChange: (b: NonNullable<BrochureDraft['brand']>) => void }) {
  const [logoUrl, setLogoUrl] = useState<string>('');
  const [primary, setPrimary] = useState<string>('#1D4ED8');
  const [secondary, setSecondary] = useState<string>('#9333EA');

  useEffect(() => {
    setLogoUrl(draft?.brand?.logoUrl || '');
    setPrimary(draft?.brand?.primary || '#1D4ED8');
    setSecondary(draft?.brand?.secondary || '#9333EA');
  }, [draft?.id]);

  const debouncedPush = useDebouncedCallback(() => {
    onChange({ logoUrl, primary, secondary });
  }, 300);

  useEffect(() => {
    debouncedPush();
  }, [logoUrl, primary, secondary]);

  const onFile = (f?: File) => {
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      const url = String(reader.result || '');
      setLogoUrl(url);
    };
    reader.readAsDataURL(f);
  };

  return (
    <section className="space-y-3">
      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm space-y-4">
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">Logo (optional)</label>
          {logoUrl ? (
            <div className="flex items-center gap-3">
              <img src={logoUrl} alt="Logo" className="w-12 h-12 rounded-lg border" />
              <button type="button" className="px-3 py-2 rounded-xl text-sm font-semibold border border-gray-300 hover:bg-gray-50" onClick={() => setLogoUrl('')}>Remove</button>
            </div>
          ) : (
            <input type="file" accept="image/*" onChange={(e) => onFile(e.target.files?.[0] || undefined)} className="block text-sm" />
          )}
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Primary Color</label>
            <input type="color" value={primary} onChange={(e) => setPrimary(e.target.value)} className="w-12 h-10 p-0 border rounded cursor-pointer align-middle" />
            <input type="text" value={primary} onChange={(e) => setPrimary(e.target.value)} className="ml-2 w-28 rounded-md border border-gray-300 px-2 py-1 text-xs" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Secondary Color</label>
            <input type="color" value={secondary} onChange={(e) => setSecondary(e.target.value)} className="w-12 h-10 p-0 border rounded cursor-pointer align-middle" />
            <input type="text" value={secondary} onChange={(e) => setSecondary(e.target.value)} className="ml-2 w-28 rounded-md border border-gray-300 px-2 py-1 text-xs" />
          </div>
        </div>
      </div>
    </section>
  );
}

function ReviewStep({ draft, error, onGenerate, onRetry }: { draft: BrochureDraft | null; error?: string | null; onGenerate: () => void; onRetry: () => void }) {
  return (
    <section className="space-y-3">
      <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">Summary</h3>
        <div className="text-sm text-gray-700">
          <div><span className="text-gray-500">Property:</span> {draft?.listingData?.title || 'N/A'} ({draft?.propertyId || 'N/A'})</div>
          <div><span className="text-gray-500">Location:</span> {draft?.listingData?.location || 'N/A'}</div>
          <div className="mt-2"><span className="text-gray-500">Title:</span> {draft?.content?.title || 'N/A'}</div>
          <div><span className="text-gray-500">Description:</span> {draft?.content?.description || 'N/A'}</div>
          <div className="mt-2"><span className="text-gray-500">Highlights:</span>
            <ul className="list-disc pl-5 mt-1">
              {(draft?.content?.highlights || []).map((h, i) => (
                <li key={i}>{h}</li>
              ))}
            </ul>
          </div>
          <div className="mt-2"><span className="text-gray-500">Brand:</span> {draft?.brand?.primary || 'N/A'} / {draft?.brand?.secondary || 'N/A'}</div>
        </div>
        <div className="mt-4">
          <button type="button" onClick={onGenerate} className="inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            Render PDF
          </button>
          {draft?.status === 'generating' && <span className="ml-3 text-sm text-blue-700">Generating...</span>}
          {draft?.status === 'ready' && <span className="ml-3 text-sm text-emerald-700">Ready</span>}
          {draft?.status === 'error' && (
            <span className="ml-3 text-sm text-red-700">{error || 'Generation failed.'} <button type="button" onClick={onRetry} className="underline">Retry</button></span>
          )}
        </div>
      </div>
    </section>
  );
}
