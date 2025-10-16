import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { useSwipeable } from 'react-swipeable';
import { Link, useNavigate } from 'react-router-dom';
import { useCommandStore, type IntelligenceContent as StoreIntelligenceContent } from '../store/commandStore';
import { 
  ChevronLeft, 
  ChevronRight, 
  Home, 
  Users, 
  ClipboardList, 
  Megaphone,
  ChevronRight as CardChevron,
  Zap,
  Activity,
  TrendingUp,
  Loader2,
  FileText,
  BarChart3,
  MapPin,
  Bed,
  Bath,
  Ruler
} from 'lucide-react';
import { type KpiMetric } from '../services/mockData';
import RefineModal from '../components/RefineModal';
import { ProgressTracker, type ProgressStep } from '../components/ui/ProgressTracker';
import { intelligenceApi, IntelligenceApiError } from '../services/api/intelligenceApi';
import { TaskStatus, type ProgressEventData } from '../types/intelligence';
import { mapApiIntelligenceContent } from '../utils/intelligenceContent';
import { parseBrochureStructuredData, formatBedrooms, formatBathrooms, formatSqft, type BrochureStructuredData } from '../utils/brochure';
import { pickRandomSeededListing, type SeededListing } from '../data/seededListings';
import DevStatus from '../components/DevStatus';

interface Slide {
  title: string;
  desc?: string;
  action?: string;
  color: string;
  render?: React.ReactNode;
}

const getIconComponent = (iconName: string) => {
  switch (iconName) {
    case 'Home':
      return <Home className="w-5 h-5 text-blue-600" />;
    case 'Zap':
      return <Zap className="w-5 h-5 text-yellow-500" />;
    case 'Activity':
      return <Activity className="w-5 h-5 text-green-600" />;
    default:
      return null;
  }
};

const getColorClasses = (color: string) => {
  switch (color) {
    case 'blue':
      return { bg: 'bg-blue-50', border: 'border-blue-500' };
    case 'yellow':
      return { bg: 'bg-yellow-50', border: 'border-yellow-500' };
    case 'green':
      return { bg: 'bg-green-50', border: 'border-green-500' };
    default:
      return { bg: 'bg-gray-50', border: 'border-gray-500' };
  }
};

const getSlides = (metrics: KpiMetric[]): Slide[] => [
  { 
    title: 'Create First', 
    desc: 'Quickly create your first workflow or task.', 
    action: 'Start Creating', 
    color: 'bg-blue-100' 
  },
  { 
    title: 'Daily Briefing', 
    desc: "Aura's AI notes:",
    color: 'bg-green-100',
    render: (
      <section className="mt-4 space-y-3">
        <ul className="text-gray-700 text-sm sm:text-base list-disc pl-5 space-y-1">
          <li>{metrics[0].value > 5 ? 'AI tasks increasing â€” great activity!' : metrics[0].value > 0 ? 'Some task activity today.' : 'No tasks yet â€” start creating!'}</li>
          <li>{metrics[1].value > 3 ? 'AI requests processing well.' : 'AI activity stable.'}</li>
          <li>Success rate at {metrics[2].value}% ({metrics[2].delta.startsWith('+') ? '+' : ''}{metrics[2].delta}% change).</li>
        </ul>
        <Link
          to="/requests"
          className="inline-block mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm sm:text-base font-medium shadow-md hover:shadow-lg"
        >
          View All Requests
        </Link>
      </section>
    )
  },
  { 
    title: 'Analytics Overview', 
    color: 'bg-purple-50',
    render: (
      <section className="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4 mt-4">
        {metrics.map((m, idx) => {
          const colors = getColorClasses(m.color);
          const deltaNum = parseFloat(m.delta);
          return (
            <motion.div
              key={m.label}
              layout
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.1 }}
              className={`p-3 sm:p-4 rounded-xl shadow-md bg-white flex flex-col items-center sm:items-start space-y-2 border-t-4 border-transparent hover:${colors.border} transition ${colors.bg}`}
            >
              <div className="flex items-center gap-2">
                {getIconComponent(m.icon)}
                <h4 className="font-medium text-gray-700 text-xs sm:text-sm">{m.label}</h4>
              </div>
              <div className="flex items-baseline gap-2">
                <motion.span
                  key={m.value}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25 }}
                  className="text-xl sm:text-2xl font-bold text-gray-900"
                >
                  {m.value}{m.isPercent && '%'}
                </motion.span>
                <motion.span
                  key={m.delta}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.25, delay: 0.1 }}
                  className={`text-xs font-medium flex items-center gap-0.5 ${
                    deltaNum >= 0 ? 'text-green-600' : 'text-red-500'
                  }`}
                >
                  {deltaNum >= 0 ? <TrendingUp className="w-3 h-3" /> : 'â–¼'}
                  {deltaNum >= 0 ? '+' : ''}{m.delta}%
                </motion.span>
              </div>
            </motion.div>
          );
        })}
      </section>
    )
  },
];

