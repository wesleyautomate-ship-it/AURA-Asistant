/**
 * SlideCard Component v3.1
 * 
 * Renders individual slides for pitch deck content in preview mode
 * Supports consistent visual hierarchy and responsive design
 */

import { motion } from 'framer-motion';
import { 
  ChevronLeft, 
  ChevronRight, 
  Presentation,
  BarChart3,
  DollarSign,
  TrendingUp,
  MapPin,
  Users,
  ArrowRight,
  CheckCircle,
  Lightbulb,
  Target
} from 'lucide-react';

// Slide data interface
export interface SlideData {
  id?: number;
  title: string;
  subtitle?: string;
  content: string[];
  type?: 'title' | 'content' | 'data' | 'closing';
  background?: 'default' | 'gradient' | 'accent';
  layout?: 'center' | 'left' | 'split';
}

interface SlideCardProps {
  slide: SlideData;
  slideNumber: number;
  totalSlides: number;
  onNext?: () => void;
  onPrevious?: () => void;
  showNavigation?: boolean;
  compact?: boolean;
  className?: string;
}

// Slide type configurations
const SLIDE_CONFIG = {
  title: {
    icon: Presentation,
    bgClass: 'bg-gradient-to-br from-blue-600 to-purple-700',
    textClass: 'text-white',
    accentClass: 'text-blue-100'
  },
  content: {
    icon: Users,
    bgClass: 'bg-white',
    textClass: 'text-gray-900',
    accentClass: 'text-blue-600'
  },
  data: {
    icon: BarChart3,
    bgClass: 'bg-gradient-to-br from-green-50 to-blue-50',
    textClass: 'text-gray-900',
    accentClass: 'text-green-600'
  },
  closing: {
    icon: Target,
    bgClass: 'bg-gradient-to-br from-purple-600 to-blue-600',
    textClass: 'text-white',
    accentClass: 'text-purple-100'
  }
};

// Content type icons for different slide content
const CONTENT_ICONS: Record<string, React.ComponentType<any>> = {
  financial: DollarSign,
  market: TrendingUp,
  location: MapPin,
  opportunity: Lightbulb,
  next: ArrowRight,
  check: CheckCircle
};

const getContentIcon = (content: string): React.ComponentType<any> => {
  const lowerContent = content.toLowerCase();
  
  if (lowerContent.includes('financial') || lowerContent.includes('revenue') || lowerContent.includes('profit')) {
    return DollarSign;
  }
  if (lowerContent.includes('market') || lowerContent.includes('growth') || lowerContent.includes('trend')) {
    return TrendingUp;
  }
  if (lowerContent.includes('location') || lowerContent.includes('area') || lowerContent.includes('district')) {
    return MapPin;
  }
  if (lowerContent.includes('opportunity') || lowerContent.includes('potential')) {
    return Lightbulb;
  }
  
  return CheckCircle;
};

