/**
 * ReportPreviewCard Component v3.1
 * 
 * Reusable preview component for generated content in Command Center results
 * Displays structured content with consistent visual hierarchy and export options
 */

import React from 'react';
import { motion } from 'framer-motion';
import { 
  FileText, 
  BarChart3, 
  MapPin, 
  Download, 
  ExternalLink,
  Eye,
  Share2,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { GeneratedContent, ContentType } from '../../services/templateOrchestrator';

interface ReportPreviewCardProps {
  content: GeneratedContent;
  onView?: (contentId: string) => void;
  onExport?: (contentId: string, format: 'pdf' | 'html' | 'json') => void;
  onShare?: (contentId: string) => void;
  compact?: boolean;
}

// Content type configurations for display
const CONTENT_CONFIG: Record<ContentType, {
  icon: React.ComponentType<any>;
  color: string;
  bgColor: string;
  label: string;
  description: string;
}> = {
  CMA: {
    icon: BarChart3,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    label: 'CMA Report',
    description: 'Comprehensive market analysis with comparables'
  },
  PITCH_DECK: {
    icon: FileText,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    label: 'Investor Pitch Deck',
    description: 'Professional presentation for investors'
  },
  SOCIAL_POST: {
    icon: Share2,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    label: 'Social Content',
    description: 'Engaging content for social media'
  },
  MARKET_REPORT: {
    icon: BarChart3,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    label: 'Market Report',
    description: 'In-depth market analysis and trends'
  }
};

const STATUS_CONFIG = {
  generating: {
    icon: Loader2,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50',
    label: 'Generating...',
    className: 'animate-spin'
  },
  ready: {
    icon: CheckCircle,
    color: 'text-green-500',
    bgColor: 'bg-green-50',
    label: 'Ready',
    className: ''
  },
  error: {
    icon: AlertCircle,
    color: 'text-red-500',
    bgColor: 'bg-red-50',
    label: 'Error',
    className: ''
  }
};

export default function ReportPreviewCard({ 
  content, 
  onView, 
  onExport, 
  onShare, 
  compact = false 
}: ReportPreviewCardProps) {
  const config = CONTENT_CONFIG[content.type];
  const statusConfig = STATUS_CONFIG[content.status];
  const IconComponent = config.icon;
  const StatusIcon = statusConfig.icon;

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleView = () => {
    if (onView && content.status === 'ready') {
      onView(content.id);
    }
  };

  const handleExport = (format: 'pdf' | 'html' | 'json') => {
    if (onExport && content.status === 'ready') {
      onExport(content.id, format);
    }
  };

  const handleShare = () => {
    if (onShare && content.status === 'ready') {
      onShare(content.id);
    }
  };

  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-lg border border-gray-200 p-3 hover:shadow-sm transition-shadow"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div className={`p-2 rounded-lg ${config.bgColor}`}>
              <IconComponent className={`w-4 h-4 ${config.color}`} />
            </div>
            
            <div className="min-w-0 flex-1">
              <h4 className="text-sm font-medium text-gray-900 truncate">
                {content.title}
              </h4>
              <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${statusConfig.bgColor}`}>
                  <StatusIcon className={`w-3 h-3 ${statusConfig.color} ${statusConfig.className}`} />
                  <span className={statusConfig.color}>{statusConfig.label}</span>
                </div>
                <span>•</span>
                <span>{formatDate(content.createdAt)}</span>
              </div>
            </div>
          </div>
          
          {content.status === 'ready' && (
            <button
              onClick={handleView}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <Eye className="w-4 h-4" />
            </button>
          )}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow duration-300"
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-xl ${config.bgColor}`}>
              <IconComponent className={`w-6 h-6 ${config.color}`} />
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                {content.title}
              </h3>
              <p className="text-gray-600 text-sm mb-2">
                {config.description}
              </p>
              
              {/* Status and metadata */}
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${statusConfig.bgColor}`}>
                  <StatusIcon className={`w-4 h-4 ${statusConfig.color} ${statusConfig.className}`} />
                  <span className={statusConfig.color}>{statusConfig.label}</span>
                </div>
                
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{formatDate(content.createdAt)}</span>
                </div>
                
                {content.metadata.location && (
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    <span>{content.metadata.location}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Status indicator */}
          <div className="flex flex-col items-end gap-2">
            <div className={`px-3 py-1 rounded-full text-xs font-medium ${statusConfig.bgColor} ${statusConfig.color}`}>
              {config.label}
            </div>
          </div>
        </div>
      </div>

      {/* Content preview */}
      {content.status === 'ready' && (
        <div className="p-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Content Preview</h4>
            
            {content.type === 'CMA' && content.content.structured && (
              <div className="space-y-3 text-sm">
                {content.content.structured.executive_summary && (
                  <div>
                    <span className="text-gray-600">Executive Summary:</span>
                    <p className="text-gray-800 mt-1">{content.content.structured.executive_summary}</p>
                  </div>
                )}
                
                {content.content.structured.market_overview && (
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <span className="text-gray-600">Avg. Price/sqft:</span>
                      <p className="font-medium">${content.content.structured.market_overview.average_price_psf}</p>
                    </div>
                    <div>
                      <span className="text-gray-600">Total Listings:</span>
                      <p className="font-medium">{content.content.structured.market_overview.total_listings}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {content.type === 'PITCH_DECK' && content.content.structured?.slides && (
              <div className="space-y-2 text-sm">
                <span className="text-gray-600">Slides:</span>
                {content.content.structured.slides.slice(0, 2).map((slide: any, index: number) => (
                  <div key={index} className="bg-white p-3 rounded border">
                    <div className="font-medium text-gray-800">{slide.title}</div>
                    <div className="text-gray-600 text-xs mt-1">{slide.subtitle}</div>
                  </div>
                ))}
                {content.content.structured.slides.length > 2 && (
                  <div className="text-xs text-gray-500 text-center">
                    +{content.content.structured.slides.length - 2} more slides
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error state */}
      {content.status === 'error' && (
        <div className="p-6">
          <div className="bg-red-50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-600 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span className="font-medium">Generation failed</span>
            </div>
            {content.error && (
              <p className="text-red-600 text-xs mt-2">{content.error}</p>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      {content.status === 'ready' && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                onClick={handleView}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Eye className="w-4 h-4" />
                View Full Report
              </button>
              
              <button
                onClick={handleShare}
                className="flex items-center gap-2 px-4 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <Share2 className="w-4 h-4" />
                Share
              </button>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleExport('pdf')}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <Download className="w-4 h-4" />
                PDF
              </button>
              
              <button
                onClick={() => handleExport('html')}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                HTML
              </button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}