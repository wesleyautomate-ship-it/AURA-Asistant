import { Plus } from 'lucide-react';
import { motion } from 'framer-motion';
import { useCommandStore } from '../../store/commandStore';

export default function CommandFab() {
  const { open } = useCommandStore();

  return (
    <motion.button
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ delay: 0.3, type: 'spring', stiffness: 200 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      onClick={open}
      aria-label="Open Command Center"
      className="fixed bottom-20 right-5 lg:bottom-6 lg:right-8 bg-gradient-to-br from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-xl hover:shadow-2xl transition-shadow z-50 group"
    >
      <Plus className="w-6 h-6 transition-transform group-hover:rotate-90" />
      
      {/* Tooltip */}
      <span className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
        AI Command Center
      </span>
    </motion.button>
  );
}
