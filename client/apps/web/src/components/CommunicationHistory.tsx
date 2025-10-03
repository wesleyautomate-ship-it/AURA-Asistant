import React from 'react';
import type { CommunicationLog } from '../store';

interface Props {
  logs: CommunicationLog[];
  onLog?: (type: CommunicationLog['type']) => void;
}

export default function CommunicationHistory({ logs, onLog }: Props) {
  const typeBadge = (type: CommunicationLog['type']) => {
    switch (type) {
      case 'call': return 'bg-blue-100 text-blue-700';
      case 'email': return 'bg-emerald-100 text-emerald-700';
      case 'sms': return 'bg-purple-100 text-purple-700';
      case 'meeting': return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-700">Communication History</h4>
        {onLog && (
          <div className="flex gap-2">
            <button className="px-2 py-1 text-xs bg-emerald-600 text-white rounded" onClick={() => onLog('email')}>Email</button>
            <button className="px-2 py-1 text-xs bg-blue-600 text-white rounded" onClick={() => onLog('call')}>Call</button>
            <button className="px-2 py-1 text-xs bg-purple-600 text-white rounded" onClick={() => onLog('sms')}>SMS</button>
            <button className="px-2 py-1 text-xs bg-yellow-600 text-white rounded" onClick={() => onLog('meeting')}>Meeting</button>
          </div>
        )}
      </div>
      <div className="space-y-2">
        {logs.length === 0 && (
          <div className="text-xs text-gray-500">No communications yet.</div>
        )}
        {logs.map(log => (
          <div key={log.id} className="bg-white border rounded p-3">
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${typeBadge(log.type)}`}>{log.type.toUpperCase()}</span>
              <span className="text-[11px] text-gray-500">{new Date(log.at).toLocaleString()}</span>
            </div>
            {log.content && <div className="text-sm text-gray-700">{log.content}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}


