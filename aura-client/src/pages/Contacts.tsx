import { Users } from "lucide-react";

export default function Contacts() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-blue-50">
      <div className="max-w-4xl mx-auto px-4 py-16 sm:py-24">
        <div className="flex flex-col items-center text-center gap-6">
          <span className="inline-flex items-center justify-center rounded-2xl bg-emerald-100 text-emerald-600 p-4 shadow-sm">
            <Users className="h-8 w-8" />
          </span>
          <div className="space-y-2">
            <h1 className="text-3xl font-semibold text-gray-900">Contacts Workspace</h1>
            <p className="text-gray-500 max-w-2xl">
              AI-driven client management, smart segments, and outreach insights are in progress.
            </p>
          </div>
          <div className="w-full max-w-2xl">
            <div className="rounded-3xl border border-emerald-100 bg-gradient-to-br from-white/90 via-emerald-50/60 to-white/90 p-10 shadow-lg shadow-emerald-100/30">
              <h2 className="text-lg font-medium text-emerald-700">Coming in Phase 3.3</h2>
              <p className="mt-3 text-sm text-emerald-600 leading-relaxed">
                Track conversations, trigger AI follow-ups, and surface warm leads with proactive recommendations.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
