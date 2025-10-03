import React, { useMemo } from 'react';
import { useStrategySources, analyzeTargetAudience } from './utils/strategyGeneration';

interface Props {
  selectedPropertyId?: string | null;
}

const TargetAnalysis: React.FC<Props> = ({ selectedPropertyId }) => {
  const { properties, clients } = useStrategySources();
  const selected = useMemo(() => {
    return selectedPropertyId ? properties.find(p => String(p.id) === String(selectedPropertyId)) : properties[0];
  }, [properties, selectedPropertyId]);

  const segments = useMemo(() => analyzeTargetAudience(selected || {}, clients), [selected, clients]);
  const teal = '#0891b2';

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-5 py-4 border-b" style={{ borderColor: '#e5e7eb' }}>
        <h3 className="text-lg font-semibold" style={{ color: '#0f172a' }}>Target Audience Analysis</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>Combines CRM (Beta-2) with property fit</p>
      </div>
      <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {segments.map(seg => (
          <div key={seg.name} className="rounded-xl border p-4" style={{ borderColor: '#e2e8f0' }}>
            <div className="flex items-center justify-between mb-2">
              <div className="text-base font-semibold" style={{ color: teal }}>{seg.name}</div>
              <div className="text-xs font-bold px-2 py-1 rounded-full" style={{ background: '#ccfbf1', color: '#115e59' }}>{seg.score}</div>
            </div>
            <div className="text-xs mb-1" style={{ color: '#0f172a' }}>Demographics</div>
            <div className="flex flex-wrap gap-2 mb-3">
              {seg.demographics.map(d => (
                <span key={d} className="text-xs px-2 py-1 rounded-md" style={{ background: '#f1f5f9', color: '#0f172a' }}>{d}</span>
              ))}
            </div>
            <div className="text-xs mb-1" style={{ color: '#0f172a' }}>Interests</div>
            <div className="flex flex-wrap gap-2">
              {seg.interests.map(i => (
                <span key={i} className="text-xs px-2 py-1 rounded-md" style={{ background: '#eef2ff', color: '#1e293b' }}>{i}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TargetAnalysis;

