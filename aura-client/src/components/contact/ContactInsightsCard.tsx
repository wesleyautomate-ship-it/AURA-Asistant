import type { LeadTemperature } from '../../types/contacts';

interface ContactInsightsCardProps {
  temperature: LeadTemperature;
  intentScore?: number | null;
  signals?: string[] | null;
  risks?: string[] | null;
}

const tempChip: Record<LeadTemperature, string> = {
  Active: 'bg-green-100 text-green-700',
  New: 'bg-blue-100 text-blue-700',
  Warm: 'bg-amber-100 text-amber-700',
  Cold: 'bg-gray-100 text-gray-700',
  Dormant: 'bg-slate-100 text-slate-700',
};

export default function ContactInsightsCard({
  temperature,
  intentScore,
  signals,
  risks,
}: ContactInsightsCardProps) {
  const score = clampScore(intentScore);
  const chipClass = tempChip[temperature] ?? tempChip.Warm;
  const signalList = Array.isArray(signals) && signals.length ? signals : ['No recent signals available'];
  const riskList = Array.isArray(risks) && risks.length ? risks : ['No immediate risks detected'];

  return (
    <section className="bg-white rounded-2xl border border-gray-200 shadow-sm p-4 sm:p-5">
      <h2 className="text-sm font-semibold text-gray-900 mb-3">Insights</h2>
      <div className="space-y-5">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-3xl font-semibold text-gray-900">{score}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${chipClass}`}>{temperature}</span>
          </div>
          <div className="mt-3 h-2 w-full rounded-full bg-gray-100">
            <div
              className="h-2 rounded-full bg-gradient-to-r from-emerald-400 to-blue-500 transition-all"
              style={{ width: `${score}%` }}
            />
          </div>
        </div>

        <div>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Signals</p>
          <ul className="space-y-1.5 text-sm text-gray-700">
            {signalList.map((item, idx) => (
              <li key={`${item}-${idx}`} className="flex items-start gap-2">
                <span className="mt-1 h-1.5 w-1.5 rounded-full bg-emerald-400" aria-hidden="true" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Risks</p>
          <ul className="space-y-1.5 text-sm text-gray-700">
            {riskList.map((item, idx) => (
              <li key={`${item}-${idx}`} className="flex items-start gap-2">
                <span className="mt-1 h-1.5 w-1.5 rounded-full bg-amber-500" aria-hidden="true" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

function clampScore(intentScore?: number | null) {
  if (typeof intentScore !== 'number' || Number.isNaN(intentScore)) {
    return 0;
  }
  return Math.max(0, Math.min(100, Math.round(intentScore)));
}

