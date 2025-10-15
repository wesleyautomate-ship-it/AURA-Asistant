import React, { useState, useEffect, useMemo } from 'react';
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
  Zap,
  Printer,
  Download,
  MapPin,
  Bed,
  Bath,
  Ruler,
  FileText
} from 'lucide-react';
import { parseBrochureStructuredData, formatBedrooms, formatBathrooms, formatSqft, type BrochureStructuredData } from '../utils/brochure';
import { motion, AnimatePresence } from 'framer-motion';
import BottomDock from '../components/ui/BottomDock';
import RefineModal from '../components/RefineModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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

  const isBrochure = content?.contentType === 'PROPERTY_BROCHURE';
  const brochureStructured = useMemo<BrochureStructuredData | null>(() => {
    if (!isBrochure || !content) {
      return null;
    }
    return parseBrochureStructuredData(
      (content.generatedContent?.structured as Record<string, unknown> | undefined) || {}
    );
  }, [isBrochure, content]);

  const brochurePdfUrl = isBrochure && content
    ? `${API_BASE_URL}/api/v1/intelligence/content/${content.contentId}?format=pdf`
    : undefined;

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
    
    const brochureText = brochureStructured?.description || brochureStructured?.title;
    const narrative = content.generatedContent.narrative;
    const textToCopy = narrative && narrative.trim().length > 0
      ? narrative
      : brochureText || content.title;

    try {
      await navigator.clipboard.writeText(textToCopy);
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

    const brochureShareText = brochureStructured
      ? `${structuredTitle(brochureStructured, content)}

${brochureStructured.description ?? ''}`.trim()
      : undefined;
    const narrative = content.generatedContent.narrative?.trim();
    const shareBody = narrative && narrative.length > 0 ? narrative : brochureShareText || content.title;

    try {
      if (navigator.share) {
        await navigator.share({
          title: content.title,
          text: shareBody,
          url: window.location.href
        });
      } else {
        await navigator.clipboard.writeText(`${content.title}

${shareBody}

Shared from Aura Assistant`);
        setCopiedField('share');
        setTimeout(() => setCopiedField(null), 2000);
      }
      console.log('Content shared successfully');
    } catch (error) {
      console.error('Failed to share content:', error);
    }
  };



  const handleExportPDF = () => {
    if (!content) return;

    if (content.contentType === 'PROPERTY_BROCHURE' && brochurePdfUrl) {
      window.open(brochurePdfUrl, '_blank', 'noopener');
      return;
    }

    const element = document.createElement('a');
    const fileContent = `${content.title}

${content.generatedContent.narrative}`;
    const file = new Blob([fileContent], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${content.title.replace(/[^a-z0-9]/gi, '_')}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handlePrint = () => {
    window.print();
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

  const narrativeText = content.generatedContent.narrative || 'No content available';
  const isLongContent = !isBrochure && narrativeText.length > 800;
  const displayContent = !isBrochure
    ? (showFullContent || !isLongContent
        ? narrativeText
        : `${narrativeText.slice(0, 800)}...`)
    : narrativeText;

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
            {isBrochure && brochureStructured ? (
              <PropertyBrochureDetail
                content={content}
                structured={brochureStructured}
                onPrint={handlePrint}
                pdfUrl={brochurePdfUrl}
              />
            ) : (
              <div className="prose prose-lg max-w-none">
                <div className="text-gray-800 leading-relaxed whitespace-pre-wrap font-['system-ui']">
                  {displayContent}
                </div>

                {!isBrochure && isLongContent && (
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
            )}
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

const structuredTitle = (structured: BrochureStructuredData, fallback: IntelligenceContent): string => {
  if (structured.title && structured.title.trim().length > 0) {
    return structured.title;
  }
  if (structured.location && structured.location.trim().length > 0) {
    return `${fallback.title} - ${structured.location}`;
  }
  return fallback.title;
};

interface PropertyBrochureDetailProps {
  content: IntelligenceContent;
  structured: BrochureStructuredData;
  onPrint: () => void;
  pdfUrl?: string;
}

function PropertyBrochureDetail({ content, structured, onPrint, pdfUrl }: PropertyBrochureDetailProps) {
  const quickFacts = [
    structured.bedrooms ? { icon: <Bed className="w-4 h-4 text-blue-600" />, label: formatBedrooms(structured.bedrooms) ?? '' } : null,
    structured.bathrooms ? { icon: <Bath className="w-4 h-4 text-blue-600" />, label: formatBathrooms(structured.bathrooms) ?? '' } : null,
    structured.areaSqft ? { icon: <Ruler className="w-4 h-4 text-blue-600" />, label: formatSqft(structured.areaSqft) ?? `${structured.areaSqft}` } : null,
    structured.propertyType ? { icon: <FileText className="w-4 h-4 text-blue-600" />, label: structured.propertyType } : null,
  ].filter(Boolean) as Array<{ icon: React.ReactNode; label: string }>;

  const sections = structured.sections || [];
  const amenitiesEntries = Object.entries(structured.amenities || {});
  const neighborhoodInsights = structured.neighborhoodInsights || [];
  const description = structured.description || content.generatedContent.narrative;
  const location = structured.location;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">Property Brochure</p>
          <h2 className="text-2xl font-semibold text-gray-900">{structuredTitle(structured, content)}</h2>
          {structured.subtitle && <p className="text-base text-gray-600">{structured.subtitle}</p>}
          {location && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <MapPin className="w-4 h-4" />
              <span>{location}</span>
            </div>
          )}
        </div>
        <div className="flex flex-col items-end gap-2">
          {structured.price && <span className="text-2xl font-semibold text-blue-600">{structured.price}</span>}
          <div className="flex flex-wrap justify-end gap-2">
            <button
              onClick={onPrint}
              className="inline-flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <Printer className="w-4 h-4" />
              Print
            </button>
            {pdfUrl && (
              <a
                href={pdfUrl}
                target="_blank"
                rel="noopener"
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700"
              >
                <Download className="w-4 h-4" />
                Download PDF
              </a>
            )}
          </div>
        </div>
      </div>

      {quickFacts.length > 0 && (
        <div className="flex flex-wrap gap-3">
          {quickFacts.map((fact, index) => (
            <span
              key={`${fact.label}-${index}`}
              className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700"
            >
              {fact.icon}
              {fact.label}
            </span>
          ))}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          {description && (
            <section className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-900">Overview</h3>
              <p className="text-sm leading-relaxed text-gray-700">{description}</p>
            </section>
          )}

          {structured.highlights.length > 0 && (
            <section className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-900">Highlights</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                {structured.highlights.map((highlight) => (
                  <li key={highlight} className="flex items-start gap-2">
                    <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-blue-500" />
                    <span>{highlight}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {structured.callToAction && (
            <div className="rounded-lg border border-blue-100 bg-blue-50 p-4 text-sm text-blue-800">
              {structured.callToAction}
            </div>
          )}
        </div>

        <div className="space-y-4">
          {sections.length > 0 && (
            <section className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-900">Key Sections</h3>
              {sections.slice(0, 3).map((section) => (
                <div key={section.label} className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                  <h4 className="text-sm font-semibold text-gray-900">{section.label}</h4>
                  {section.body && <p className="mt-1 text-sm text-gray-700">{section.body}</p>}
                  {section.bullets && section.bullets.length > 0 && (
                    <ul className="mt-2 space-y-1 list-disc list-inside text-sm text-gray-700">
                      {section.bullets.map((bullet) => (
                        <li key={bullet}>{bullet}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </section>
          )}

          {amenitiesEntries.length > 0 && (
            <section className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-900">Amenities</h3>
              <div className="grid gap-2">
                {amenitiesEntries.map(([category, amenities]) => (
                  <div key={category} className="rounded-lg border border-gray-100 bg-white p-3">
                    <p className="mb-1 text-sm font-semibold text-gray-900 capitalize">{category.replace(/_/g, ' ')}</p>
                    <div className="flex flex-wrap gap-2 text-xs text-gray-600">
                      {(amenities as string[]).map((amenity) => (
                        <span key={amenity} className="rounded-full bg-gray-100 px-2 py-1">
                          {amenity}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {neighborhoodInsights.length > 0 && (
            <section className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-900">Neighborhood Insights</h3>
              <ul className="space-y-1 text-sm text-gray-700">
                {neighborhoodInsights.map((insight) => (
                  <li key={insight} className="flex items-start gap-2">
                    <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-emerald-500" />
                    <span>{insight}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
