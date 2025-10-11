import { motion } from 'framer-motion';
import { Loader2, CheckCircle2, Clock, AlertCircle, RefreshCw, AlertTriangle } from 'lucide-react';
import { useCommandStore, type Request } from '../../store/commandStore';
import { getTaskAge, isRetryableStatus, isTaskStale } from '../../config/taskLifecycle';

interface RequestItemProps {
  request: Request;
}

export function RequestItem({ request }: RequestItemProps) {
  const { retryTask } = useCommandStore();
  const { title, status, error, timestamp, id } = request;
  
  const handleRetry = async () => {
    console.log(`[RequestItem] Retrying task: ${title}`);
    try {
      await retryTask(id);
    } catch (err) {
      console.error('[RequestItem] Retry failed:', err);
    }
  };
  
  // Calculate task age and staleness
  const taskAge = getTaskAge(timestamp);
  const isStale = isTaskStale(timestamp, status);
  const canRetry = isRetryableStatus(status);
  
  // Format age for display
  const formatAge = (age: number): string => {
    const minutes = Math.floor(age / 60000);
    const seconds = Math.floor((age % 60000) / 1000);
    if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    }
    return `${seconds}s`;
  };
  const statusConfig = {
    Pending: {
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      icon: Clock,
    },
    Processing: {
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      icon: Loader2,
    },
    Complete: {
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      icon: CheckCircle2,
    },
    Error: {
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      icon: AlertCircle,
    },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`px-3 py-2.5 rounded-lg ${config.bgColor} border ${config.borderColor} mb-2 hover:shadow-sm transition-shadow ${
        isStale ? 'ring-2 ring-yellow-200' : ''
      }`}
    >
      {/* Main content */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-2.5 flex-1 min-w-0">
          <Icon
            className={`w-4 h-4 flex-shrink-0 mt-0.5 ${
              status === 'Processing' ? 'animate-spin' : ''
            } ${config.color}`}
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium text-gray-800 truncate">{title}</p>
              {isStale && (
                <div title="Task is stale">
                  <AlertTriangle className="w-3 h-3 text-yellow-600 flex-shrink-0" />
                </div>
              )}
            </div>
            {error && (
              <div className="text-red-600 text-xs mt-1 flex items-center gap-1">
                <AlertTriangle className="w-3 h-3 flex-shrink-0" />
                <span className="line-clamp-2">{error}</span>
              </div>
            )}
            
            {/* Task age and metadata */}
            <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
              <span>Age: {formatAge(taskAge)}</span>
              {request.type && request.type !== 'GENERIC' && (
                <span className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">
                  {request.type}
                </span>
              )}
              {request.parentId && (
                <span className="text-blue-600">🔗 Linked</span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2 ml-2 flex-shrink-0">
          <span className={`text-xs font-semibold ${config.color}`}>
            {status}
          </span>
        </div>
      </div>
      
      {/* Retry button for error states */}
      {canRetry && (
        <div className="mt-2 pt-2 border-t border-gray-200">
          <button
            onClick={handleRetry}
            className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
            title="Retry this task"
          >
            <RefreshCw className="w-3 h-3" />
            Retry Task
          </button>
        </div>
      )}
    </motion.div>
  );
}
