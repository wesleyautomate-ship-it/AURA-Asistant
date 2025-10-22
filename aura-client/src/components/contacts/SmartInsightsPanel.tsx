export interface SmartInsightsPanelProps {
  intentScore?: number; // 0..100
  signals?: string[];
  flags?: string[];
}

export default function SmartInsightsPanel({ intentScore = 62, signals = [], flags = [] }: SmartInsightsPanelProps) {
  const bucket = intentScore >= 75 ? 'Hot' : intentScore >= 45 ? 'Warm' : 'Cold';
  const chipClass = bucket === 'Hot'
    ? 'bg-red-100 text-red-700'
    : bucket === 'Warm'
    ? 'bg-amber-100 text-amber-700'
    : 'bg-gray-100 text-gray-700';

  const defaultSignals = signals.length ? signals : [
    'Engaged with waterfront listings last week',
    'Opened brochure email twice in 24h',
  ];
  const defaultFlags = flags.length ? flags : [
    'Dormant 14 days',
  ];

  return (
    <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 p-4">
          <p className="text-sm text-gray-600">Intent Score</p>
          <div className="mt-2 flex items-center gap-2">
            <span className="text-2xl font-semibold text-gray-900">{intentScore}</span>
            <span className={`text-xs px-2 py-1 rounded-full ${chipClass}`}>{bucket}</span>
          </div>
          <div className="mt-3 w-full h-2 rounded-full bg-gray-100">
            <div className="h-2 rounded-full bg-gradient-to-r from-emerald-400 to-blue-500" style={{ width: `${intentScore}%` }} />
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 p-4">
          <p className="text-sm font-semibold text-gray-900 mb-2">Signals</p>
          <ul className="text-sm text-gray-700 space-y-1.5">
            {defaultSignals.map((s, i) => <li key={i}>• {s}</li>)}
          </ul>
        </div>

        <div className="rounded-xl border border-gray-200 p-4">
          <p className="text-sm font-semibold text-gray-900 mb-2">Risk / Opportunities</p>
          <ul className="text-sm text-gray-700 space-y-1.5">
            {defaultFlags.map((f, i) => <li key={i}>• {f}</li>)}
          </ul>
        </div>
      </div>
    </section>
  );
}

