import { motion } from 'framer-motion';
import { Loader2, CheckCircle2, Clock, AlertCircle } from 'lucide-react';
import { RequestStatus } from '../../store/commandStore';

interface RequestItemProps {
  title: string;
  status: RequestStatus;
  error?: string;
}

export function RequestItem({ title, status, error }: RequestItemProps) {
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
      className={`flex items-start justify-between px-3 py-2.5 rounded-lg ${config.bgColor} border ${config.borderColor} mb-2 hover:shadow-sm transition-shadow`}
    >
      <div className="flex items-start gap-2.5 flex-1 min-w-0">
        <Icon
          className={`w-4 h-4 flex-shrink-0 mt-0.5 ${
            status === 'Processing' ? 'animate-spin' : ''
          } ${config.color}`}
        />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-800 truncate">{title}</p>
          {error && (
            <p className="text-xs text-red-600 mt-1 line-clamp-2">{error}</p>
          )}
        </div>
      </div>
      <span
        className={`text-xs font-semibold ${config.color} ml-2 flex-shrink-0`}
      >
        {status}
      </span>
    </motion.div>
  );
}
