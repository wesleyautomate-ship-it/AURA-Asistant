import React from 'react';
import { Brain, CheckCircle, AlertTriangle, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Request, RequestStatus } from '../store/commandStore';

interface TaskTileProps {
  task: Request;
  hasIntelligenceContent?: boolean;
  enhanced?: boolean;
  exportReady?: boolean;
}

export default function TaskTile({ 
  task, 
  hasIntelligenceContent = false, 
  enhanced = false, 
  exportReady = false 
}: TaskTileProps) {
  const navigate = useNavigate();

  const getStatusIcon = (status: RequestStatus) => {
    switch (status) {
      case 'Complete':
        return enhanced ? 
          <Brain className="w-4 h-4 text-blue-600" /> : 
          <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'Processing':
        return <Loader2 className="w-4 h-4 text-orange-600 animate-spin" />;
      case 'Error':
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'Pending':
        return <div className="w-4 h-4 rounded-full bg-gray-300" />;
      default:
        return <div className="w-4 h-4 rounded-full bg-gray-300" />;
    }
  };

  const getStatusLabel = (status: RequestStatus) => {
    if (status === 'Complete') {
      if (enhanced) return 'AI Enhanced';
      if (exportReady) return 'Draft';
      return 'Complete';
    }
    return status;
  };

  const getStatusColor = (status: RequestStatus) => {
    if (status === 'Complete') {
      if (enhanced) return 'text-blue-600 bg-blue-50';
      if (exportReady) return 'text-green-600 bg-green-50';
      return 'text-green-600 bg-green-50';
    }
    switch (status) {
      case 'Processing':
        return 'text-orange-600 bg-orange-50';
      case 'Error':
        return 'text-red-600 bg-red-50';
      case 'Pending':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  const handleClick = () => {
    if (hasIntelligenceContent && task.status === 'Complete') {
      navigate(`/content/${task.id}`);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
      onClick={handleClick}
      className={`
        bg-white rounded-lg p-4 border border-gray-100 transition-all
        ${hasIntelligenceContent && task.status === 'Complete' 
          ? 'cursor-pointer hover:border-gray-200 hover:shadow-sm' 
          : 'cursor-default'
        }
      `}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            {getStatusIcon(task.status)}
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
              {getStatusLabel(task.status)}
            </span>
          </div>
          
          <h3 className="font-medium text-gray-900 text-sm mb-1 truncate">
            {task.title}
          </h3>
          
          <p className="text-xs text-gray-500">
            {formatTimestamp(task.timestamp)}
          </p>
          
          {task.error && (
            <p className="text-xs text-red-600 mt-2 truncate">
              {task.error}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
}