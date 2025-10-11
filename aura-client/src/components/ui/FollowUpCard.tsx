import { motion } from 'framer-motion';
import { X, Sparkles, ArrowRight } from 'lucide-react';
import { FollowUpSuggestion } from '../../services/followupAgent';

interface FollowUpCardProps {
  suggestion: FollowUpSuggestion | null;
  onAccept: () => void;
  onDismiss: () => void;
  isGenerating?: boolean;
  isExecuting?: boolean;
}
export default function FollowUpCard({ 
  suggestion, 
  onAccept, 
  onDismiss, 
  isGenerating = false,
  isExecuting = false 
}: FollowUpCardProps) {
  if (!suggestion) {
    return null;
  }
  
  const { message, confidence } = suggestion;
  const isLoading = isGenerating || isExecuting;
  
  // Color-coded confidence indicators
  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.8) return { dot: 'bg-green-500', text: 'text-green-600' };
    if (conf >= 0.6) return { dot: 'bg-yellow-500', text: 'text-yellow-600' };
    return { dot: 'bg-gray-400', text: 'text-gray-500' };
  };
  
  const confidenceColors = getConfidenceColor(confidence);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      transition={{ 
        type: 'spring', 
        damping: 25, 
        stiffness: 300,
        duration: 0.3 
      }}
      className="mt-4 p-4 rounded-2xl bg-gradient-to-r from-purple-50 via-blue-50 to-indigo-50 border border-blue-100 shadow-sm hover:shadow-md transition-all duration-200"
    >
      {/* Header with AI indicator */}
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg">
          <Sparkles className="w-3.5 h-3.5 text-white" />
        </div>
        <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">
          Smart Follow-up
        </span>
        <div className="flex-1" />
        <div className="flex items-center gap-1">
          <div className={`w-2 h-2 rounded-full ${confidenceColors.dot}`}></div>
          <span className={`text-xs font-medium ${confidenceColors.text}`}>
            {Math.round(confidence * 100)}% match
          </span>
        </div>
      </div>

      {/* Suggestion message */}
      <p className="text-sm font-medium text-gray-800 leading-relaxed mb-4">
        {message}
      </p>

      {/* Action buttons */}
      <div className="flex items-center gap-3">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onAccept}
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white text-sm font-medium rounded-xl transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              Processing...
            </>
          ) : (
            <>
              Continue
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => {
            console.log('[FollowUpCard] Dismiss button clicked');
            onDismiss();
          }}
          disabled={isLoading}
          className="p-2.5 bg-white hover:bg-gray-50 text-gray-400 hover:text-gray-600 rounded-xl border border-gray-200 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          title="✕ Dismiss suggestion"
        >
          <X className="w-4 h-4" />
        </motion.button>
      </div>

      {/* Optional: Intent preview */}
      {suggestion.actionData && (
        <div className="mt-3 pt-3 border-t border-blue-100">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>Intent:</span>
            <span className="font-medium text-blue-600">
              {suggestion.intent.replace('_', ' ')}
            </span>
            {suggestion.actionData.inferredLocation && (
              <>
                <span>•</span>
                <span>Location: {suggestion.actionData.inferredLocation}</span>
              </>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
}

/**
 * Loading state variant of the FollowUpCard for when suggestions are being generated
 */
export function FollowUpCardSkeleton() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-4 p-4 rounded-2xl bg-gradient-to-r from-gray-50 to-blue-50 border border-gray-200 shadow-sm"
    >
      <div className="flex items-center gap-2 mb-3">
        <div className="w-6 h-6 bg-gray-300 rounded-lg animate-pulse"></div>
        <div className="w-20 h-3 bg-gray-300 rounded animate-pulse"></div>
      </div>
      
      <div className="space-y-2 mb-4">
        <div className="w-full h-3 bg-gray-300 rounded animate-pulse"></div>
        <div className="w-3/4 h-3 bg-gray-300 rounded animate-pulse"></div>
      </div>

      <div className="flex gap-3">
        <div className="flex-1 h-9 bg-gray-300 rounded-xl animate-pulse"></div>
        <div className="w-9 h-9 bg-gray-300 rounded-xl animate-pulse"></div>
      </div>
    </motion.div>
  );
}