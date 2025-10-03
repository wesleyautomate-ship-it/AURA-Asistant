import React, { useMemo } from 'react';
import { buildMarketingTimeline } from './utils/strategyGeneration';
import { useStrategySources } from './utils/strategyGeneration';

interface Props {
  selectedPropertyId?: string | null;
}

const MarketingTimeline: React.FC<Props> = ({ selectedPropertyId }) => {
  const { properties } = useStrategySources();
  const selected = useMemo(() => {
    return selectedPropertyId ? properties.find(p => String(p.id) === String(selectedPropertyId)) : properties[0];
  }, [properties, selectedPropertyId]);

  const timeline = useMemo(() => buildMarketingTimeline(selected || {}), [selected]);
  const teal = '#0891b2';

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-5 py-4 border-b" style={{ borderColor: '#e5e7eb' }}>
        <h3 className="text-lg font-semibold" style={{ color: '#0f172a' }}>Marketing Timeline</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>Coordinates with templates from Beta-3</p>
      </div>
      <div className="p-5 space-y-4">
        {timeline.map(item => (
          <div key={item.id} className="flex items-start gap-4">
            <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold" style={{ background: '#ccfbf1', color: '#115e59' }}>W{item.week}</div>
            <div className="flex-1">
              <div className="text-sm font-semibold" style={{ color: teal }}>{item.title}</div>
              <div className="text-sm" style={{ color: '#334155' }}>{item.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MarketingTimeline;