type BrochureStepId = 'init' | 'property_lookup' | 'prompt_build' | 'generating' | 'formatting' | 'completed';

const BROCHURE_STEP_PROGRESS: Record<BrochureStepId, number> = {
  init: 5,
  property_lookup: 20,
  prompt_build: 40,
  generating: 70,
  formatting: 90,
  completed: 100,
};

const BROCHURE_PROGRESS_STEPS: ProgressStep[] = [
  { id: 'init', label: 'Initializing', description: 'Preparing brochure workflow', percentage: 5 },
  { id: 'property_lookup', label: 'Property Lookup', description: 'Finding the right listing', percentage: 20 },
  { id: 'prompt_build', label: 'Prompt Build', description: 'Gathering listing insights', percentage: 40 },
  { id: 'generating', label: 'Generating', description: 'Crafting brochure narrative', percentage: 70 },
  { id: 'formatting', label: 'Formatting', description: 'Polishing presentation', percentage: 90 },
  { id: 'completed', label: 'Ready', description: 'Brochure ready to review', percentage: 100 },
];

const normalizeBrochureStep = (event: ProgressEventData): BrochureStepId => {
  const rawStep = (event.current_step || event.status || 'generating').toString().toLowerCase();

  if (rawStep.includes('lookup')) return 'property_lookup';
  if (rawStep.includes('prompt')) return 'prompt_build';
  if (rawStep.includes('format')) return 'formatting';
  if (rawStep.includes('init') || rawStep.includes('queue')) return 'init';
  if (rawStep.includes('complete')) return 'completed';
  if (rawStep.includes('generate')) return 'generating';

  return 'generating';
};

const clampProgress = (value: number): number => {
  if (!Number.isFinite(value)) return 0;
  if (value < 0) return 0;
  if (value > 100) return 100;
  return Math.round(value);
};

const mapStepToProgress = (step: BrochureStepId, fallback?: number): number => {
  if (typeof fallback === 'number' && Number.isFinite(fallback)) {
    return clampProgress(fallback);
  }
  return BROCHURE_STEP_PROGRESS[step];
};

