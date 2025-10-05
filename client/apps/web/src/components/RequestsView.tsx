import React, { useEffect, useState, useCallback } from 'react';
import ViewHeader from './ViewHeader';
import RequestCard from './RequestCard';
import { useAIRequestStore, selectAllRequests, selectLoading, selectError, selectCounts } from '@/store';
import { Request } from '@/types';

interface RevisionModalProps {
  request: Request;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (instructions: string) => void;
}

const RevisionModal: React.FC<RevisionModalProps> = ({ request, isOpen, onClose, onSubmit }) => {
  const [instructions, setInstructions] = useState('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (instructions.trim()) {
      onSubmit(instructions.trim());
      setInstructions('');
      onClose();
    }
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Request Revision</h3>
        <p className="text-sm text-gray-600 mb-4">
          Provide instructions for revising: {request.title}
        </p>
        <form onSubmit={handleSubmit}>
          <textarea
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="Please provide specific instructions for the revision..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            rows={4}
            required
          />
          <div className="flex justify-end gap-3 mt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!instructions.trim()}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Request Revision
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const SkeletonCard: React.FC = () => (
  <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm animate-pulse">
    <div className="flex space-x-4">
      <div className="w-24 h-24 bg-gray-200 rounded-lg" />
      <div className="flex-grow">
        <div className="flex items-center justify-between mb-2">
          <div className="w-20 h-4 bg-gray-200 rounded" />
          <div className="w-16 h-4 bg-gray-200 rounded" />
        </div>
        <div className="w-3/4 h-5 bg-gray-200 rounded mb-3" />
        <div className="w-full h-2 bg-gray-200 rounded mb-2" />
        <div className="flex justify-between items-center">
          <div className="w-24 h-4 bg-gray-200 rounded" />
          <div className="w-8 h-8 bg-gray-200 rounded-full" />
        </div>
      </div>
    </div>
  </div>
);

const EmptyState: React.FC<{ onRetry: () => void }> = ({ onRetry }) => (
  <div className="flex flex-col items-center justify-center py-12 px-4">
    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
      <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    </div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">No requests yet</h3>
    <p className="text-gray-500 text-center mb-4">
      Create your first AI request using the Command Center
    </p>
    <button
      onClick={onRetry}
      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
    >
      Refresh
    </button>
  </div>
);

const ErrorState: React.FC<{ error: string; onRetry: () => void }> = ({ error, onRetry }) => (
  <div className="flex flex-col items-center justify-center py-12 px-4">
    <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
      <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">Something went wrong</h3>
    <p className="text-gray-500 text-center mb-4 max-w-md">
      {error}
    </p>
    <button
      onClick={onRetry}
      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
    >
      Try Again
    </button>
  </div>
);

const RequestsView: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<Request['status'] | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [revisionModal, setRevisionModal] = useState<{ request: Request; isOpen: boolean } | null>(null);
  
  const requests = useAIRequestStore(selectAllRequests);
  const loading = useAIRequestStore(selectLoading);
  const error = useAIRequestStore(selectError);
  const counts = useAIRequestStore(selectCounts);
  
  const fetchAll = useAIRequestStore(state => state.fetchAll);
  const approve = useAIRequestStore(state => state.approve);
  const revise = useAIRequestStore(state => state.revise);
  const clearError = useAIRequestStore(state => state.clearError);
  
  // Load requests on mount
  useEffect(() => {
    fetchAll();
    
    // Cleanup subscriptions on unmount
    return () => {
      useAIRequestStore.getState().unsubscribeAll();
    };
  }, [fetchAll]);
  
  // Filter requests
  const filteredRequests = React.useMemo(() => {
    let filtered = requests;
    
    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(request => request.status === statusFilter);
    }
    
    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(request => 
        request.title.toLowerCase().includes(query) ||
        request.description.toLowerCase().includes(query) ||
        request.category.toLowerCase().includes(query)
      );
    }
    
    return filtered;
  }, [requests, statusFilter, searchQuery]);
  
  const handleRetry = useCallback(() => {
    clearError();
    fetchAll();
  }, [clearError, fetchAll]);
  
  const handleRequestClick = useCallback((request: Request) => {
    // Show request details or actions
    console.log('Request clicked:', request);
  }, []);
  
  const handleApprove = useCallback(async (request: Request) => {
    try {
      await approve(request.id);
    } catch (error) {
      console.error('Failed to approve request:', error);
    }
  }, [approve]);
  
  const handleRevise = useCallback((request: Request) => {
    setRevisionModal({ request, isOpen: true });
  }, []);
  
  const handleRevisionSubmit = useCallback(async (instructions: string) => {
    if (!revisionModal) return;
    
    try {
      await revise(revisionModal.request.id, instructions);
    } catch (error) {
      console.error('Failed to request revision:', error);
    }
  }, [revise, revisionModal]);
  
  const statusOptions: Array<{ value: Request['status'] | 'all'; label: string; count?: number }> = [
    { value: 'all', label: 'All', count: counts.total },
    { value: 'Queued', label: 'Queued', count: counts.queued },
    { value: 'Processing', label: 'Processing', count: counts.processing },
    { value: 'Ready for Review', label: 'Ready for Review', count: counts.draft_ready + counts.approved },
  ];
  
  return (
    <div className="flex flex-col h-full bg-gray-50">
      <ViewHeader title="AI Requests" />
      
      {/* Filters */}
      <div className="px-6 py-4 bg-white border-b border-gray-200">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          {/* Search */}
          <div className="relative flex-1 max-w-sm">
            <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search requests..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          {/* Status filter */}
          <div className="flex gap-2 overflow-x-auto">
            {statusOptions.map(option => (
              <button
                key={option.value}
                onClick={() => setStatusFilter(option.value)}
                className={`px-3 py-2 text-xs font-medium rounded-full whitespace-nowrap transition-colors ${
                  statusFilter === option.value
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {option.label}
                {option.count !== undefined && (
                  <span className="ml-1 opacity-75">({option.count})</span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      <main className="flex-1 overflow-y-auto px-6 pt-4 pb-28">
        {error ? (
          <ErrorState error={error} onRetry={handleRetry} />
        ) : loading ? (
          <div className="space-y-4">
            {Array.from({ length: 3 }, (_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        ) : filteredRequests.length === 0 ? (
          <EmptyState onRetry={handleRetry} />
        ) : (
          <div className="space-y-4">
            {filteredRequests.map(request => (
              <div key={request.id} className="relative">
                <RequestCard 
                  request={request} 
                  onClick={handleRequestClick}
                />
                
                {/* Action buttons for Ready for Review requests */}
                {request.status === 'Ready for Review' && (
                  <div className="absolute top-4 right-4 flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRevise(request);
                      }}
                      className="px-3 py-1 text-xs font-medium text-orange-700 bg-orange-100 rounded-full hover:bg-orange-200 transition-colors"
                    >
                      Revise
                    </button>
                    {request.progress >= 95 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleApprove(request);
                        }}
                        className="px-3 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full hover:bg-green-200 transition-colors"
                      >
                        Approve
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
      
      {/* Revision Modal */}
      {revisionModal && (
        <RevisionModal
          request={revisionModal.request}
          isOpen={revisionModal.isOpen}
          onClose={() => setRevisionModal(null)}
          onSubmit={handleRevisionSubmit}
        />
      )}
    </div>
  );
};

export default RequestsView;
