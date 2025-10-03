import React from 'react';
import type { Client, CommunicationLog } from '../store';
import LeadScoring from './LeadScoring';
import CommunicationHistory from './CommunicationHistory';

interface Props {
  client: Client;
  logs: CommunicationLog[];
  onBack?: () => void;
  onLogCommunication?: (type: CommunicationLog['type']) => void;
}

export default function ClientDetail({ client, logs, onBack, onLogCommunication }: Props) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">{client.name}</h3>
          <div className="text-sm text-gray-500">{client.email} • {client.phone}</div>
        </div>
        {onBack && (
          <button className="px-3 py-1 text-sm border rounded" onClick={onBack}>Back</button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2 space-y-4">
          <div className="bg-white border rounded p-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Details</h4>
            <div className="text-sm text-gray-700 space-y-1">
              {client.notes && <p>{client.notes}</p>}
              {client.lastContactedAt && <p>Last contacted: {new Date(client.lastContactedAt).toLocaleString()}</p>}
              <p>Status: <span className="uppercase font-medium">{client.status}</span></p>
            </div>
          </div>

          <div className="bg-white border rounded p-4">
            <CommunicationHistory logs={logs} onLog={onLogCommunication} />
          </div>
        </div>
        <div className="space-y-4">
          <div className="bg-white border rounded p-4">
            <LeadScoring score={client.leadScore} />
          </div>
          <div className="bg-white border rounded p-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Quick Actions</h4>
            <div className="flex gap-2">
              {client.phone && (
                <a href={`tel:${client.phone}`} className="px-3 py-1 text-sm bg-emerald-600 text-white rounded">Call</a>
              )}
              {client.email && (
                <a href={`mailto:${client.email}`} className="px-3 py-1 text-sm bg-emerald-600 text-white rounded">Email</a>
              )}
              <button className="px-3 py-1 text-sm bg-emerald-600 text-white rounded" onClick={() => onLogCommunication && onLogCommunication('sms')}>Message</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


