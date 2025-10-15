import { Home } from "lucide-react";

export default function Properties() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-blue-50">
      <div className="max-w-4xl mx-auto px-4 py-16 sm:py-24">
        <div className="flex flex-col items-center text-center gap-6">
          <span className="inline-flex items-center justify-center rounded-2xl bg-indigo-100 text-indigo-600 p-4 shadow-sm">
            <Home className="h-8 w-8" />
          </span>
          <div className="space-y-2">
            <h1 className="text-3xl font-semibold text-gray-900">Property Portfolio</h1>
            <p className="text-gray-500 max-w-2xl">
              Listing intelligence, brochure automation, and pipeline analytics will land here soon.
            </p>
          </div>
          <div className="w-full max-w-2xl">
            <div className="rounded-3xl border border-indigo-100 bg-gradient-to-br from-white/90 via-indigo-50/60 to-white/90 p-10 shadow-lg shadow-indigo-100/30">
              <h2 className="text-lg font-medium text-indigo-700">Coming in Phase 3.3</h2>
              <p className="mt-3 text-sm text-indigo-600 leading-relaxed">
                Manage active listings, sync property data, and launch AI-ready marketing assets from a single command center.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
