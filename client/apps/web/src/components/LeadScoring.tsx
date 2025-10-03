import React from 'react';

interface LeadScoringProps {
  score?: number;
}

export default function LeadScoring({ score }: LeadScoringProps) {
  const value = typeof score === 'number' ? score : 0;
  const color = value >= 80 ? 'bg-emerald-600' : value >= 60 ? 'bg-yellow-500' : 'bg-red-500';
  const labelColor = value >= 80 ? 'text-emerald-700' : value >= 60 ? 'text-yellow-700' : 'text-red-700';

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-500">Lead Score</span>
        <span className={`text-xs font-medium ${labelColor}`}>{value}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full`} style={{ width: `${Math.min(Math.max(value, 0), 100)}%` }}></div>
      </div>
    </div>
  );
}


