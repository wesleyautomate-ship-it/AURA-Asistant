/**
 * Error Dialog Component
 * ======================
 * 
 * User-friendly error display with actionable suggestions
 * Supports retry functionality and dismissal
 * 
 * Track 4 - Phase 3: Error Handling
 */

import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, X } from 'lucide-react';

export interface ErrorDialogProps {
  isOpen: boolean;
  error: string;
  onRetry?: () => void;
  onDismiss: () => void;
  suggestions?: string[];
}

export function ErrorDialog({
  isOpen,
  error,
  onRetry,
  onDismiss,
  suggestions = [],
}: ErrorDialogProps) {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm"
        onClick={onDismiss}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-white rounded-xl shadow-xl max-w-md w-full p-6"
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-50 rounded-lg">
                <AlertCircle className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">
                  Generation Failed
                </h3>
                <p className="text-sm text-gray-500">
                  We encountered an issue
                </p>
              </div>
            </div>
            <button
              onClick={onDismiss}
              className="p-1 hover:bg-gray-100 rounded-md transition-colors"
              aria-label="Close dialog"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          {/* Error Message */}
          <div className="mb-4 p-3 bg-red-50 rounded-lg border border-red-100">
            <p className="text-sm text-red-800">{error}</p>
          </div>

          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">
                Suggestions:
              </p>
              <ul className="space-y-1">
                {suggestions.map((suggestion, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                    <span className="text-blue-500 mt-0.5">•</span>
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            {onRetry && (
              <button
                onClick={onRetry}
                className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium shadow-sm"
              >
                Retry
              </button>
            )}
            <button
              onClick={onDismiss}
              className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
            >
              {onRetry ? 'Cancel' : 'Close'}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
