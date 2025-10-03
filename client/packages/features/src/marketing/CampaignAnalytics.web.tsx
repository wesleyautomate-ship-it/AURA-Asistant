import React from 'react';

interface MetricCardProps {
  label: string;
  value: string;
  delta?: string;
  color?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, delta, color = '#0891b2' }) => (
  <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
    <div className="text-xs text-gray-500 mb-1">{label}</div>
    <div className="text-2xl font-bold" style={{color}}>{value}</div>
    {delta && <div className="text-xs text-gray-500 mt-1">{delta} vs. last campaign</div>}
  </div>
);

interface CampaignAnalyticsProps {
  stats?: {
    opens?: number;
    clicks?: number;
    conversions?: number;
    reach?: number;
  };
}

const CampaignAnalytics: React.FC<CampaignAnalyticsProps> = ({ stats }) => {
  const s = {
    opens: stats?.opens ?? 1240,
    clicks: stats?.clicks ?? 220,
    conversions: stats?.conversions ?? 14,
    reach: stats?.reach ?? 5200,
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm">
      <div className="p-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-800">Campaign Performance</h3>
        <div className="text-xs text-gray-500">Sample metrics (stubbed)</div>
      </div>
      <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-3">
        <MetricCard label="Email Opens" value={`${s.opens.toLocaleString()}`} color="#7c3aed" delta="+12%" />
        <MetricCard label="Link Clicks" value={`${s.clicks.toLocaleString()}`} color="#2563eb" delta="+8%" />
        <MetricCard label="Conversions" value={`${s.conversions.toLocaleString()}`} color="#059669" delta="+3%" />
        <MetricCard label="Social Reach" value={`${s.reach.toLocaleString()}`} color="#ef4444" delta="+5%" />
      </div>
    </div>
  );
};

export default CampaignAnalytics;
