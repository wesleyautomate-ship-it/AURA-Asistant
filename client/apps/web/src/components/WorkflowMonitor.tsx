import React, { useEffect, useState } from 'react';
import { listRuns, type WorkflowRun } from '../services/workflowEngine';

interface Props {
  onRefresh?: () => void;
}

const statusColor = (s: WorkflowRun['status']) => {
  switch (s) {
    case 'completed': return 'bg-green-100 text-green-800';
    case 'running': return 'bg-blue-100 text-blue-800';
    case 'failed': return 'bg-red-100 text-red-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

const stepColor = (s: any) => {
  switch (s) {
    case 'completed': return 'text-green-700';
    case 'running': return 'text-blue-700';
    case 'failed': return 'text-red-700';
    default: return 'text-gray-700';
  }
};

const WorkflowMonitor: React.FC<Props> = () => {
  const [runs, setRuns] = useState<WorkflowRun[]>([]);

  const refresh = () => setRuns(listRuns());

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="px-5 py-4 border-b" style={{ borderColor: '#e5e7eb' }}>
        <h3 className="text-lg font-semibold" style={{ color: '#0f172a' }}>Workflow Monitor</h3>
        <p className="text-sm" style={{ color: '#64748b' }}>Execution monitoring and progress tracking</p>
      </div>
      <div className="p-5 space-y-4">
        {runs.length === 0 && (
          <div className="text-sm" style={{ color: '#64748b' }}>No runs yet. Start a package to see progress here.</div>
        )}
        {runs.map(run => (
          <div key={run.id} className="rounded-xl border p-4" style={{ borderColor: '#e2e8f0' }}>
            <div className="flex items-center justify-between mb-2">
              <div className="text-base font-semibold" style={{ color: '#0891b2' }}>{run.packageName}</div>
              <span className={`text-xs font-bold px-2 py-1 rounded-full ${statusColor(run.status)}`}>{run.status.toUpperCase()}</span>
            </div>
            <div className="text-xs mb-2" style={{ color: '#475569' }}>Started: {new Date(run.startedAt).toLocaleString()}</div>
            <div className="space-y-1">
              {run.steps.map(s => (
                <div key={s.id} className="flex items-center justify-between text-sm">
                  <div className="font-medium" style={{ color: '#0f172a' }}>{s.title}</div>
                  <div className={stepColor(s.status)}>{s.status}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkflowMonitor;
