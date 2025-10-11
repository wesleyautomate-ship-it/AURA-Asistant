/**
 * Progress Tracker Component
 * ===========================
 * 
 * Shows real-time pipeline progress with step indicators
 * Displays current step, percentage, and status
 * 
 * Track 4.1 - Progress Indicators
 */

import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Loader2, AlertCircle } from 'lucide-react';

export interface ProgressStep {
  id: string;
  label: string;
  description: string;
  percentage: number;
}

export interface ProgressTrackerProps {
  currentStep: string;
  progress: number;
  status: 'processing' | 'success' | 'error' | 'idle';
  error?: string;
  steps?: ProgressStep[];
}

const DEFAULT_STEPS: ProgressStep[] = [
  {
    id: 'normalizing',
    label: 'Understanding',
    description: 'Analyzing your request...',
    percentage: 20,
  },
  {
    id: 'validating',
    label: 'Validating',
    description: 'Checking parameters...',
    percentage: 40,
  },
  {
    id: 'enriching',
    label: 'Enriching',
    description: 'Auto-filling details...',
    percentage: 60,
  },
  {
    id: 'generating',
    label: 'Generating',
    description: 'Creating content...',
    percentage: 80,
  },
  {
    id: 'saving',
    label: 'Saving',
    description: 'Finalizing...',
    percentage: 90,
  },
  {
    id: 'completed',
    label: 'Complete',
    description: 'All done!',
    percentage: 100,
  },
];

export function ProgressTracker({
  currentStep,
  progress,
  status,
  error,
  steps = DEFAULT_STEPS,
}: ProgressTrackerProps) {
  // Find current step index
  const currentStepIndex = steps.findIndex(step => step.id === currentStep);
  const currentStepData = steps[currentStepIndex] || steps[0];

  return (
    <div className="w-full bg-white rounded-xl border border-gray-200 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {status === 'processing' && (
            <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
          )}
          {status === 'success' && (
            <CheckCircle2 className="w-4 h-4 text-green-500" />
          )}
          {status === 'error' && (
            <AlertCircle className="w-4 h-4 text-red-500" />
          )}
          {status === 'idle' && (
            <Circle className="w-4 h-4 text-gray-400" />
          )}
          
          <div>
            <h3 className="text-sm font-medium text-gray-900">
              {currentStepData.label}
            </h3>
            <p className="text-xs text-gray-500">
              {error || currentStepData.description}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <p className="text-lg font-semibold text-gray-900">
            {progress}%
          </p>
          <p className="text-[10px] text-gray-400">
            Step {currentStepIndex + 1}/{steps.length}
          </p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="relative h-2 bg-gray-100 rounded-full overflow-hidden mb-4">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className={`absolute inset-y-0 left-0 rounded-full ${
            status === 'error' ? 'bg-red-500' :
            status === 'success' ? 'bg-green-500' :
            'bg-gradient-to-r from-blue-500 to-purple-500'
          }`}
        />
        {status === 'processing' && (
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: '200%' }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: 'linear',
            }}
            className="absolute inset-0 w-1/3 bg-gradient-to-r from-transparent via-white/30 to-transparent"
          />
        )}
      </div>

      {/* Step Indicators */}
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isComplete = index < currentStepIndex || status === 'success';
          const isCurrent = index === currentStepIndex;
          const isError = status === 'error' && isCurrent;

          return (
            <div
              key={step.id}
              className="flex flex-col items-center gap-1 flex-1"
            >
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium transition-all ${
                  isError
                    ? 'bg-red-500 text-white'
                    : isComplete
                    ? 'bg-green-500 text-white'
                    : isCurrent
                    ? 'bg-blue-500 text-white animate-pulse'
                    : 'bg-gray-200 text-gray-400'
                }`}
              >
                {isError ? '!' : isComplete ? '✓' : index + 1}
              </div>
              <span className={`text-[10px] text-center ${
                isCurrent ? 'text-gray-900 font-medium' : 'text-gray-400'
              }`}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * Compact Progress Bar (for inline use)
 */
export function CompactProgressBar({
  progress,
  status,
}: Pick<ProgressTrackerProps, 'progress' | 'status'>) {
  return (
    <div className="relative h-1 bg-gray-100 rounded-full overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ duration: 0.3 }}
        className={`absolute inset-y-0 left-0 rounded-full ${
          status === 'error' ? 'bg-red-500' :
          status === 'success' ? 'bg-green-500' :
          'bg-blue-500'
        }`}
      />
    </div>
  );
}

/**
 * Progress Badge (for request tiles)
 */
export function ProgressBadge({
  progress,
  status,
}: Pick<ProgressTrackerProps, 'progress' | 'status'>) {
  return (
    <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${
      status === 'error' ? 'bg-red-50 text-red-700' :
      status === 'success' ? 'bg-green-50 text-green-700' :
      status === 'processing' ? 'bg-blue-50 text-blue-700' :
      'bg-gray-50 text-gray-600'
    }`}>
      {status === 'processing' && <Loader2 className="w-3 h-3 animate-spin" />}
      {status === 'success' && <CheckCircle2 className="w-3 h-3" />}
      {status === 'error' && <AlertCircle className="w-3 h-3" />}
      <span>{progress}%</span>
    </div>
  );
}
