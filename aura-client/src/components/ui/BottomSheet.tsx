import { useEffect, useRef, useCallback, type ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import Portal from './Portal';

export interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  initialHeight?: 'content' | 'half' | 'full';
}

const focusableSelectors = [
  'a[href]',
  'button:not([disabled])',
  'textarea:not([disabled])',
  'input:not([type="hidden"]):not([disabled])',
  'select:not([disabled])',
  '[tabindex]:not([tabindex="-1"])'
].join(',');

export default function BottomSheet({ isOpen, onClose, title, children, initialHeight = 'content' }: BottomSheetProps) {
  const sheetRef = useRef<HTMLDivElement>(null);
  const startScrollLockRef = useRef<string | null>(null);
  // Baseline Y offset for sheet; do not redeclare.
  const INITIAL_Y = initialHeight === 'full' ? '0%' : '100%';

  // Body scroll lock
  useEffect(() => {
    if (!isOpen) return;
    startScrollLockRef.current = document.body.style.overflow || '';
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = startScrollLockRef.current ?? '';
      startScrollLockRef.current = null;
    };
  }, [isOpen]);

  // Close on ESC
  useEffect(() => {
    if (!isOpen) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab') {
        const focusable = sheetRef.current?.querySelectorAll<HTMLElement>(focusableSelectors);
        if (!focusable || focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  // Auto-focus first focusable element when open
  useEffect(() => {
    if (!isOpen) return;
    const t = setTimeout(() => {
      const firstFocusable = sheetRef.current?.querySelector<HTMLElement>(focusableSelectors);
      firstFocusable?.focus();
    }, 50);
    return () => clearTimeout(t);
  }, [isOpen]);

  const handleDragEnd = useCallback((_: MouseEvent | TouchEvent | PointerEvent, info: { offset: { x: number; y: number } }) => {
    const height = sheetRef.current?.clientHeight ?? 0;
    if (info.offset.y > height * 0.25) {
      onClose();
    }
  }, [onClose]);

  return (
    <Portal>
      <AnimatePresence>{isOpen && (
        <>
          {/* Scrim */}
          <motion.div
            className="fixed inset-0 bg-black/40 z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.24 }}
            onClick={onClose}
            aria-hidden
          />

          {/* Sheet */}
          <motion.div
            ref={sheetRef}
            className="fixed inset-x-0 bottom-0 z-50 rounded-t-2xl bg-white shadow-2xl p-4 pb-[calc(16px+env(safe-area-inset-bottom))]"
            role="dialog"
            aria-modal="true"
            aria-label={title || 'Bottom Sheet'}
            initial={{ y: INITIAL_Y }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
            drag="y"
            dragDirectionLock
            dragConstraints={{ top: 0, bottom: 0 }}
            onDragEnd={handleDragEnd}
          >
            {/* Handle */}
            <div className="mx-auto mb-3 h-1.5 w-12 rounded-full bg-gray-300" />
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-base sm:text-lg font-semibold text-gray-900">{title}</h2>
              <button
                onClick={onClose}
                className="p-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Close"
              >
                <X className="w-5 h-5 text-gray-600" />
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-3">Choose an option</p>

            {children}
          </motion.div>
        </>
      )}</AnimatePresence>
    </Portal>
  );
}

