import React, { useMemo } from 'react';
import { useStrategySources, prepareNegotiationPlan } from './utils/strategyGeneration';

interface Props {
  selectedPropertyId?: string | null;
}

const NegotiationPrep: React.FC<Props> = ({ selectedPropertyId }) => {
  const { properties } = useStrategySources();
  const selected = useMemo(() => {
    return selectedPropertyId ? properties.find(p => String(p.id) === String(selectedPropertyId)) : properties[0];
  }, [properties, selectedPropertyId]);

  const plays = useMemo(() => prepareNegotiationPlan(selected || {}), [selected]);
  const teal = '#0891b2';

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-5 py-4 border-b" style={{ borderColor: '#e5e7eb' }}>
        <h3 className="text-lg font-semibold" style={{ color: '#0f172a' }}>Negotiation Preparation</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>Offer analysis and counter-strategies</p>
      </div>
      <div className="p-5 grid grid-cols-1 md:grid-cols-3 gap-4">
        {plays.map((p) => (
          <div key={p.name} className="rounded-xl border p-4 flex flex-col gap-2" style={{ borderColor: '#e2e8f0' }}>
            <div className="text-sm font-semibold" style={{ color: teal }}>{p.name}</div>
            <div className="text-xs" style={{ color: '#334155' }}><span className="font-bold">Trigger:</span> {p.trigger}</div>
            <div className="text-xs" style={{ color: '#334155' }}><span className="font-bold">Counter:</span> {p.counter}</div>
            <div className="mt-auto">
              <span className="text-[10px] px-2 py-1 rounded-full font-bold" style={{ background: p.risk === 'high' ? '#fee2e2' : p.risk === 'medium' ? '#ffedd5' : '#dcfce7', color: '#111827' }}>RISK: {p.risk.toUpperCase()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NegotiationPrep;