export default function Dashboard() {
  const navigate = useNavigate();
  const {
    requests,
    addRequest,
    updateRequestStatus,
    updateRequestProgress,
    saveIntelligenceContent
  } = useCommandStore();
  
  // Generate real metrics from task data
  const generateRealMetrics = (): KpiMetric[] => {
    const totalTasks = requests.length;
    const completedTasks = requests.filter(r => r.status === 'Complete').length;
    const processingTasks = requests.filter(r => r.status === 'Processing').length;
    // const errorTasks = requests.filter(r => r.status === 'Error').length;
    
    // Calculate engagement rate (completed tasks / total tasks)
    const engagementRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    
    // Mock some deltas for visual appeal (could be real historical comparison)
    const totalDelta = totalTasks > 10 ? '+15' : totalTasks > 5 ? '+8' : '+3';
    const aiDelta = processingTasks > 0 ? '+12' : '0';
    const engagementDelta = engagementRate > 70 ? '+5' : engagementRate > 50 ? '+2' : '-1';
    
    return [
      {
        label: 'Total Tasks',
        value: totalTasks,
        delta: totalDelta,
        icon: 'Home',
        color: 'blue',
        isPercent: false,
      },
      {
        label: 'AI Requests',
        value: processingTasks + completedTasks,
        delta: aiDelta,
        icon: 'Zap',
        color: 'yellow',
        isPercent: false,
      },
      {
        label: 'Success Rate',
        value: engagementRate,
        delta: engagementDelta,
        icon: 'Activity',
        color: 'green',
        isPercent: true,
      },
    ];
  };
  
  const [metrics, setMetrics] = useState<KpiMetric[]>(generateRealMetrics);

  const [brochureStatus, setBrochureStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [brochureProgress, setBrochureProgress] = useState(0);
  const [brochureStep, setBrochureStep] = useState<BrochureStepId>('init');
  const [brochureError, setBrochureError] = useState<string | null>(null);
  const [brochureListing, setBrochureListing] = useState<SeededListing | null>(null);
  const [brochureContent, setBrochureContent] = useState<StoreIntelligenceContent | null>(null);
  const [isBrochureModalOpen, setIsBrochureModalOpen] = useState(false);
  const brochureStructured = useMemo(() => {
    if (!brochureContent) {
      return null;
    }
    return parseBrochureStructuredData(
      (brochureContent.generatedContent?.structured as Record<string, unknown> | undefined) || {}
    );
  }, [brochureContent]);

  const isBrochureProcessing = brochureStatus === 'processing';

  const handleCloseBrochureModal = useCallback(() => {
    if (brochureStatus === 'processing') {
      return;
    }

    setIsBrochureModalOpen(false);

    if (brochureStatus !== 'success') {
      setBrochureStatus('idle');
      setBrochureProgress(0);
      setBrochureStep('init');
      setBrochureError(null);
      setBrochureListing(null);
      setBrochureContent(null);
    }
  }, [brochureStatus]);

  const openBrochureInViewer = useCallback((contentId: string) => {
    setIsBrochureModalOpen(false);
    setBrochureStatus('idle');
    setBrochureProgress(0);
    setBrochureStep('init');
    setBrochureError(null);
    setBrochureListing(null);
    setBrochureContent(null);
    navigate(`/content/${contentId}`);
  }, [navigate]);

  const handleGenerateBrochure = useCallback(async () => {
    if (brochureStatus === 'processing') {
      return;
    }

    const listing = pickRandomSeededListing();
    let hasFailed = false;

    setBrochureListing(listing);
    setBrochureStatus('processing');
    setBrochureStep('init');
    setBrochureProgress(BROCHURE_STEP_PROGRESS.init);
    setBrochureError(null);
    setBrochureContent(null);
    setIsBrochureModalOpen(true);

    const requestId = addRequest(`Property Brochure • ${listing.title}`, 'PROPERTY_BROCHURE', {
      listingId: listing.listingId,
      source: 'dashboard_quick_action',
    });
    brochureRequestIdRef.current = requestId;
    updateRequestStatus(requestId, 'Processing');
    updateRequestProgress(requestId, BROCHURE_STEP_PROGRESS.init, 'init');

    const handleProgressUpdate = (event: ProgressEventData) => {
      const step = normalizeBrochureStep(event);
      const computedProgress = mapStepToProgress(step, event.progress);

      setBrochureStep(step);
      setBrochureProgress((prev) => Math.max(prev, computedProgress));

      if (brochureRequestIdRef.current) {
        updateRequestProgress(brochureRequestIdRef.current, computedProgress, step);
        if (event.status === TaskStatus.PROCESSING || event.status === TaskStatus.QUEUED) {
          updateRequestStatus(brochureRequestIdRef.current, 'Processing');
        }
      }

      if (event.status === TaskStatus.FAILED) {
        hasFailed = true;
        const message = event.data?.error || 'Brochure generation failed.';
        setBrochureStatus('error');
        setBrochureError(message);
        if (brochureRequestIdRef.current) {
          updateRequestStatus(brochureRequestIdRef.current, 'Error', message);
        }
      }

      if (event.status === TaskStatus.COMPLETED) {
        setBrochureProgress(100);
        setBrochureStep('completed');
      }
    };

    try {
      const apiContent = await intelligenceApi.generateBrochure(listing.listingId, {
        context: {
          listing_title: listing.title,
          listing_location: listing.location,
        },
        onProgress: handleProgressUpdate,
      });

      if (hasFailed) {
        return;
      }

      const mappedContent = mapApiIntelligenceContent(apiContent);
      saveIntelligenceContent(mappedContent);
      setBrochureContent(mappedContent);
      setBrochureStatus('success');
      setBrochureProgress(100);
      setBrochureStep('completed');

      if (brochureRequestIdRef.current) {
        updateRequestStatus(brochureRequestIdRef.current, 'Complete');
        updateRequestProgress(brochureRequestIdRef.current, 100, 'completed');
      }
    } catch (error) {
      hasFailed = true;
      const message = error instanceof IntelligenceApiError
        ? error.message
        : 'Unable to generate property brochure.';
      setBrochureStatus('error');
      setBrochureError(message);
      if (brochureRequestIdRef.current) {
        updateRequestStatus(brochureRequestIdRef.current, 'Error', message);
      }
    } finally {
      brochureRequestIdRef.current = null;
    }
  }, [addRequest, brochureStatus, saveIntelligenceContent, updateRequestProgress, updateRequestStatus]);

  const slides = useMemo(() => getSlides(metrics), [metrics]);

  const [index, setIndex] = useState(0);
  const [direction, setDirection] = useState(0);

  // Placeholder handlers for upcoming AI modules (Phase 3.3)
  const handleGenerateCMA = useCallback(() => {
    // Placeholder: to be implemented in Phase 3.3
    console.log('CMA Report generation is coming soon.');
    alert('CMA Report is coming soon.');
  }, []);

  const handleGenerateSocialPost = useCallback(() => {
    // Placeholder: to be implemented in Phase 3.3
    console.log('Social Post generation is coming soon.');
    alert('Social Post is coming soon.');
  }, []);

  const nextSlide = () => {
    setDirection(1);
    setIndex((i) => (i + 1) % slides.length);
  };
  
  const prevSlide = () => {
    setDirection(-1);
    setIndex((i) => (i - 1 + slides.length) % slides.length);
  };

  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => nextSlide(),
    onSwipedRight: () => prevSlide(),
    preventScrollOnSwipe: true,
    trackMouse: true,
  });

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 300 : -300,
      opacity: 0,
    }),
    center: {
      x: 0,
      opacity: 1,
    },
    exit: (direction: number) => ({
      x: direction < 0 ? 300 : -300,
      opacity: 0,
    }),
  };

  // Update metrics when requests change (real-time sync)
  useEffect(() => {
    const newMetrics = generateRealMetrics();
    setMetrics(newMetrics);
  }, [requests]);

  // Auto-refresh metrics every 30 seconds (less frequent since we have real-time sync)
  useEffect(() => {
    const interval = setInterval(() => {
      const newMetrics = generateRealMetrics();
      setMetrics(newMetrics);
    }, 30000);
    return () => clearInterval(interval);
  }, [requests]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') prevSlide();
      if (e.key === 'ArrowRight') nextSlide();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const brochureHeaderSubtitle = brochureListing
    ? `${brochureListing.title}${brochureListing.location ? ` - ${brochureListing.location}` : ''}`
    : undefined;

  useEffect(() => {
    if (brochureStatus !== 'success' || !brochureContent) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      openBrochureInViewer(brochureContent.contentId);
    }, 1500);

    return () => window.clearTimeout(timeoutId);
  }, [brochureStatus, brochureContent, openBrochureInViewer]);

  return (
    <>
      <div className="w-full min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      <div className="max-w-6xl mx-auto px-3 sm:px-6 lg:px-10 py-4 sm:py-6 lg:py-8 space-y-6 sm:space-y-8">
        {/* Header */}
        <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div>
            <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">Smart Dashboard</h1>
            <p className="text-gray-600 mt-1 text-sm sm:text-base">
              Manage your properties, clients, and AI workflows efficiently.
            </p>
          </div>
        </header>

        {/* Carousel */}
        <section
          {...swipeHandlers}
          role="region"
          aria-roledescription="carousel"
          aria-label="Featured actions carousel"
          className="relative overflow-hidden rounded-2xl bg-white shadow-lg p-4 sm:p-6 lg:p-8 touch-pan-y"
        >
          <div className="relative min-h-[260px] sm:min-h-[320px]">
            <AnimatePresence initial={false} custom={direction} mode="wait">
              <motion.div
                key={index}
                custom={direction}
                variants={slideVariants}
                initial="enter"
                animate="center"
                exit="exit"
                transition={{
                  x: { type: 'spring', stiffness: 300, damping: 30 },
                  opacity: { duration: 0.2 },
                }}
                className={`absolute inset-0 rounded-xl p-4 sm:p-6 lg:p-8 ${slides[index].color} flex flex-col ${slides[index].render ? 'justify-start' : 'justify-center'}`}
              >
                <h2 className="text-xl sm:text-2xl lg:text-3xl font-semibold text-gray-900 mb-2 sm:mb-3">
                  {slides[index].title}
                </h2>
                {slides[index].desc && (
                  <p className="text-gray-700 text-sm sm:text-base lg:text-lg mb-4 sm:mb-6 max-w-2xl">
                    {slides[index].desc}
                  </p>
                )}
                {slides[index].action && (
                  <button
                    className="inline-flex items-center justify-center px-4 sm:px-6 py-2 sm:py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md hover:shadow-lg w-fit text-sm sm:text-base"
                    aria-label={`${slides[index].action} for ${slides[index].title}`}
                  >
                    {slides[index].action}
                  </button>
                )}
                {slides[index].render && slides[index].render}
              </motion.div>
            </AnimatePresence>

            {/* Screen reader announcement */}
            <div className="sr-only" aria-live="polite" aria-atomic="true">
              Slide {index + 1} of {slides.length}: {slides[index].title}
            </div>
          </div>

          {/* Navigation Controls */}
          <button
            onClick={prevSlide}
            aria-label="Previous slide"
            className="absolute left-2 sm:left-3 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full shadow-md p-2 sm:p-3 hover:shadow-lg transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 z-10"
          >
            <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5 text-gray-700" />
          </button>
          <button
            onClick={nextSlide}
            aria-label="Next slide"
            className="absolute right-2 sm:right-3 top-1/2 -translate-y-1/2 bg-white/90 hover:bg-white rounded-full shadow-md p-2 sm:p-3 hover:shadow-lg transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 z-10"
          >
            <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5 text-gray-700" />
          </button>

          {/* Dot Indicators */}
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
            {slides.map((_, i) => (
              <button
                key={i}
                onClick={() => {
                  setDirection(i > index ? 1 : -1);
                  setIndex(i);
                }}
                aria-label={`Go to slide ${i + 1}`}
                className={`w-2 h-2 rounded-full transition-all ${
                  i === index
                    ? 'bg-blue-600 w-8'
                    : 'bg-gray-400 hover:bg-gray-500'
                }`}
              />
            ))}
          </div>
        </section>

        {/* Core Module Cards */}
        <section className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <Card title="Properties" desc="Browse and manage listings" icon={<Home className="w-6 h-6 text-blue-600" />} to="/properties" />
          {/* New AI Workflow tile matching existing style (placed early to ensure first-screen visibility) */}
          <CardButton
            title="AI Workflow"
            desc="Create brochure, CMA, or social"
            icon={<Zap className="w-6 h-6 text-yellow-500" />}
            onClick={() => navigate('/ai-workflow')}
          />
          <Card title="Contacts" desc="Manage clients and relationships" icon={<Users className="w-6 h-6 text-green-600" />} to="/contacts" />
          <Card title="Requests" desc="Track AI and workflow requests" icon={<ClipboardList className="w-6 h-6 text-orange-500" />} to="/requests" />
          <Card title="Marketing" desc="Create and manage campaigns" icon={<Megaphone className="w-6 h-6 text-purple-600" />} to="/marketing" />
        </section>

        {/* (Removed inline AI Workflows section to keep first view clean) */}
      </div>
    </div>

      <DevStatus />
      {/* AI Workflow uses a dedicated full page route; no Bottom Sheet */}
      <RefineModal
        isOpen={isBrochureModalOpen}
        onClose={handleCloseBrochureModal}
        variant="preview"
        headerTitle="Property Brochure Generator"
        headerSubtitle={brochureHeaderSubtitle}
      >
        <div className="space-y-4">
          <ProgressTracker
            currentStep={brochureStep}
            progress={brochureProgress}
            status={
              brochureStatus === 'error'
                ? 'error'
                : brochureStatus === 'success'
                ? 'success'
                : brochureStatus === 'processing'
                ? 'processing'
                : 'idle'
            }
            error={brochureStatus === 'error' ? (brochureError ?? 'Brochure generation failed.') : undefined}
            steps={BROCHURE_PROGRESS_STEPS}
          />
          {brochureStatus === 'processing' && brochureListing && (
            <div className="rounded-lg border border-blue-100 bg-blue-50 p-3 text-sm text-blue-700">
              Generating a brochure for <span className="font-semibold text-blue-900">{brochureListing.title}</span>
              {brochureListing.location ? ` - ${brochureListing.location}` : ''}.
            </div>
          )}
          {brochureStatus === 'error' && brochureError && (
            <div className="rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-700">
              {brochureError}
            </div>
          )}
          {brochureStatus === 'success' && brochureContent && brochureStructured && (
            <BrochurePreviewCard
              content={brochureContent}
              structured={brochureStructured}
              listing={brochureListing}
              onViewNow={() => openBrochureInViewer(brochureContent.contentId)}
            />
          )}
        </div>
      </RefineModal>
    </>
  );
}

