import React, { useState } from 'react';
import PackageTemplates from './PackageTemplates';
import WorkflowMonitor from './WorkflowMonitor';
import PackageBuilder from './PackageBuilder';
import { PACKAGE_TEMPLATES } from '../utils/packageOrchestration';
import { startRun } from '../services/workflowEngine';

const PackagesView: React.FC<{ onBack: () => void; }> = ({ onBack }) => {
  const teal = '#0891b2';
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);

  const handleStart = async (id?: string) => {
    const tpl = PACKAGE_TEMPLATES.find(t => t.id === (id ?? selectedTemplateId));
    if (!tpl) return;
    await startRun(tpl, {});
    // Monitor will auto-refresh and show the run
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-gray-50 to-gray-100">
      <header className="flex items-center justify-between p-6 border-b border-gray-200 bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="flex items-center">
          <button onClick={onBack} className="p-2 rounded-xl hover:bg-gray-100 transition-colors duration-200" aria-label="Go back">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="ml-4">
            <h2 className="text-xl font-semibold" style={{ color: '#0f172a' }}>Packages</h2>
            <p className="text-sm" style={{ color: '#475569' }}>Automate multi-step workflows across Strategy, Marketing, CRM</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: teal }}></div>
          <span className="text-xs font-medium" style={{ color: '#475569' }}>AI Ready</span>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto p-6 md:p-8 pb-20">
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            <PackageTemplates onSelect={(id) => { setSelectedTemplateId(id); handleStart(id); }} />
            <PackageBuilder />
          </div>
          <div className="space-y-6">
            <WorkflowMonitor />
            <div className="bg-white border border-gray-200 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="text-base font-semibold" style={{ color: teal }}>Quick Start</div>
              </div>
              <div className="flex gap-2 flex-wrap">
                <button onClick={() => handleStart('new_listing')} className="px-3 py-2 text-sm rounded-lg font-semibold" style={{ background: '#0891b2', color: 'white' }}>New Listing Package</button>
                <button onClick={() => handleStart('lead_nurture')} className="px-3 py-2 text-sm rounded-lg font-semibold" style={{ background: '#7c3aed', color: 'white' }}>Lead Nurturing Package</button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default PackagesView;
