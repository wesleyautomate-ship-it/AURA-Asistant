import { useCommandStore, RequestType } from '../store/commandStore';
import { CheckCircle, Loader2, AlertCircle, Clock, ArrowLeft, ClipboardList, Download } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useState } from 'react';

export default function RequestsPage() {
  const { requests } = useCommandStore();
  const [filter, setFilter] = useState<RequestType | 'ALL'>('ALL');

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Complete':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'Processing':
        return <Loader2 className="w-5 h-5 animate-spin text-blue-500" />;
      case 'Error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'Pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Complete':
        return 'border-green-200 bg-green-50';
      case 'Processing':
        return 'border-blue-200 bg-blue-50';
      case 'Error':
        return 'border-red-200 bg-red-50';
      case 'Pending':
        return 'border-gray-200 bg-gray-50';
      default:
        return 'border-gray-200 bg-white';
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

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 pb-24 sm:pb-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        {/* Header */}
        <header className="space-y-4">
          <Link 
            to="/" 
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">AI Requests</h1>
            <p className="text-gray-600 mt-2 text-sm sm:text-base">
              Track your recent AI-generated actions, reports, and content.
            </p>
          </div>
        </header>

        {/* Filter Buttons */}
        <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
          {(['ALL', 'CMA', 'MARKET_REPORT', 'SOCIAL_POST', 'GENERIC'] as const).map((filterType) => (
            <button
              key={filterType}
              onClick={() => setFilter(filterType)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                filter === filterType
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-white text-gray-600 border border-gray-200 hover:border-blue-300 hover:text-blue-600'
              }`}
            >
              {filterType === 'ALL' ? 'All Tasks' : filterType.replace('_', ' ')}
            </button>
          ))}
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <p className="text-gray-600 text-xs sm:text-sm font-medium">Total</p>
            <p className="text-2xl sm:text-3xl font-bold text-gray-900 mt-1">{requests.length}</p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <p className="text-gray-600 text-xs sm:text-sm font-medium">Complete</p>
            <p className="text-2xl sm:text-3xl font-bold text-green-600 mt-1">
              {requests.filter(r => r.status === 'Complete').length}
            </p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <p className="text-gray-600 text-xs sm:text-sm font-medium">Processing</p>
            <p className="text-2xl sm:text-3xl font-bold text-blue-600 mt-1">
              {requests.filter(r => r.status === 'Processing').length}
            </p>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <p className="text-gray-600 text-xs sm:text-sm font-medium">Errors</p>
            <p className="text-2xl sm:text-3xl font-bold text-red-600 mt-1">
              {requests.filter(r => r.status === 'Error').length}
            </p>
          </div>
        </div>

        {/* Requests List */}
        <div className="space-y-3">
          {(() => {
            const filteredRequests = filter === 'ALL' 
              ? requests 
              : requests.filter(r => r.type === filter);
            
            if (requests.length === 0) {
              return (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl p-8 sm:p-12 text-center shadow-sm border border-gray-100"
            >
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ClipboardList className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No AI tasks yet</h3>
              <p className="text-gray-600 text-sm max-w-md mx-auto">
                Start by opening Aura Command Center and creating your first AI request.
                All your tasks will appear here.
              </p>
            </motion.div>
              );
            }
            
            if (filteredRequests.length === 0) {
              return (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-xl p-8 sm:p-12 text-center shadow-sm border border-gray-100"
                >
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <ClipboardList className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No {filter} tasks yet</h3>
                  <p className="text-gray-600 text-sm max-w-md mx-auto">
                    Tasks of this type will appear here when created.
                  </p>
                </motion.div>
              );
            }
            
            return (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-3"
              >
                {filteredRequests.map((req, index) => (
                <motion.div
                  key={req.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`p-4 sm:p-5 rounded-xl shadow-sm border-2 transition-all hover:shadow-md ${getStatusColor(req.status)}`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        {getStatusIcon(req.status)}
                        <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">
                          {req.status}
                        </span>
                      </div>
                      <h2 className="font-semibold text-gray-900 text-sm sm:text-base mb-1 line-clamp-2">
                        {req.title}
                      </h2>
                      <p className="text-xs sm:text-sm text-gray-500">
                        {formatTimestamp(req.timestamp)}
                      </p>
                      {req.error && (
                        <p className="mt-2 text-xs text-red-600 bg-red-50 rounded px-2 py-1 border border-red-200">
                          Error: {req.error}
                        </p>
                      )}
                      {/* CMA Report Download Link */}
                      {req.type === 'CMA' && req.metadata?.report_url && req.status === 'Complete' && (
                        <a
                          href={req.metadata.report_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-3 inline-flex items-center gap-2 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg text-xs font-medium hover:bg-blue-100 transition-colors border border-blue-200"
                        >
                          <Download className="w-4 h-4" />
                          Download CMA Report
                        </a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
            );
          })()}
        </div>
      </div>
    </div>
  );
}
