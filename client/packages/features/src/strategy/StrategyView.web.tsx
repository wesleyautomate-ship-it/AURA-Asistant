import React, { useMemo, useState, useEffect } from 'react';
import ListingStrategy from './ListingStrategy.web';
import TargetAnalysis from './TargetAnalysis.web';
import MarketingTimeline from './MarketingTimeline.web';
import NegotiationPrep from './NegotiationPrep.web';
import { usePropertyStore } from '@propertypro/store';

interface Props {
  onBack?: () => void;
}


const StrategyView: React.FC<Props> = ({ onBack }) => {
  const teal = '#0891b2';
  const propertyStore = usePropertyStore();
  const [selectedPropertyId, setSelectedPropertyId] = useState<string | null>(null);

  useEffect(() => {
    try {
      // Ensure properties are fetched for selection
      // @ts-ignore optional chaining for robustness
      if (propertyStore.fetch?.status === 'idle' || !propertyStore.fetch?.lastUpdated) {
        propertyStore.fetchProperties().catch(() => {});
      }
    } catch {}
  }, []);

  const properties: any[] = (propertyStore as any)?.items || [];
  const selected = useMemo(() => {
    if (!selectedPropertyId) return properties[0] || null;
    return properties.find((p) => String(p.id) === String(selectedPropertyId)) || null;
  }, [properties, selectedPropertyId]);

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="flex items-center justify-between p-6 border-b border-gray-200 bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="flex items-center">
          {onBack ? (
            <button onClick={onBack} className="p-2 rounded-xl hover:bg-gray-100 transition-colors duration-200" aria-label="Go back">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          ) : (
            <span className="w-10" />
          )}
          <div className="ml-4">
            <h2 className="text-xl font-semibold" style={{ color: '#0f172a' }}>Strategy</h2>
            <p className="text-sm" style={{ color: '#475569' }}>Plan for Success ??" Listing strategy, audience, timeline, negotiation</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: teal }}></div>
          <span className="text-xs font-medium" style={{ color: '#475569' }}>AI Ready</span>
        </div>
      </header>

      {/* Body */}
      <main className="flex-1 overflow-y-auto p-6 md:p-8 pb-20">
        {/* Property Selector */}
        <div className="max-w-6xl mx-auto mb-6">
          <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div>
              <div className="text-sm font-semibold" style={{ color: teal }}>Selected Property</div>
              <div className="text-sm" style={{ color: '#0f172a' }}>{selected ? (selected.address || selected.title || 'Property') : 'None'}</div>
            </div>
            <div>
              <select
                className="border rounded-lg px-3 py-2 text-sm"
                style={{ borderColor: '#e2e8f0', color: '#0f172a' }}
                value={selectedPropertyId ?? ''}
                onChange={(e) => setSelectedPropertyId(e.target.value || null)}
              >
                <option value="">Auto-select first</option>
                {properties.map((p) => (
                  <option key={p.id} value={String(p.id)}>{p.address || p.title || `Property ${p.id}`}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Modules Grid */}
        <div className="max-w-6xl mx-auto grid grid-cols-1 gap-6">
          <ListingStrategy selectedPropertyId={selectedPropertyId} />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <TargetAnalysis selectedPropertyId={selectedPropertyId} />
            <MarketingTimeline selectedPropertyId={selectedPropertyId} />
          </div>
          <NegotiationPrep selectedPropertyId={selectedPropertyId} />
        </div>
      </main>
    </div>
  );
};

export default StrategyView;
