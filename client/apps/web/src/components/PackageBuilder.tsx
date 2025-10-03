import React, { useState } from 'react';

interface StepDef { id: string; title: string; description?: string }

const PackageBuilder: React.FC = () => {
  const [name, setName] = useState('Custom Package');
  const [steps, setSteps] = useState<StepDef[]>([
    { id: 'step-1', title: 'Add Step Title' },
  ]);

  const addStep = () => {
    setSteps(s => [...s, { id: `step-${s.length + 1}`, title: 'New Step' }]);
  };

  const updateStep = (idx: number, field: keyof StepDef, value: string) => {
    setSteps(s => s.map((st, i) => i === idx ? { ...st, [field]: value } : st));
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-5 py-4 border-b" style={{ borderColor: '#e5e7eb' }}>
        <h3 className="text-lg font-semibold" style={{ color: '#0f172a' }}>Package Builder</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>Create custom multi-step workflows</p>
      </div>
      <div className="p-5 space-y-4">
        <div>
          <label className="text-xs block mb-1" style={{ color: '#475569' }}>Package Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" style={{ borderColor: '#e2e8f0', color: '#0f172a' }} />
        </div>

        <div className="space-y-3">
          {steps.map((st, idx) => (
            <div key={st.id} className="rounded-xl border p-3" style={{ borderColor: '#e2e8f0' }}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div>
                  <label className="text-xs block mb-1" style={{ color: '#475569' }}>Step Title</label>
                  <input value={st.title} onChange={(e) => updateStep(idx, 'title', e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" style={{ borderColor: '#e2e8f0', color: '#0f172a' }} />
                </div>
                <div>
                  <label className="text-xs block mb-1" style={{ color: '#475569' }}>Description</label>
                  <input value={st.description ?? ''} onChange={(e) => updateStep(idx, 'description', e.target.value)} className="w-full border rounded-lg px-3 py-2 text-sm" style={{ borderColor: '#e2e8f0', color: '#0f172a' }} />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-2">
          <button onClick={addStep} className="px-3 py-2 text-sm rounded-lg font-semibold" style={{ background: '#0891b2', color: 'white' }}>Add Step</button>
          <button className="px-3 py-2 text-sm rounded-lg font-semibold" style={{ background: '#f1f5f9', color: '#0f172a' }}>Save (mock)</button>
        </div>
      </div>
    </div>
  );
};

export default PackageBuilder;
