import { useCommandStore, RequestType } from '../store/commandStore';
import { ArrowLeft, ClipboardList } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import TaskTile from '../components/TaskTile';

export default function RequestsPage() {
  const { requests, getIntelligenceContentByTaskId } = useCommandStore();
  const [filter, setFilter] = useState<RequestType | 'ALL'>('ALL');

  const hasIntelligenceContent = (taskId: string) => {
    const intelligenceContent = getIntelligenceContentByTaskId(taskId);
    return intelligenceContent !== undefined;
  };
  
  const getIntelligenceContentData = (taskId: string) => {
    const content = getIntelligenceContentByTaskId(taskId);
    if (!content) return { enhanced: false, exportReady: false };
    
    return {
      enhanced: content.enhanced,
      exportReady: content.exportReady
    };
  };

  return (
    <div className="w-full min-h-screen bg-white">
      <div className="max-w-6xl mx-auto px-6 py-6">
        {/* Header */}
        <header className="mb-8">
          <Link 
            to="/" 
            className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 transition-colors font-medium mb-6"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Tasks</h1>
            <p className="text-gray-600 mt-1">
              Your AI-generated content and requests
            </p>
          </div>
        </header>

        {/* Filter Buttons */}
        <div className="flex flex-wrap gap-2 mb-6">
          {(['ALL', 'CMA', 'CMA_REPORT', 'PITCH_DECK', 'MARKET_REPORT', 'SOCIAL_POST', 'GENERIC'] as const).map((filterType) => (
            <button
              key={filterType}
              onClick={() => setFilter(filterType)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === filterType
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {filterType === 'ALL' ? 'All' : filterType.replace('_', ' ')}
            </button>
          ))}
        </div>

        {/* Tasks Grid */}
        <div className="space-y-4">
          {(() => {
            const filteredRequests = filter === 'ALL' 
              ? requests 
              : requests.filter(r => r.type === filter);
            
            if (requests.length === 0) {
              return (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-12"
                >
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <ClipboardList className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No tasks yet</h3>
                  <p className="text-gray-600 text-sm">
                    Start by creating your first AI request in the command center.
                  </p>
                </motion.div>
              );
            }
            
            if (filteredRequests.length === 0) {
              return (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-12"
                >
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <ClipboardList className="w-8 h-8 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No {filter.toLowerCase()} tasks</h3>
                  <p className="text-gray-600 text-sm">
                    Tasks of this type will appear here when created.
                  </p>
                </motion.div>
              );
            }
            
            return (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
              >
                {filteredRequests.map((req, index) => {
                  const hasIntel = hasIntelligenceContent(req.id);
                  const intelData = hasIntel ? getIntelligenceContentData(req.id) : { enhanced: false, exportReady: false };
                  
                  return (
                    <TaskTile
                      key={req.id}
                      task={req}
                      hasIntelligenceContent={hasIntel}
                      enhanced={intelData.enhanced}
                      exportReady={intelData.exportReady}
                    />
                  );
                })}
              </motion.div>
            );
          })()}
        </div>
      </div>
    </div>
  );
}
