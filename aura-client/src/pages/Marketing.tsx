import { Megaphone } from "lucide-react";

export default function Marketing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-blue-50">
      <div className="max-w-4xl mx-auto px-4 py-16 sm:py-24">
        <div className="flex flex-col items-center text-center gap-6">
          <span className="inline-flex items-center justify-center rounded-2xl bg-blue-100 text-blue-600 p-4 shadow-sm">
            <Megaphone className="h-8 w-8" />
          </span>
          <div className="space-y-2">
            <h1 className="text-3xl font-semibold text-gray-900">Marketing Command Center</h1>
            <p className="text-gray-500 max-w-2xl">
              AI-powered campaign orchestration, smart channel scheduling, and on-brand asset libraries are on the way.
            </p>
          </div>
          <div className="w-full max-w-2xl">
            <div className="rounded-3xl border border-blue-100 bg-gradient-to-br from-white/90 via-blue-50/60 to-white/90 p-10 shadow-lg shadow-blue-100/30">
              <h2 className="text-lg font-medium text-blue-700">Coming in Phase 3.3</h2>
              <p className="mt-3 text-sm text-blue-600 leading-relaxed">
                Draft omni-channel campaigns, surface performance insights, and launch automated nurture flows without leaving Aura.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

