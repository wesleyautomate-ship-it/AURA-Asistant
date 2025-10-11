import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCommandStore, IntelligenceContent } from '../store/commandStore';
import { 
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Brain,
  CheckCircle,
  AlertTriangle,
  Zap
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import BottomDock from '../components/ui/BottomDock';
import RefineModal from '../components/RefineModal';

interface ContentViewerParams {
  contentId: string;
}

export default function ContentViewer() {
  const { contentId } = useParams<{ contentId: string }>();
  const { getIntelligenceContent, getIntelligenceContentByTaskId, updateRequestStatus } = useCommandStore();
  const [content, setContent] = useState<IntelligenceContent | null>(null);
  const [showRefineModal, setShowRefineModal] = useState(false);
  const [showInsights, setShowInsights] = useState(false);
  const [showFullContent, setShowFullContent] = useState(false);
  const [isApproved, setIsApproved] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  useEffect(() => {
    if (!contentId) return;
    
    // Try to get content by contentId first, then by taskId
    let intelligenceContent = getIntelligenceContent(contentId);
    
    if (!intelligenceContent) {
      // Fallback: try to find by taskId
      intelligenceContent = getIntelligenceContentByTaskId(contentId);
    }
    
    if (intelligenceContent) {
      setContent(intelligenceContent);
      console.log('📖 [ContentViewer] Loaded content:', intelligenceContent.contentId);
    } else {
      console.warn('📖 [ContentViewer] Content not found:', contentId);
    }
  }, [contentId, getIntelligenceContent, getIntelligenceContentByTaskId]);

  const handleCopyToClipboard = async () => {
    if (!content) return;
    
    try {
      await navigator.clipboard.writeText(content.generatedContent.narrative);
      setCopiedField('content');
      setTimeout(() => setCopiedField(null), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const handleApprove = () => {
    if (content?.taskId) {
      updateRequestStatus(content.taskId, 'Complete');
      setIsApproved(true);
      console.log('✅ Content approved and published:', content.contentId);
    }
  };

  const handleRefineSubmit = async (prompt: string) => {
    if (!content) return;
    
    setIsProcessing(true);
    try {
      // TODO: Integrate with existing CommandCenter AI pipeline
      console.log('🤖 Refining content with prompt:', prompt);
      
      // Simulate AI processing delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // TODO: Update content with refined version
      console.log('✨ Content refined successfully');
      setShowRefineModal(false);
    } catch (error) {
      console.error('Failed to refine content:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleShare = async () => {
    if (!content) return;
    
    try {
      if (navigator.share) {
        await navigator.share({
          title: content.title,
          text: content.generatedContent.narrative,
          url: window.location.href
        });
      } else {
        // Fallback to clipboard
        await navigator.clipboard.writeText(`${content.title}\n\n${content.generatedContent.narrative}\n\nShared from Aura Assistant`);
        setCopiedField('share');
        setTimeout(() => setCopiedField(null), 2000);
      }
      console.log('📤 Content shared successfully');
    } catch (error) {
      console.error('Failed to share content:', error);
    }
  };

  const handleExportPDF = () => {
    if (!content) return;
    
    // TODO: Integrate with PDF generation service
    console.log('📄 Exporting content as PDF:', content.contentId);
    
    // For now, create a simple download with content
    const element = document.createElement('a');
    const fileContent = `${content.title}\n\n${content.generatedContent.narrative}`;
    const file = new Blob([fileContent], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${content.title.replace(/[^a-z0-9]/gi, '_')}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const getStatusIcon = (content: IntelligenceContent) => {
    if (isApproved) return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (content.enhanced) return <Brain className="w-5 h-5 text-blue-600" />;
    if (content.exportReady) return <CheckCircle className="w-5 h-5 text-green-600" />;
    return <AlertTriangle className="w-5 h-5 text-orange-600" />;
  };

  const getStatusLabel = (content: IntelligenceContent) => {
    if (isApproved) return 'Approved';
    if (content.enhanced && content.exportReady) return 'AI Enhanced';
    if (content.exportReady) return 'Ready';
    return 'In Progress';
  };

  const getStatusColor = (content: IntelligenceContent) => {
    if (isApproved) return 'bg-green-100 text-green-800';
    if (content.enhanced && content.exportReady) return 'bg-blue-100 text-blue-800';
    if (content.exportReady) return 'bg-green-100 text-green-800';
    return 'bg-orange-100 text-orange-800';
  };

  const truncateContent = (text: string, maxLength: number = 800) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  if (!content) {
    return (
      <div className="w-full min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Content Not Found</h2>
          <p className="text-gray-600 mb-6">The requested content could not be found.</p>
          <Link 
            to="/requests"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Tasks
          </Link>
        </div>
      </div>
    );
  }

  const contentText = content.generatedContent.narrative || 'No content available';
  const isLongContent = contentText.length > 800;
  const displayContent = showFullContent ? contentText : truncateContent(contentText);

  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="w-full min-h-screen bg-slate-50 pb-32" // Bottom padding for dock and FAB
      >
        <div className="max-w-2xl mx-auto px-4 py-6 sm:px-6">
          
          {/* Header */}
          <header className="mb-6">
            <Link 
              to="/requests"
              className="inline-flex items-center gap-2 text-gray-500 hover:text-gray-700 transition-colors font-medium mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Tasks
            </Link>
            
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3">
                  {content.title}
                </h1>
                
                <div className="flex items-center gap-2">
                  <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium ${getStatusColor(content)}`}>
                    {getStatusIcon(content)}
                    {getStatusLabel(content)}
                  </div>
                </div>
              </div>
            </div>
          </header>

          {/* Main Content Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6"
          >
            <div className="prose prose-lg max-w-none">
              <div className="text-gray-800 leading-relaxed whitespace-pre-wrap font-['system-ui']">
                {displayContent}
              </div>
              
              {isLongContent && (
                <button
                  onClick={() => setShowFullContent(!showFullContent)}
                  className="inline-flex items-center gap-2 mt-4 text-blue-600 hover:text-blue-700 font-medium transition-colors"
                >
                  {showFullContent ? (
                    <>
                      Show less
                      <ChevronUp className="w-4 h-4" />
                    </>
                  ) : (
                    <>
                      View full content
                      <ChevronDown className="w-4 h-4" />
                    </>
                  )}
                </button>
              )}
            </div>
          </motion.div>

          {/* Key Insights - Collapsible */}
          {(content.generatedContent.keyInsights.length > 0 || content.generatedContent.actionableRecommendations.length > 0) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
            >
              <button
                onClick={() => setShowInsights(!showInsights)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-900">AI Insights</h3>
                  <span className="text-sm text-gray-500">
                    ({content.generatedContent.keyInsights.length + content.generatedContent.actionableRecommendations.length})
                  </span>
                </div>
                {showInsights ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
              </button>
              
              <AnimatePresence>
                {showInsights && (
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: 'auto' }}
                    exit={{ height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="border-t border-gray-100"
                  >
                    <div className="p-4 space-y-4">
                      {/* Key Insights */}
                      {content.generatedContent.keyInsights.length > 0 && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-3">Key Insights</h4>
                          <div className="space-y-2">
                            {content.generatedContent.keyInsights.map((insight, index) => (
                              <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                                <span className="text-gray-700 text-sm">{insight}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Recommendations */}
                      {content.generatedContent.actionableRecommendations.length > 0 && (
                        <div>
                          <h4 className="font-medium text-gray-900 mb-3">Recommendations</h4>
                          <div className="space-y-2">
                            {content.generatedContent.actionableRecommendations.map((rec, index) => (
                              <div key={index} className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                <span className="text-gray-700 text-sm">{rec}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}

        </div>
      </motion.div>

      {/* Bottom Dock */}
      <BottomDock
        onRefineWithAI={() => setShowRefineModal(true)}
        onApprove={handleApprove}
        onCopy={handleCopyToClipboard}
        onShare={handleShare}
        onExportPDF={handleExportPDF}
        isApproved={isApproved}
        isProcessing={isProcessing}
      />

      {/* Refine Modal */}
      <RefineModal
        isOpen={showRefineModal}
        onClose={() => setShowRefineModal(false)}
        onSubmit={handleRefineSubmit}
        isProcessing={isProcessing}
        taskTitle={content.contentType.toLowerCase().replace('_', ' ')}
      />
    </>
  );
}