interface CardProps {
  title: string;
  desc: string;
  icon: React.ReactNode;
  to: string;
}

interface BrochurePreviewCardProps {
  content: StoreIntelligenceContent;
  structured: BrochureStructuredData;
  listing?: SeededListing | null;
  onViewNow: () => void;
  isNavigating?: boolean;
}

function BrochurePreviewCard({ content, structured, listing, onViewNow, isNavigating = false }: BrochurePreviewCardProps) {
  const quickFacts = [
    structured.bedrooms ? { icon: <Bed className="w-4 h-4 text-blue-600" />, label: formatBedrooms(structured.bedrooms) ?? "" } : null,
    structured.bathrooms ? { icon: <Bath className="w-4 h-4 text-blue-600" />, label: formatBathrooms(structured.bathrooms) ?? "" } : null,
    structured.areaSqft ? { icon: <Ruler className="w-4 h-4 text-blue-600" />, label: formatSqft(structured.areaSqft) ?? "" } : null,
    structured.propertyType ? { icon: <FileText className="w-4 h-4 text-blue-600" />, label: structured.propertyType } : null,
  ].filter(Boolean) as Array<{ icon: React.ReactNode; label: string }>;

  const title = structured.title || content.title;
  const location = structured.location || listing?.location;
  const highlights = structured.highlights.slice(0, 3);

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">Preview Ready</p>
          <h4 className="text-lg font-semibold text-gray-900">{title}</h4>
          {structured.subtitle && (
            <p className="text-sm text-gray-500">{structured.subtitle}</p>
          )}
        </div>
        <div className="text-right space-y-1">
          {structured.price && (
            <p className="text-lg font-semibold text-blue-600">{structured.price}</p>
          )}
          {location && (
            <div className="flex items-center justify-end gap-1 text-sm text-gray-500">
              <MapPin className="w-3.5 h-3.5" />
              <span>{location}</span>
            </div>
          )}
        </div>
      </div>

      {quickFacts.length > 0 && (
        <div className="flex flex-wrap gap-3 text-xs text-gray-600">
          {quickFacts.map((fact, index) => (
            <span
              key={`${fact.label}-${index}`}
              className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 font-medium text-blue-700"
            >
              {fact.icon}
              {fact.label}
            </span>
          ))}
        </div>
      )}

      {highlights.length > 0 && (
        <div className="space-y-2">
          <h5 className="text-xs font-semibold uppercase tracking-wide text-gray-500">Highlights</h5>
          <ul className="space-y-1 text-sm text-gray-700">
            {highlights.map((highlight) => (
              <li key={highlight} className="flex items-start gap-2">
                <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-blue-500" />
                <span>{highlight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {structured.description && (
        <div className="rounded-lg border border-blue-100 bg-blue-50 p-3">
          <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-blue-700">
            <FileText className="w-4 h-4" />
            Overview
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">
            {structured.description.length > 340
              ? `${structured.description.slice(0, 337)}...`
              : structured.description}
          </p>
        </div>
      )}

      <button
        onClick={onViewNow}
        disabled={isNavigating}
        className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-wait disabled:bg-blue-300"
      >
        View full brochure
      </button>
    </div>
  );
}

interface QuickActionTileProps {
  title: string;
  desc: string;
  icon: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  loading?: boolean;
}

function QuickActionTile({ title, desc, icon, onClick, disabled = false, loading = false }: QuickActionTileProps) {
  return (
    <motion.button
      type="button"
      onClick={disabled ? undefined : onClick}
      whileHover={disabled ? undefined : { scale: 1.03, y: -4 }}
      whileTap={disabled ? undefined : { scale: 0.98 }}
      disabled={disabled}
      className={`w-full text-left ${disabled ? 'cursor-not-allowed opacity-90' : 'cursor-pointer'}`}
    >
      <div className="aspect-[4/3] p-3 sm:p-6 rounded-2xl bg-white shadow-md hover:shadow-xl transition-shadow flex flex-col justify-center space-y-2 sm:space-y-4 text-center sm:text-left border border-gray-100 hover:border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
        <div className="flex items-start justify-between sm:justify-start sm:gap-2">
          <div className="mx-auto sm:mx-0">
            {icon}
          </div>
          {loading && <Loader2 className="hidden sm:block w-4 h-4 animate-spin text-blue-500" />}
        </div>
        <div className="space-y-1">
          <h3 className="font-semibold text-sm sm:text-lg text-gray-900">{title}</h3>
          <p className="text-gray-600 text-xs sm:text-sm leading-relaxed">{desc}</p>
        </div>
        {loading && (
          <div className="flex items-center justify-center sm:hidden">
            <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
          </div>
        )}
      </div>
    </motion.button>
  );
}


 


function Card({ title, desc, icon, to }: CardProps) {
  return (
    <Link to={to} className="block">
      <motion.div
        whileHover={{ scale: 1.03, y: -4 }}
        whileTap={{ scale: 0.98 }}
        className="aspect-[4/3] p-3 sm:p-6 rounded-2xl bg-white shadow-md hover:shadow-xl transition-shadow cursor-pointer flex flex-col justify-center space-y-2 sm:space-y-4 text-center sm:text-left border border-gray-100 hover:border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        aria-label={`Navigate to ${title}`}
      >
        <div className="flex items-start justify-between sm:justify-start sm:gap-2">
          <div className="mx-auto sm:mx-0">
            {icon}
          </div>
          <CardChevron className="hidden sm:block w-4 h-4 sm:w-5 sm:h-5 text-gray-400" />
        </div>
        <div className="space-y-1">
          <h3 className="font-semibold text-sm sm:text-lg text-gray-900">{title}</h3>
          <p className="text-gray-600 text-xs sm:text-sm leading-relaxed">{desc}</p>
        </div>
      </motion.div>
    </Link>
  );
}

interface CardButtonProps {
  title: string;
  desc: string;
  icon: React.ReactNode;
  onClick: () => void;
}

function CardButton({ title, desc, icon, onClick }: CardButtonProps) {
  return (
    <button type="button" onClick={onClick} className="block w-full text-left">
      <motion.div
        whileHover={{ scale: 1.03, y: -4 }}
        whileTap={{ scale: 0.98 }}
        className="aspect-[4/3] p-3 sm:p-6 rounded-2xl bg-white shadow-md hover:shadow-xl transition-shadow cursor-pointer flex flex-col justify-center space-y-2 sm:space-y-4 text-center sm:text-left border border-gray-100 hover:border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        aria-label={`Open ${title}`}
      >
        <div className="flex items-start justify-between sm:justify-start sm:gap-2">
          <div className="mx-auto sm:mx-0">
            {icon}
          </div>
          <CardChevron className="hidden sm:block w-4 h-4 sm:w-5 sm:h-5 text-gray-400" />
        </div>
        <div className="space-y-1">
          <h3 className="font-semibold text-sm sm:text-lg text-gray-900">{title}</h3>
          <p className="text-gray-600 text-xs sm:text-sm leading-relaxed">{desc}</p>
        </div>
      </motion.div>
    </button>
  );
}

interface ActionButtonProps {
  icon: React.ReactNode;
  label: string;
  caption?: string;
  onClick: () => void;
  disabled?: boolean;
}

function ActionButton({ icon, label, caption, onClick, disabled = false }: ActionButtonProps) {
  return (
    <button
      type="button"
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
      className={`w-full text-left rounded-xl shadow-md hover:shadow-lg transition active:scale-[0.99] border border-gray-100 bg-white p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 ${disabled ? 'opacity-70 cursor-wait' : ''}`}
      aria-label={label}
    >
      <div className="flex items-center gap-3">
        <div>{icon}</div>
        <div className="flex-1">
          <div className="text-sm font-semibold text-gray-900">{label}</div>
          {caption && <div className="text-xs text-gray-600">{caption}</div>}
        </div>
      </div>
    </button>
  );
}
