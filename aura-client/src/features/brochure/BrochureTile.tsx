import { useState } from 'react';
import { FileText, Loader2, Download } from 'lucide-react';
import { createBrochure, type BrochureResult } from '../../api/documents';
import { useCommandStore } from '../../store/commandStore';

export default function BrochureTile() {
  const { addRequest, updateRequestStatus } = useCommandStore();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BrochureResult | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (loading) return;
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    setResult(null);

    const reqId = addRequest('Property Brochure', 'PROPERTY_BROCHURE');
    try {
      const res = await createBrochure({ title: 'Property Brochure' });
      setResult(res);
      setSuccessMsg('Brochure generated');
      updateRequestStatus(reqId, 'Complete');
    } catch (err) {
      console.error('[BrochureTile] Generate failed', err);
      setErrorMsg('Failed to generate brochure');
      updateRequestStatus(reqId, 'Error', 'Failed to generate brochure');
    } finally {
      setLoading(false);
      // Auto-hide success message after a short delay
      setTimeout(() => setSuccessMsg(null), 2500);
    }
  };

  return (
    <div className="w-full">
      <div className="aspect-[4/3] p-3 sm:p-6 rounded-2xl bg-white shadow-md hover:shadow-xl transition-shadow flex flex-col justify-between border border-gray-100">
        <div className="space-y-2">
          <div className="flex items-start justify-between sm:justify-start sm:gap-2">
            <div className="mx-auto sm:mx-0">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="space-y-1">
            <h3 className="font-semibold text-sm sm:text-lg text-gray-900">Brochure</h3>
            <p className="text-gray-600 text-xs sm:text-sm leading-relaxed">
              Generate a simple property brochure from mock data.
            </p>
          </div>
          {successMsg && (
            <div className="rounded bg-green-50 text-green-700 text-xs px-2 py-1 inline-block">{successMsg}</div>
          )}
          {errorMsg && (
            <div className="rounded bg-red-50 text-red-700 text-xs px-2 py-1 inline-block">{errorMsg}</div>
          )}
        </div>

        <div className="mt-3 flex items-center justify-between gap-3">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-wait disabled:bg-blue-300"
          >
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
            Generate brochure
          </button>
          {result?.file_url && (
            <a
              href={result.file_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
              title="Download brochure"
            >
              <Download className="w-4 h-4" />
              Download
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

