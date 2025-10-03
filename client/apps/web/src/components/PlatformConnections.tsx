import React, { useEffect, useState } from 'react';
import { socialMediaApi, type Platform, type PlatformConnection } from '../services/socialMediaApi';

const PlatformConnections: React.FC = () => {
  const [connections, setConnections] = useState<PlatformConnection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    socialMediaApi.getConnections().then(setConnections).finally(() => setLoading(false));
  }, []);

  const toggle = async (p: Platform) => {
    setLoading(true);
    const current = connections.find(c => c.platform === p)?.connected;
    const updated = current ? await socialMediaApi.disconnect(p) : await socialMediaApi.connect(p);
    setConnections(prev => prev.map(c => c.platform === p ? updated : c));
    setLoading(false);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
      <div className="p-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-800">Platform Connections</h3>
        {loading && <div className="text-xs text-gray-500">Loading...</div>}
      </div>
      <div className="px-4 pb-4 grid grid-cols-1 md:grid-cols-3 gap-3">
        {connections.map(c => (
          <div key={c.platform} className="border rounded-lg p-3 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold capitalize">{c.platform}</div>
              <div className="text-xs text-gray-500">{c.accountName || 'Not connected'}</div>
            </div>
            <button onClick={() => toggle(c.platform)} className={`px-3 py-1 rounded-md text-xs font-medium ${c.connected ? 'bg-gray-100 text-gray-800' : 'bg-purple-600 text-white'}`}>
              {c.connected ? 'Disconnect' : 'Connect'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlatformConnections;
