import React, { useMemo } from 'react';
import { useStrategySources, generateListingStrategy } from './utils/strategyGeneration';
import { usePropertyStore } from '@propertypro/store';

interface Props {
  selectedPropertyId?: string | null;
}

const ListingStrategy: React.FC<Props> = ({ selectedPropertyId }) => {
  const { properties } = useStrategySources();
  const selected = useMemo(() => {
    return selectedPropertyId ? properties.find(p => String(p.id) === String(selectedPropertyId)) : properties[0];
  }, [properties, selectedPropertyId]);

  const strategy = useMemo(() => generateListingStrategy(selected || {}), [selected]);

  const teal = '#0891b2';

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-5 py-4 border-b flex items-center justify-between" style={{ borderColor: '#e5e7eb' }}>
        <div>
          <h3 className="text-lg font-semibold" style={{ color: '#0f172a' }}>Listing Strategy</h3>
          <p className="text-sm" style={{ color: '#64748b' }}>Auto-generated from property analytics (Beta-1)</p>
        </div>
        <span className="px-3 py-1 text-xs font-bold rounded-full" style={{ background: '#ccfbf1', color: '#0f766e' }}>TEAL</span>
      </div>

      <div className="p-5 space-y-5">
        <div>
          <h4 className="text-base font-semibold mb-1" style={{ color: teal }}>{strategy.title}</h4>
          <p className="text-sm" style={{ color: '#334155' }}>{strategy.summary}</p>
        </div>

        <div>
          <h5 className="text-sm font-bold mb-2" style={{ color: '#0f172a' }}>Key Selling Points</h5>
          <div className="flex flex-wrap gap-2">
            {strategy.usps.map((u) => (
              <span key={u.key} className="text-xs px-2 py-1 rounded-full border" style={{ borderColor: '#94a3b8', color: '#0f172a' }}>{u.key}: {u.value}</span>
            ))}
          </div>
        </div>

        <div>
          <h5 className="text-sm font-bold mb-2" style={{ color: '#0f172a' }}>Pricing Options</h5>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {strategy.pricing.alternatives.map((alt) => (
              <div key={alt.label} className="rounded-xl border p-3" style={{ borderColor: '#e2e8f0' }}>
                <div className="text-xs font-semibold" style={{ color: teal }}>{alt.label}</div>
                <div className="text-lg font-bold" style={{ color: '#0f172a' }}>{alt.price ? `$${alt.price.toLocaleString()}` : 'TBD'}</div>
                <div className="text-xs" style={{ color: '#475569' }}>{alt.notes}</div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h5 className="text-sm font-bold mb-2" style={{ color: '#0f172a' }}>Primary Channels</h5>
          <div className="flex flex-wrap gap-2">
            {strategy.channels.map((c) => (
              <span key={c} className="text-xs px-2 py-1 rounded-md" style={{ background: '#f1f5f9', color: '#0f172a' }}>{c}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListingStrategy;

