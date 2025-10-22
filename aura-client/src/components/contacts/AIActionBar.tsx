import { MessageSquare, FileText, Lightbulb, Sparkles, Calendar } from 'lucide-react';

export interface AIActionBarProps {
  onGenerateFollowUp?: () => void;
  onScheduleFollowUp?: () => void;
  onSummarizeNotes?: () => void;
  onRecommendProperties?: () => void;
  onNextBestAction?: () => void;
  isProcessing?: boolean;
}

export default function AIActionBar({
  onGenerateFollowUp = () => console.warn('onGenerateFollowUp not implemented'),
  onScheduleFollowUp = () => console.warn('onScheduleFollowUp not implemented'),
  onSummarizeNotes = () => console.warn('onSummarizeNotes not implemented'),
  onRecommendProperties = () => console.warn('onRecommendProperties not implemented'),
  onNextBestAction = () => console.warn('onNextBestAction not implemented'),
  isProcessing = false,
}: AIActionBarProps) {
  const base =
    'flex items-center gap-2 px-3 py-2 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 active:scale-95 transition shadow-sm text-sm disabled:opacity-50 disabled:cursor-not-allowed';

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-3 sm:p-4">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
        <div className="flex items-center gap-2">
          <button className={base} onClick={onGenerateFollowUp} disabled={isProcessing}>
            <MessageSquare className="w-4 h-4 text-blue-600" />
            <span>Follow-Up</span>
          </button>
          <button
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 active:scale-95 transition shadow-sm text-sm"
            onClick={onScheduleFollowUp}
            disabled={isProcessing}
          >
            <Calendar className="w-4 h-4 text-emerald-600" />
            <span className="hidden sm:inline">Schedule Follow-Up</span>
            <span className="sm:hidden">Schedule</span>
          </button>
        </div>
        <button className={base} onClick={onSummarizeNotes} disabled={isProcessing}>
          <FileText className="w-4 h-4 text-emerald-600" />
          <span>Summarize Notes</span>
        </button>
        <button className={base} onClick={onRecommendProperties} disabled={isProcessing}>
          <Sparkles className="w-4 h-4 text-purple-600" />
          <span>Recommend Properties</span>
        </button>
        <button className={base} onClick={onNextBestAction} disabled={isProcessing}>
          <Lightbulb className="w-4 h-4 text-amber-600" />
          <span>Next Best Action</span>
        </button>
      </div>
    </div>
  );
}
