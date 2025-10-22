import { useEffect, useRef, useState } from 'react';
import { Sparkles } from 'lucide-react';

export interface NotesEditorProps {
  initial?: string;
  onAutoSave?: (value: string) => void;
  onAIImprove?: (value: string) => void;
}

export default function NotesEditor({ initial = '', onAutoSave, onAIImprove }: NotesEditorProps) {
  const [value, setValue] = useState(initial);
  const timer = useRef<number | null>(null);

  useEffect(() => {
    // debounce autosave
    if (timer.current) window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => {
      onAutoSave?.(value);
    }, 600);
    return () => {
      if (timer.current) window.clearTimeout(timer.current);
    };
  }, [value]);

  return (
    <section className="bg-white rounded-2xl shadow-lg border border-gray-200 p-4 sm:p-5">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm font-semibold text-gray-900">Notes</p>
        <button
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-gray-200 bg-white hover:bg-gray-50 text-sm"
          onClick={() => onAIImprove?.(value)}
        >
          <Sparkles className="w-4 h-4 text-purple-600" />
          AI Improve
        </button>
      </div>
      <textarea
        className="w-full min-h-[140px] rounded-xl border border-gray-200 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-200"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Write notes..."
      />
      <p className="mt-2 text-xs text-gray-500">Autosaves as you type</p>
    </section>
  );
}

