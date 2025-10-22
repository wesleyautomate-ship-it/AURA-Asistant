/**
 * CMAReport Page Component v3.1
 * 
 * Full-page viewer for generated CMA reports with export options
 * Displays comprehensive market analysis with professional layout following brand templates
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  Printer, 
  ExternalLink,
  BarChart3,
  TrendingUp,
  Building2,
  MapPin,
  Calendar,
  FileText,
  Home,
  DollarSign,
  Clock,
  Users
} from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCommandStore, CMAData } from '../store/commandStore';

// Type alias for backward compatibility
type LegacyMarketOverview = {
  average_price_psf: number;
  total_listings: number;
  avg_days_on_market: number;
  price_trend: 'upward' | 'downward' | 'stable';
  median_price: number;
  price_change_yoy: number;
};

type LegacyComparable = {
  address: string;
  price: number;
  size: number;
  price_psf: number;
  bedrooms?: number;
  bathrooms?: number;
  building_type?: string;
  days_on_market?: number;
};

type LegacyCMAData = {
  executive_summary: string;
  market_overview: LegacyMarketOverview;
  comparables: LegacyComparable[];
  insights: string[];
  recommendations: string;
  neighborhood_stats?: {
    population: number;
    avg_income: number;
    employment_rate: number;
    development_projects: number;
  };
};

export default function CMAReport() {
  const { id: taskId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getGeneratedContent } = useCommandStore();
  const [content, setContent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exportLoading, setExportLoading] = useState<string | null>(null);

  useEffect(() => {
    if (taskId) {
      try {
        const generatedContent = getGeneratedContent(taskId);
        if (generatedContent && generatedContent.type === 'CMA_REPORT') {
          setContent(generatedContent);
        } else {
          setError('CMA report not found or invalid type');
        }
      } catch (err) {
        setError('Failed to load CMA report');
        console.error('Error loading CMA content:', err);
      } finally {
        setLoading(false);
      }
    }
  }, [taskId, getGeneratedContent]);

  const handleExport = async (format: 'pdf' | 'html' | 'json') => {
    if (!content || !taskId) return;
    
    setExportLoading(format);
    
    // Simulate export process
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // In production, this would call the actual export API
      const exportUrl = `/api/v1/cma/export/${taskId}?format=${format}`;
      window.open(exportUrl, '_blank');
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExportLoading(null);
    }
  };

  const handleShare = async () => {
    if (!content) return;
    
    try {
      if (navigator.share) {
        await navigator.share({
          title: content.title,
          text: `CMA Report - ${content.title}`,
          url: window.location.href
        });
      } else {
        await navigator.clipboard.writeText(window.location.href);
        // Could show a toast notification here
      }
    } catch (error) {
      console.error('Share failed:', error);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading CMA Report...</p>
        </div>
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            {error ? 'Error Loading Report' : 'Report Not Found'}
          </h1>
          <p className="text-gray-600 mb-4">
            {error || 'The CMA report you\'re looking for doesn\'t exist.'}
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => navigate(-1)}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Go Back
            </button>
            <button
              onClick={() => navigate('/requests')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              View Requests
            </button>
          </div>
        </div>
      </div>
    );
  }

  const cmaData = content.data as CMAData;
  
  // Transform new data structure to legacy format for backward compatibility
  const legacyData: LegacyCMAData = {
    executive_summary: cmaData.insights?.[0] || 'Market analysis summary',
    market_overview: {
      average_price_psf: cmaData.marketAnalysis?.pricePerSqft || 0,
      total_listings: cmaData.marketAnalysis?.inventory || 0,
      avg_days_on_market: cmaData.marketAnalysis?.daysOnMarket || 0,
      price_trend: cmaData.marketAnalysis?.marketTrend === 'up' ? 'upward' : 
                   cmaData.marketAnalysis?.marketTrend === 'down' ? 'downward' : 'stable',
      median_price: cmaData.marketAnalysis?.medianPrice || 0,
      price_change_yoy: 0 // Not available in new structure
    },
    comparables: cmaData.comparables?.map(comp => ({
      address: comp.address,
      price: comp.price,
      size: comp.sqft,
      price_psf: comp.pricePerSqft,
      bedrooms: comp.bedrooms,
      bathrooms: comp.bathrooms,
      building_type: 'Residential', // Default value
      days_on_market: undefined
    })) || [],
    insights: cmaData.insights || [],
    recommendations: cmaData.insights?.[cmaData.insights?.length - 1] || 'No specific recommendations available',
    neighborhood_stats: undefined // Not available in new structure
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-gray-900">{content.title}</h1>
                  <p className="text-sm text-gray-500">
                    Generated {new Date(content.generatedAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleShare}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <Share2 className="w-4 h-4" />
                Share
              </button>
              
              <button
                onClick={handlePrint}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <Printer className="w-4 h-4" />
                Print
              </button>
              
              <div className="relative">
                <button
                  onClick={() => handleExport('pdf')}
                  disabled={!!exportLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {exportLoading === 'pdf' ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <Download className="w-4 h-4" />
                  )}
                  Export PDF
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Report Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          
          {/* Report Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-8 py-12 text-white">
            <div className="max-w-3xl">
              <h1 className="text-3xl font-bold mb-4">
                Competitive Market Analysis
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-blue-100">
                {cmaData.property?.address && (
                  <div className="flex items-center gap-2">
                    <MapPin className="w-5 h-5" />
                    <div>
                      <div className="text-sm opacity-80">Property Address</div>
                      <div className="font-medium text-white">{cmaData.property.address}</div>
                    </div>
                  </div>
                )}
                
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5" />
                  <div>
                    <div className="text-sm opacity-80">Report Date</div>
                    <div className="font-medium text-white">
                      {new Date(content.generatedAt).toLocaleDateString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  <div>
                    <div className="text-sm opacity-80">Report Type</div>
                    <div className="font-medium text-white">Full CMA Analysis</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="p-8">
            
            {/* Executive Summary */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                Executive Summary
              </h2>
              <div className="bg-blue-50 rounded-xl p-6">
                <p className="text-gray-800 leading-relaxed text-lg">
                  {legacyData.executive_summary}
                </p>
              </div>
            </section>

            {/* Market Overview */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <div className="p-2 bg-green-50 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                </div>
                Market Overview
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div className="bg-gray-50 rounded-xl p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <DollarSign className="w-5 h-5 text-blue-600" />
                    <span className="text-sm font-medium text-gray-600">Avg. Price/sqft</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    ${legacyData.market_overview.average_price_psf.toLocaleString()}
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-xl p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <Building2 className="w-5 h-5 text-purple-600" />
                    <span className="text-sm font-medium text-gray-600">Total Listings</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {legacyData.market_overview.total_listings.toLocaleString()}
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-xl p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <Clock className="w-5 h-5 text-orange-600" />
                    <span className="text-sm font-medium text-gray-600">Avg. Days on Market</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {legacyData.market_overview.avg_days_on_market}
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-xl p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <TrendingUp className="w-5 h-5 text-green-600" />
                    <span className="text-sm font-medium text-gray-600">Price Trend</span>
                  </div>
                  <div className={`text-2xl font-bold capitalize ${
                    legacyData.market_overview.price_trend === 'upward' ? 'text-green-600' :
                    legacyData.market_overview.price_trend === 'downward' ? 'text-red-600' :
                    'text-gray-600'
                  }`}>
                    {legacyData.market_overview.price_trend}
                  </div>
                </div>
              </div>
            </section>

            {/* Comparable Properties */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <div className="p-2 bg-purple-50 rounded-lg">
                  <Home className="w-5 h-5 text-purple-600" />
                </div>
                Comparable Properties
              </h2>
              
              <div className="overflow-x-auto">
                <table className="w-full border-collapse bg-white rounded-xl border border-gray-200">
                  <thead>
                    <tr className="bg-gray-50 border-b border-gray-200">
                      <th className="text-left py-4 px-6 font-semibold text-gray-900">Address</th>
                      <th className="text-left py-4 px-6 font-semibold text-gray-900">Price</th>
                      <th className="text-left py-4 px-6 font-semibold text-gray-900">Size (sqft)</th>
                      <th className="text-left py-4 px-6 font-semibold text-gray-900">Price/sqft</th>
                    </tr>
                  </thead>
                  <tbody>
                    {legacyData.comparables.map((comp, index) => (
                      <tr key={index} className="border-b border-gray-100">
                        <td className="py-4 px-6 text-gray-900">{comp.address}</td>
                        <td className="py-4 px-6 text-gray-900 font-medium">
                          ${comp.price.toLocaleString()}
                        </td>
                        <td className="py-4 px-6 text-gray-600">
                          {comp.size.toLocaleString()} sqft
                        </td>
                        <td className="py-4 px-6 text-gray-900 font-medium">
                          ${comp.price_psf.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Market Insights */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <div className="p-2 bg-orange-50 rounded-lg">
                  <BarChart3 className="w-5 h-5 text-orange-600" />
                </div>
                Key Market Insights
              </h2>
              
              <div className="space-y-4">
                {legacyData.insights.map((insight, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-4 p-4 bg-orange-50 rounded-xl"
                  >
                    <div className="flex-shrink-0 w-6 h-6 bg-orange-200 rounded-full flex items-center justify-center mt-1">
                      <span className="text-orange-600 text-sm font-semibold">{index + 1}</span>
                    </div>
                    <p className="text-gray-800 leading-relaxed">{insight}</p>
                  </motion.div>
                ))}
              </div>
            </section>

            {/* Recommendations */}
            <section className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <div className="p-2 bg-green-50 rounded-lg">
                  <Users className="w-5 h-5 text-green-600" />
                </div>
                Recommendations
              </h2>
              
              <div className="bg-green-50 rounded-xl p-8">
                <p className="text-gray-800 leading-relaxed text-lg">
                  {legacyData.recommendations}
                </p>
              </div>
            </section>

          </div>

          {/* Footer */}
          <div className="bg-gray-50 border-t border-gray-200 px-8 py-6">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                <p>Report generated by Aura AI • {new Date().toLocaleDateString()}</p>
                <p className="mt-1">Data sources: Market analytics and comparable property research</p>
              </div>
              
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleExport('html')}
                  disabled={!!exportLoading}
                  className="flex items-center gap-2 px-3 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 transition-colors"
                >
                  {exportLoading === 'html' ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                  ) : (
                    <ExternalLink className="w-4 h-4" />
                  )}
                  Export HTML
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}