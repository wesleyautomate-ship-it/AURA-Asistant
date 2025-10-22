import { useState, useRef, useEffect } from 'react';
import { Mic, Send, X, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface RefineModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit?: (prompt: string) => void;
  isProcessing?: boolean;
  taskTitle?: string;
  variant?: "refine" | "preview";
  headerTitle?: string;
  headerSubtitle?: string;
  children?: React.ReactNode;
}

export default function RefineModal({ 
  isOpen, 
  onClose, 
  onSubmit, 
  isProcessing = false,
  taskTitle = "content",
  variant = "refine",
  headerTitle,
  headerSubtitle,
  children
}: RefineModalProps) {
  const [prompt, setPrompt] = useState("");
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isRefineVariant = variant === "refine";

  useEffect(() => {
    if (isOpen && isRefineVariant && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isOpen, isRefineVariant]);

  useEffect(() => {
    if (isRefineVariant && !onSubmit) {
      console.warn("[RefineModal] onSubmit is required when using the refine variant.");
    }
  }, [isRefineVariant, onSubmit]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isRefineVariant || !onSubmit || !prompt.trim() || isProcessing) return;

    onSubmit(prompt.trim());
    setPrompt("");
  };

  const handleMicClick = () => {
    // TODO: Integrate with existing voice recording functionality
    setIsListening(!isListening);
    console.log("Voice input not yet implemented");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isRefineVariant) return;

    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      handleSubmit(e);
    }
  };

  if (!isOpen) return null;

  const resolvedTitle = headerTitle || (isRefineVariant ? "Refine with AI" : "Preview");
  const resolvedSubtitle = headerSubtitle || (isRefineVariant
    ? `Tell Aura what to adjust in your ${taskTitle}`
    : taskTitle ? String(taskTitle) : undefined);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end sm:items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className="w-full max-w-md bg-white rounded-t-2xl sm:rounded-2xl shadow-xl"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div>
              <h3 className="font-semibold text-gray-900">{resolvedTitle}</h3>
              {resolvedSubtitle && (
                <p className="text-sm text-gray-600">{resolvedSubtitle}</p>
              )}
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {isRefineVariant ? (
            <>
              {/* Form */}
              <form onSubmit={handleSubmit} className="p-4">
                <div className="space-y-4">
                  {/* Suggestion Pills */}
                  <div className="flex flex-wrap gap-2">
                    {[
                      "Make it more professional",
                      "Add more details", 
                      "Simplify the language",
                      "Focus on key points"
                    ].map((suggestion) => (
                      <button
                        key={suggestion}
                        type="button"
                        onClick={() => setPrompt(suggestion)}
                        className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>

                  {/* Input Area */}
                  <div className="relative">
                    <textarea
                      ref={textareaRef}
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Tell Aura what to adjust..."
                      className="w-full h-24 px-4 py-3 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={isProcessing}
                    />

                    {/* Voice Input Button */}
                    <button
                      type="button"
                      onClick={handleMicClick}
                      className={`absolute bottom-3 right-12 p-2 rounded-full transition-all ${
                        isListening 
                          ? "bg-red-500 text-white animate-pulse" 
                          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                      }`}
                    >
                      <Mic className="w-4 h-4" />
                    </button>

                    {/* Send Button */}
                    <button
                      type="submit"
                      disabled={!prompt.trim() || isProcessing || !onSubmit}
                      className="absolute bottom-3 right-3 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                      {isProcessing ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </button>
                  </div>

                  {/* Helper Text */}
                  <p className="text-xs text-gray-500">
                    Press Cmd/Ctrl + Enter to send - {prompt.length}/500 characters
                  </p>
                </div>
              </form>

              {/* Examples Section */}
              {!prompt && (
                <div className="px-4 pb-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 text-sm mb-2">Example prompts:</h4>
                    <ul className="space-y-1 text-sm text-gray-600">
                      <li>- "Make the tone more conversational"</li>
                      <li>- "Add specific examples and numbers"</li>
                      <li>- "Emphasize the investment opportunity"</li>
                      <li>- "Remove technical jargon"</li>
                    </ul>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="p-4 space-y-4">
              {children}
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
