import React from 'react';
import { PACKAGE_TEMPLATES } from '../utils/packageOrchestration';

interface Props {
  onSelect: (id: string) => void;
}

const PackageTemplates: React.FC<Props> = ({ onSelect }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-5 py-4 border-b" style={{ borderColor: '#e5e7eb' }}>
        <h3 className="text-lg font-semibold" style={{ color: '#0f172a' }}>Package Templates</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>Pre-built workflows for common tasks</p>
      </div>
      <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        {PACKAGE_TEMPLATES.map(t => (
          <div key={t.id} className="rounded-xl border p-4 flex flex-col gap-2" style={{ borderColor: '#e2e8f0' }}>
            <div className="flex items-center justify-between">
              <div className="text-base font-semibold" style={{ color: '#0891b2' }}>{t.name}</div>
              <span className="text-[10px] font-bold px-2 py-1 rounded-full" style={{ background: '#ccfbf1', color: '#115e59' }}>TEMPLATE</span>
            </div>
            <div className="text-sm" style={{ color: '#334155' }}>{t.summary}</div>
            <div className="text-xs" style={{ color: '#475569' }}>Steps: {t.steps.map(s => s.title).join(' → ')}</div>
            <div className="mt-2">
              <button onClick={() => onSelect(t.id)} className="px-3 py-2 text-sm rounded-lg font-semibold" style={{ background: '#0891b2', color: 'white' }}>Start</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PackageTemplates;
