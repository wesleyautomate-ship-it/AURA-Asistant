import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Check, Share2, Copy, Download } from 'lucide-react';

interface BottomDockProps {
  onRefineWithAI: () => void;
  onApprove: () => void;
  onCopy: () => void;
  onShare?: () => void;
  onExportPDF?: () => void;
  isApproved?: boolean;
  isProcessing?: boolean;
}

export default function BottomDock({ 
  onRefineWithAI, 
  onApprove, 
  onCopy,
  onShare,
  onExportPDF,
  isApproved = false,
  isProcessing = false 
}: BottomDockProps) {
  
  const buttonBaseClasses = "flex items-center gap-1 px-2 py-1.5 text-xs sm:text-sm font-medium transition-all active:scale-95 disabled:cursor-not-allowed disabled:opacity-50 rounded-full whitespace-nowrap min-w-fit";

  return (
    <motion.div
      initial={{ y: 100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: 100, opacity: 0 }}
      transition={{ type: "spring", stiffness: 80, damping: 15 }}
      className="fixed bottom-[88px] sm:bottom-[16px] inset-x-0 z-40 flex justify-center px-3"
    >
      <div className="flex gap-1.5 overflow-x-auto scrollbar-hide bg-white dark:bg-neutral-900 shadow-lg shadow-slate-200/50 px-2 py-1.5 rounded-2xl backdrop-blur-lg bg-opacity-95 max-w-[calc(100vw-100px)] w-full justify-start sm:justify-center">
        
        {/* Refine with AI - Primary Action */}
        <button
          onClick={onRefineWithAI}
          disabled={isProcessing}
          className={`${buttonBaseClasses} bg-blue-600 text-white hover:bg-blue-700 disabled:bg-blue-400`}
        >
          <MessageSquare className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          <span className="hidden xs:inline">{isProcessing ? 'Refining...' : 'Refine'}</span>
          <span className="xs:hidden">{isProcessing ? '...' : 'AI'}</span>
        </button>

        {/* Approve - Success Action */}
        <button
          onClick={onApprove}
          disabled={isApproved || isProcessing}
          className={`${buttonBaseClasses} ${
            isApproved
              ? 'bg-green-100 text-green-700 cursor-default'
              : 'bg-green-600 text-white hover:bg-green-700'
          }`}
        >
          <Check className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          <span className="hidden sm:inline">{isApproved ? 'Approved' : 'Approve'}</span>
        </button>

        {/* Share - Secondary Action */}
        <button
          onClick={onShare}
          disabled={!onShare}
          className={`${buttonBaseClasses} border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-200 dark:hover:bg-neutral-700`}
        >
          <Share2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          <span className="hidden sm:inline">Share</span>
        </button>

        {/* Copy - Secondary Action */}
        <button
          onClick={onCopy}
          className={`${buttonBaseClasses} border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-200 dark:hover:bg-neutral-700`}
        >
          <Copy className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          <span className="hidden sm:inline">Copy</span>
        </button>

        {/* Export PDF - Secondary Action */}
        <button
          onClick={onExportPDF}
          disabled={!onExportPDF}
          className={`${buttonBaseClasses} border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-neutral-600 dark:bg-neutral-800 dark:text-neutral-200 dark:hover:bg-neutral-700`}
        >
          <Download className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          <span className="hidden sm:inline">Export</span>
        </button>

      </div>
    </motion.div>
  );
}