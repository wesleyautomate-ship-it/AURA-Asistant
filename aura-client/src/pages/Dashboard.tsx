import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useSwipeable } from 'react-swipeable';
import { Link } from 'react-router-dom';
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
  TrendingUp
} from 'lucide-react';
import { generateKpiData, type KpiMetric } from '../services/mockData';

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
          <li>{metrics[0].value > 24 ? 'New listings added recently.' : 'Listings stable today.'}</li>
          <li>{metrics[1].value > 18 ? 'AI requests increasing — good momentum!' : 'AI activity normal.'}</li>
          <li>Engagement at {metrics[2].value}% ({metrics[2].delta >= '0' ? '+' : ''}{metrics[2].delta}% change).</li>
        </ul>
        <button className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm sm:text-base font-medium shadow-md hover:shadow-lg">
          View Full Briefing
        </button>
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
                  {deltaNum >= 0 ? <TrendingUp className="w-3 h-3" /> : '▼'}
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

export default function Dashboard() {
  const [metrics, setMetrics] = useState<KpiMetric[]>(() => {
    const saved = localStorage.getItem('aura_metrics');
    return saved ? JSON.parse(saved) : generateKpiData();
  });

  const [index, setIndex] = useState(0);
  const [direction, setDirection] = useState(0);

  const slides = getSlides(metrics);
  
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

  // Auto-refresh metrics every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      const next = generateKpiData();
      setMetrics(next);
      localStorage.setItem('aura_metrics', JSON.stringify(next));
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Load saved metrics on mount
  useEffect(() => {
    const saved = localStorage.getItem('aura_metrics');
    if (saved) {
      setMetrics(JSON.parse(saved));
    }
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') prevSlide();
      if (e.key === 'ArrowRight') nextSlide();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
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
          <Card title="Contacts" desc="Manage clients and relationships" icon={<Users className="w-6 h-6 text-green-600" />} to="/contacts" />
          <Card title="Requests" desc="Track AI and workflow requests" icon={<ClipboardList className="w-6 h-6 text-orange-500" />} to="/requests" />
          <Card title="Marketing" desc="Create and manage campaigns" icon={<Megaphone className="w-6 h-6 text-purple-600" />} to="/marketing" />
        </section>
      </div>
    </div>
  );
}

interface CardProps {
  title: string;
  desc: string;
  icon: React.ReactNode;
  to: string;
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