export default function SlideCard({
  slide,
  slideNumber,
  totalSlides,
  onNext,
  onPrevious,
  showNavigation = false,
  compact = false,
  className = ''
}: SlideCardProps) {
  const slideType = slide.type || 'content';
  const config = SLIDE_CONFIG[slideType];
  const IconComponent = config.icon;

  const slideHeight = compact ? 'h-64' : 'h-96';
  const aspectRatio = '16:9'; // Standard presentation aspect ratio

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative ${slideHeight} rounded-xl overflow-hidden shadow-lg border border-gray-200 ${className}`}
      style={{ aspectRatio: compact ? '16/10' : '16/9' }}
    >
      {/* Slide Content */}
      <div className={`${config.bgClass} h-full relative p-8 flex flex-col justify-center`}>
        
        {/* Slide Number Badge */}
        <div className="absolute top-4 right-4">
          <div className="bg-black bg-opacity-20 backdrop-blur-sm rounded-full px-3 py-1">
            <span className={`text-xs font-medium ${config.textClass} opacity-80`}>
              {slideNumber} / {totalSlides}
            </span>
          </div>
        </div>

        {/* Title Slide Layout */}
        {slideType === 'title' && (
          <div className="text-center">
            <div className={`w-16 h-16 ${config.accentClass.replace('text-', 'bg-').replace('600', '500')} rounded-full flex items-center justify-center mx-auto mb-6 bg-opacity-20`}>
              <IconComponent className={`w-8 h-8 ${config.textClass}`} />
            </div>
            
            <h1 className={`text-4xl font-bold ${config.textClass} mb-4`}>
              {slide.title}
            </h1>
            
            {slide.subtitle && (
              <p className={`text-xl ${config.accentClass} mb-8`}>
                {slide.subtitle}
              </p>
            )}
            
            {slide.content.length > 0 && (
              <div className="space-y-2">
                {slide.content.map((item, index) => (
                  <motion.p
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`text-lg ${config.accentClass}`}
                  >
                    {item}
                  </motion.p>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Content Slide Layout */}
        {slideType === 'content' && (
          <div className={slide.layout === 'center' ? 'text-center' : 'text-left'}>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-blue-50 rounded-lg">
                <IconComponent className="w-6 h-6 text-blue-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900">
                {slide.title}
              </h2>
            </div>
            
            {slide.subtitle && (
              <p className="text-xl text-gray-600 mb-8">
                {slide.subtitle}
              </p>
            )}
            
            <div className="space-y-4">
              {slide.content.map((item, index) => {
                const ContentIcon = getContentIcon(item);
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg"
                  >
                    <div className="flex-shrink-0">
                      <ContentIcon className="w-5 h-5 text-blue-600" />
                    </div>
                    <p className="text-gray-800 text-lg leading-relaxed">
                      {item}
                    </p>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}

        {/* Data Slide Layout */}
        {slideType === 'data' && (
          <div>
            <div className="text-center mb-8">
              <div className="p-3 bg-green-100 rounded-lg inline-flex">
                <IconComponent className="w-6 h-6 text-green-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mt-4 mb-2">
                {slide.title}
              </h2>
              {slide.subtitle && (
                <p className="text-lg text-gray-600">
                  {slide.subtitle}
                </p>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {slide.content.map((item, index) => {
                const ContentIcon = getContentIcon(item);
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white rounded-xl p-6 shadow-sm border border-gray-100"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <ContentIcon className="w-5 h-5 text-green-600" />
                      <div className="h-px bg-gray-200 flex-1"></div>
                    </div>
                    <p className="text-gray-800 font-medium text-lg">
                      {item}
                    </p>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}

        {/* Closing Slide Layout */}
        {slideType === 'closing' && (
          <div className="text-center">
            <div className={`w-20 h-20 ${config.accentClass.replace('text-', 'bg-').replace('100', '500')} rounded-full flex items-center justify-center mx-auto mb-6 bg-opacity-20`}>
              <IconComponent className={`w-10 h-10 ${config.textClass}`} />
            </div>
            
            <h2 className={`text-4xl font-bold ${config.textClass} mb-6`}>
              {slide.title}
            </h2>
            
            {slide.subtitle && (
              <p className={`text-xl ${config.accentClass} mb-8`}>
                {slide.subtitle}
              </p>
            )}
            
            {slide.content.length > 0 && (
              <div className="space-y-4">
                {slide.content.map((item, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-center gap-3"
                  >
                    <ArrowRight className={`w-5 h-5 ${config.accentClass}`} />
                    <p className={`text-lg ${config.textClass}`}>
                      {item}
                    </p>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {/* Navigation Controls */}
        {showNavigation && (
          <div className="absolute inset-x-4 bottom-4 flex items-center justify-between">
            <button
              onClick={onPrevious}
              disabled={slideNumber === 1}
              className="p-2 bg-black bg-opacity-20 backdrop-blur-sm rounded-full text-white disabled:opacity-30 disabled:cursor-not-allowed hover:bg-opacity-30 transition-all"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            
            <div className="flex gap-2">
              {Array.from({ length: totalSlides }, (_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full transition-all ${
                    i + 1 === slideNumber 
                      ? 'bg-white' 
                      : 'bg-white bg-opacity-30'
                  }`}
                />
              ))}
            </div>
            
            <button
              onClick={onNext}
              disabled={slideNumber === totalSlides}
              className="p-2 bg-black bg-opacity-20 backdrop-blur-sm rounded-full text-white disabled:opacity-30 disabled:cursor-not-allowed hover:bg-opacity-30 transition-all"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
}

// Preset slide templates for common pitch deck sections
export const SLIDE_TEMPLATES = {
  titleSlide: (title: string, subtitle: string): SlideData => ({
    title,
    subtitle,
    content: [],
    type: 'title',
    layout: 'center'
  }),
  
  problemStatement: (problems: string[]): SlideData => ({
    title: 'The Opportunity',
    subtitle: 'Market challenges we address',
    content: problems,
    type: 'content',
    layout: 'left'
  }),
  
  solution: (solutions: string[]): SlideData => ({
    title: 'Our Solution',
    subtitle: 'How we solve the problem',
    content: solutions,
    type: 'content',
    layout: 'left'
  }),
  
  financials: (metrics: string[]): SlideData => ({
    title: 'Financial Highlights',
    subtitle: 'Key performance metrics',
    content: metrics,
    type: 'data',
    layout: 'split'
  }),
  
  nextSteps: (steps: string[]): SlideData => ({
    title: 'Next Steps',
    subtitle: 'Ready to move forward',
    content: steps,
    type: 'closing',
    layout: 'center'
  })
};