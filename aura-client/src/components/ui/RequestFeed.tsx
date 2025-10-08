import { AnimatePresence, motion } from 'framer-motion';
import { RequestItem } from './RequestItem';
import { Request } from '../../store/commandStore';
import { Activity } from 'lucide-react';

interface RequestFeedProps {
  requests: Request[];
}

export default function RequestFeed({ requests }: RequestFeedProps) {
  if (requests.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="mt-6 pt-4 border-t border-gray-200 w-full"
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <Activity className="w-4 h-4 text-blue-500" />
        <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
          AI Tasks
        </p>
        <div className="flex-1 h-px bg-gradient-to-r from-gray-200 to-transparent"></div>
        <span className="text-xs text-gray-500 font-medium">
          {requests.length} {requests.length === 1 ? 'task' : 'tasks'}
        </span>
      </div>

      {/* Scrollable Feed */}
      <div className="max-h-[280px] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
        <AnimatePresence mode="popLayout">
          {requests.map((request) => (
            <RequestItem
              key={request.id}
              title={request.title}
              status={request.status}
              error={request.error}
            />
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
