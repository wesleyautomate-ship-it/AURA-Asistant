/**
 * DeckBuilder Page Component v3.1
 * 
 * Interactive deck preview and slide editor for generated pitch decks
 * Supports full-screen presentation mode and export functionality
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  Printer, 
  ExternalLink,
  Play,
  Maximize,
  Grid3X3,
  ChevronLeft,
  ChevronRight,
  FileText,
  Presentation,
  Edit3,
  Save,
  MoreHorizontal
} from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCommandStore, PitchDeckData } from '../store/commandStore';
import SlideCard, { SlideData } from '../components/ui/SlideCard';

// Deck data interface
interface DeckData {
  slides: SlideData[];
  title?: string;
  subtitle?: string;
  metadata?: {
    author?: string;
    date?: string;
    version?: string;
  };
}

// View modes
type ViewMode = 'grid' | 'single' | 'presentation';

export default function DeckBuilder() {
  const { id: taskId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { getGeneratedContent } = useCommandStore();
  const [content, setContent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('single');
  const [currentSlide, setCurrentSlide] = useState(0);
  const [exportLoading, setExportLoading] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [deckData, setDeckData] = useState<DeckData | null>(null);

  useEffect(() => {
    if (taskId) {
      try {
        const generatedContent = getGeneratedContent(taskId);
        if (generatedContent && generatedContent.type === 'PITCH_DECK') {
          setContent(generatedContent);
          
          const pitchData = generatedContent.data as PitchDeckData;
          if (pitchData?.slides) {
            setDeckData({
              slides: pitchData.slides.map((slide, index) => ({
                id: index,
                title: slide.title,
                subtitle: slide.content.text || '',
                content: slide.content.bullets || [slide.content.text || ''].filter(Boolean),
                type: slide.type === 'title' ? 'title' : 
                      slide.type === 'conclusion' ? 'closing' :
                      slide.content.charts ? 'data' : 'content'
              })),
              title: pitchData.title,
              metadata: {
                author: 'Aura AI',
                date: new Date().toLocaleDateString(),
                version: '1.0'
              }
            });
          }
        } else {
          setError('Pitch deck not found or invalid type');
        }
      } catch (err) {
        setError('Failed to load pitch deck');
        console.error('Error loading deck content:', err);
      } finally {
        setLoading(false);
      }
    }
  }, [taskId, getGeneratedContent]);

  const handleExport = async (format: 'pdf' | 'html' | 'json') => {
    if (!content || !taskId) return;
    
    setExportLoading(format);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const exportUrl = `/api/v1/decks/export/${taskId}?format=${format}`;
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
          text: `Investor Pitch Deck - ${content.title}`,
          url: window.location.href
        });
      } else {
        await navigator.clipboard.writeText(window.location.href);
      }
    } catch (error) {
      console.error('Share failed:', error);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleSlideNavigation = (direction: 'next' | 'previous') => {
    if (!deckData) return;
    
    if (direction === 'next' && currentSlide < deckData.slides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    } else if (direction === 'previous' && currentSlide > 0) {
      setCurrentSlide(currentSlide - 1);
    }
  };

  const handlePresentationMode = () => {
    setViewMode('presentation');
    // In a real implementation, this would enter full-screen mode
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen();
    }
  };

  const exitPresentationMode = () => {
    setViewMode('single');
    if (document.fullscreenElement) {
      document.exitFullscreen();
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (viewMode === 'presentation') {
        switch (e.key) {
          case 'ArrowRight':
          case ' ':
            handleSlideNavigation('next');
            break;
          case 'ArrowLeft':
            handleSlideNavigation('previous');
            break;
          case 'Escape':
            exitPresentationMode();
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [viewMode, currentSlide, deckData]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Pitch Deck...</p>
        </div>
      </div>
    );
  }

  if (error || !content || !deckData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Presentation className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            {error ? 'Error Loading Deck' : 'Deck Not Found'}
          </h1>
          <p className="text-gray-600 mb-4">
            {error || 'The pitch deck you\'re looking for doesn\'t exist.'}
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
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              View Requests
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Presentation Mode
  if (viewMode === 'presentation') {
    return (
      <div className="fixed inset-0 bg-black z-50">
        <div className="h-full flex items-center justify-center p-8">
          <div className="w-full max-w-6xl">
            <SlideCard
              slide={deckData.slides[currentSlide]}
              slideNumber={currentSlide + 1}
              totalSlides={deckData.slides.length}
              onNext={() => handleSlideNavigation('next')}
              onPrevious={() => handleSlideNavigation('previous')}
              showNavigation={true}
              className="w-full"
            />
          </div>
          
          {/* Exit button */}
          <button
            onClick={exitPresentationMode}
            className="absolute top-4 right-4 p-3 bg-black bg-opacity-50 backdrop-blur-sm rounded-full text-white hover:bg-opacity-70 transition-all"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
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
                <div className="p-2 bg-purple-50 rounded-lg">
                  <Presentation className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h1 className="text-lg font-semibold text-gray-900">{content.title}</h1>
                  <p className="text-sm text-gray-500">
                    {deckData.slides.length} slides • Generated {new Date(content.generatedAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* View Mode Toggle */}
              <div className="flex items-center bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'grid' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-600'
                  }`}
                >
                  <Grid3X3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('single')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'single' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-600'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                </button>
              </div>

              <button
                onClick={handlePresentationMode}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <Play className="w-4 h-4" />
                Present
              </button>

              <button
                onClick={handleShare}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
              >
                <Share2 className="w-4 h-4" />
                Share
              </button>
              
              <div className="relative">
                <button
                  onClick={() => handleExport('pdf')}
                  disabled={!!exportLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
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

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Grid View */}
        {viewMode === 'grid' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {deckData.slides.map((slide, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="cursor-pointer"
                onClick={() => {
                  setCurrentSlide(index);
                  setViewMode('single');
                }}
              >
                <SlideCard
                  slide={slide}
                  slideNumber={index + 1}
                  totalSlides={deckData.slides.length}
                  compact={true}
                  className="hover:shadow-xl transition-shadow duration-300"
                />
                <div className="mt-3 text-center">
                  <h3 className="text-sm font-medium text-gray-900 truncate">
                    {slide.title}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    Slide {index + 1}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Single View */}
        {viewMode === 'single' && (
          <div className="max-w-5xl mx-auto">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <h2 className="text-2xl font-bold text-gray-900">
                  Slide {currentSlide + 1} of {deckData.slides.length}
                </h2>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleSlideNavigation('previous')}
                    disabled={currentSlide === 0}
                    className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleSlideNavigation('next')}
                    disabled={currentSlide === deckData.slides.length - 1}
                    className="p-2 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg border transition-colors ${
                    isEditing 
                      ? 'bg-blue-50 text-blue-700 border-blue-200'
                      : 'text-gray-600 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {isEditing ? <Save className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
                  {isEditing ? 'Save' : 'Edit'}
                </button>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
              <SlideCard
                slide={deckData.slides[currentSlide]}
                slideNumber={currentSlide + 1}
                totalSlides={deckData.slides.length}
                className="w-full max-w-4xl mx-auto"
              />
            </div>

            {/* Slide Navigation */}
            <div className="mt-8">
              <div className="flex items-center justify-between">
                <button
                  onClick={() => handleSlideNavigation('previous')}
                  disabled={currentSlide === 0}
                  className="flex items-center gap-2 px-4 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </button>

                <div className="flex gap-2">
                  {deckData.slides.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentSlide(index)}
                      className={`w-3 h-3 rounded-full transition-all ${
                        index === currentSlide 
                          ? 'bg-purple-600' 
                          : 'bg-gray-300 hover:bg-gray-400'
                      }`}
                    />
                  ))}
                </div>

                <button
                  onClick={() => handleSlideNavigation('next')}
                  disabled={currentSlide === deckData.slides.length - 1}
                  className="flex items-center gap-2 px-4 py-2 text-gray-600 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Slide Summary */}
        <div className="mt-12 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Deck Overview</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {deckData.slides.map((slide, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  index === currentSlide
                    ? 'border-purple-200 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => {
                  setCurrentSlide(index);
                  setViewMode('single');
                }}
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xs font-semibold text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
                    {index + 1}
                  </span>
                  <h4 className="font-medium text-gray-900 truncate">
                    {slide.title}
                  </h4>
                </div>
                {slide.subtitle && (
                  <p className="text-sm text-gray-600 mb-2">
                    {slide.subtitle}
                  </p>
                )}
                <p className="text-xs text-gray-500">
                  {slide.content.length} content items
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
