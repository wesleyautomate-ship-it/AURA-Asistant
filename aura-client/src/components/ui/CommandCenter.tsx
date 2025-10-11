import { motion, AnimatePresence } from 'framer-motion';
import { useCommandStore, Mode } from '../../store/commandStore';
import { Mic, Send, X, Bot, Loader2, Square, Pause, Play, MessageSquare, Trash2 } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { transcribeAudio, streamAIResponse } from '../../services/api';
import { orchestrateCommand } from '../../services/orchestrator';
import { generateContent, getGenerationStatus } from '../../services/orchestratorService';
import { startTaskSync, stopTaskSync, isTaskSyncActive } from '../../services/taskSync';
import { generateFollowUp, generateFollowUpCommand, shouldGenerateFollowUp, type FollowUpSuggestion } from '../../services/followupAgent';
import FollowUpCard from './FollowUpCard';
import { ProgressTracker } from './ProgressTracker';
import { ErrorDialog } from './ErrorDialog';

// Mode Toggle Component
function ModeToggle() {
  const { mode, setMode, reset } = useCommandStore();
  
  const handleModeChange = (newMode: Mode) => {
    setMode(newMode);
    reset();
  };

  return (
    <div 
      role="tablist" 
      aria-label="Input mode"
      className="grid grid-cols-2 w-40 bg-gray-100 rounded-xl p-1 text-xs font-medium mx-auto"
    >
      <button
        role="tab"
        aria-selected={mode === 'text'}
        onClick={() => handleModeChange('text')}
        className={`py-1.5 rounded-lg transition-all ${
          mode === 'text'
            ? 'bg-white shadow-sm text-gray-900'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        💬 Text
      </button>
      <button
        role="tab"
        aria-selected={mode === 'voice'}
        onClick={() => handleModeChange('voice')}
        className={`py-1.5 rounded-lg transition-all ${
          mode === 'voice'
            ? 'bg-white shadow-sm text-gray-900'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        🎙️ Voice
      </button>
    </div>
  );
}

// Voice UI Component with Simple Audio Recorder style
function VoiceUI() {
  const { 
    phase, setPhase, togglePause, addHistory, addResponse, addRequest, updateRequestStatus,
    sessionState, setRecording, setProcessing, setStreaming, updateSession
  } = useCommandStore();
  const BAR_COUNT = 24;
  const BASE_HEIGHT = 4; // px base height per bar
  const MAX_HEIGHT = 40; // px max height per bar
  const [barHeights, setBarHeights] = useState<number[]>(Array(BAR_COUNT).fill(BASE_HEIGHT));
  const [amplitude, setAmplitude] = useState(0);
  const [transcript, setTranscript] = useState('');
  const [showTranscript, setShowTranscript] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const rafRef = useRef<number | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  // --- Local ref for SSE cleanup ---
  const streamCleanupRef = useRef<(() => void) | null>(null);
  
  // Progress tracking state
  const [pipelineProgress, setPipelineProgress] = useState(0);
  const [pipelineStep, setPipelineStep] = useState<string>('idle');
  const [pipelineStatus, setPipelineStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [pipelineError, setPipelineError] = useState<string | undefined>();
  const [showErrorDialog, setShowErrorDialog] = useState(false);
  const [errorSuggestions, setErrorSuggestions] = useState<string[]>([]);
  const progressPollInterval = useRef<number | null>(null);
  
  // Progress polling functions
  const startProgressPolling = (requestId: string) => {
    console.log('[VoiceUI] Starting progress polling for:', requestId);
    
    // Clear any existing interval
    if (progressPollInterval.current) {
      clearInterval(progressPollInterval.current);
    }

    // Poll every 500ms
    progressPollInterval.current = window.setInterval(() => {
      const status = getGenerationStatus(requestId);
      
      if (status) {
        setPipelineProgress(status.progress || 0);
        setPipelineStep(status.currentStep || 'processing');
        
        // Stop polling when complete or error
        if (status.status === 'completed' || status.status === 'error') {
          console.log('[VoiceUI] Pipeline finished:', status.status);
          if (progressPollInterval.current) {
            clearInterval(progressPollInterval.current);
            progressPollInterval.current = null;
          }
          
          setPipelineStatus(status.status === 'completed' ? 'success' : 'error');
        }
      }
    }, 500);
  };

  const stopProgressPolling = () => {
    console.log('[VoiceUI] Stopping progress polling');
    if (progressPollInterval.current) {
      clearInterval(progressPollInterval.current);
      progressPollInterval.current = null;
    }
  };

  // Cleanup on unmount: ensure stream is closed and UI restored
  useEffect(() => {
    return () => {
      // Stop progress polling
      stopProgressPolling();
      
      if (streamCleanupRef.current) {
        console.log('[VoiceUI] Cleaning up active SSE stream on unmount');
        streamCleanupRef.current();
        streamCleanupRef.current = null;
      }
      document.body.style.overflow = 'auto';
      document.body.style.pointerEvents = 'auto';
    };
  }, []);

  // Setup microphone with real-time amplitude visualization
  useEffect(() => {
    if (phase !== 'listening') {
      setAmplitude(0);
      return;
    }

    let animationId: number;

    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        streamRef.current = stream;
        const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
        audioContextRef.current = ctx;
        const analyser = ctx.createAnalyser();
        const src = ctx.createMediaStreamSource(stream);
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.8;
        src.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const draw = () => {
          if (phase !== 'listening' && phase !== 'paused') return;

          analyser.getByteTimeDomainData(dataArray);
          
          // Calculate average amplitude from time-domain data
          let sum = 0;
          for (let i = 0; i < dataArray.length; i++) {
            const normalized = (dataArray[i] - 128) / 128; // -1 to 1
            sum += Math.abs(normalized);
          }
          const avg = sum / dataArray.length;
          
          // Update amplitude (0 to 1 range)
          if (phase === 'listening') {
            setAmplitude(Math.min(avg * 2, 1)); // amplify sensitivity
          }

          animationId = requestAnimationFrame(draw);
        };

        draw();
      })
      .catch((err) => {
        console.warn('Microphone access denied, using fallback animation:', err);
        
        // Fallback: mock amplitude animation
        const fallback = () => {
          if (phase === 'listening') {
            const mock = Math.sin(Date.now() / 200) * 0.5 + 0.5; // 0-1 sine wave
            setAmplitude(mock * 0.6); // gentler mock animation
          }
          animationId = requestAnimationFrame(fallback);
        };
        fallback();
      });

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    };
  }, [phase]);

  // Update bar heights based on amplitude
  useEffect(() => {
    if (phase === 'listening') {
      const updateBars = () => {
        setBarHeights((prev) =>
          prev.map((prevHeight, i) => {
            // Each bar reacts with slight phase offset
            const phaseOffset = Math.sin((Date.now() / 1000) + i * 0.2);
            const variance = 1 + phaseOffset * 0.15; // ±15% per bar
            const target = BASE_HEIGHT + amplitude * (MAX_HEIGHT - BASE_HEIGHT) * variance;
            
            // Smooth interpolation
            const smoothed = prevHeight + (target - prevHeight) * 0.3;
            return smoothed;
          })
        );
        rafRef.current = requestAnimationFrame(updateBars);
      };
      updateBars();
    } else if (phase === 'idle') {
      setBarHeights(Array(BAR_COUNT).fill(BASE_HEIGHT));
    }

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [phase, amplitude, BAR_COUNT, BASE_HEIGHT, MAX_HEIGHT]);

  // Phase actions
  const startRecording = () => {
    setPhase('listening');
    setRecording(true);
    updateSession({ recordingStartTime: Date.now() });
  };
  
  const stopRecording = async () => {
    setIsTranscribing(true);
    setPhase('thinking');
    setRecording(false);
    
    try {
      // Check if AURA mock mode is enabled
      const auraMockMode = import.meta.env.VITE_AURA_MOCK_MODE === 'true';
      
      let transcribedText: string;
      
      if (auraMockMode) {
        console.log('[VoiceUI] Using AURA mock transcription...');
        // Use new mock system directly
        const { simulateMockTranscription } = await import('../../mocks/transcriptionPrompts');
        transcribedText = await simulateMockTranscription();
      } else {
        console.log('[VoiceUI] Using real transcription API...');
        // For real mode, get actual audio blob from MediaRecorder
        // TODO: Implement actual audio recording capture
        const mockBlob = new Blob(['mock audio data'], { type: 'audio/webm' });
        transcribedText = await transcribeAudio(mockBlob);
      }
      
      if (transcribedText && transcribedText.trim()) {
        console.log('[VoiceUI] Transcription successful:', transcribedText);
        setTranscript(transcribedText);
        setPhase('stopped');
        setIsTranscribing(false);
        setShowTranscript(true);
      } else {
        throw new Error('Empty transcript response');
      }
    } catch (error) {
      console.error('[VoiceUI] Transcription failed:', error);
      // Ultimate fallback
      const mockTranscript = 'Generate a comprehensive CMA for Downtown Dubai with pricing trends and market analysis.';
      setTranscript(mockTranscript);
      setPhase('stopped');
      setIsTranscribing(false);
      setShowTranscript(true);
    }
  };
  
  const deleteRecording = () => {
    setPhase('idle');
    setBarHeights(Array(BAR_COUNT).fill(BASE_HEIGHT));
    setAmplitude(0);
    setTranscript('');
    setShowTranscript(false);
    setIsTranscribing(false);
    setRecording(false);
    updateSession({ recordingStartTime: undefined });
  };

  const sendCommand = async () => {
    let currentTranscript = transcript;
    
    // If we're still recording, stop recording first and get transcript
    if (phase === 'listening' || phase === 'paused') {
      console.log('[VoiceUI] Stopping recording and processing command');
      await stopRecording();
      // Wait a moment for transcript to be ready and get updated transcript
      await new Promise(resolve => setTimeout(resolve, 500));
      // Get the updated transcript from state after stopRecording completes
      const state = useCommandStore.getState();
      currentTranscript = transcript || 'Generate a comprehensive CMA for Downtown Dubai with pricing trends and market analysis.'; // Fallback
    }
    
    if (!currentTranscript?.trim()) {
      console.warn('[VoiceUI] No transcript available for sending, using fallback');
      currentTranscript = 'Generate a comprehensive CMA for Downtown Dubai with pricing trends and market analysis.';
    }
    
    console.log('[VoiceUI] Starting command processing:', currentTranscript);
    
    // Add request to queue
    const requestId = addRequest(currentTranscript);
    
    setPhase('thinking');
    setProcessing(true);
    updateSession({ currentTaskId: requestId, lastPrompt: currentTranscript });
    console.log('[VoiceUI] Phase changed → thinking');
    setShowTranscript(false);
    addHistory(currentTranscript, 'voice');
    
    // Lock scroll during processing
    document.body.style.overflow = 'hidden';
    
    // Short delay before starting orchestration
    setTimeout(async () => {
      try {
        // Close any existing stream before starting new one
        if (streamCleanupRef.current) {
          console.log('[VoiceUI] Closing previous stream before starting new one');
          streamCleanupRef.current();
          streamCleanupRef.current = null;
        }
        
        updateRequestStatus(requestId, 'Processing');
        console.log('[VoiceUI] Request status → Processing');
        setPhase('responding');
        setStreaming(true);
        console.log('[VoiceUI] Phase changed → responding');
        
        // Initialize progress tracking
        setPipelineStatus('processing');
        setPipelineProgress(0);
        setPipelineStep('normalizing');
        startProgressPolling(requestId);
        
        // Use new orchestrator
        console.log('[VoiceUI] Calling generateContent...');
        const result = await generateContent({
          userInput: currentTranscript,
          requestId,
        });
        console.log('[VoiceUI] Generation result:', result);
        
        if (!result.success) {
          throw new Error(result.error || 'Generation failed');
        }
        
        // Stop progress polling
        stopProgressPolling();
        setPipelineStatus('success');
        setPipelineProgress(100);
        setPipelineStep('completed');
        
        // Content is already saved by orchestrator
        console.log('[VoiceUI] Content ID:', result.contentId);
        
        let responseText = '';
        
        // Start streaming AI response
        console.log('[VoiceUI] Starting SSE stream...');
        streamCleanupRef.current = streamAIResponse(
          currentTranscript,
          // onChunk
          (chunk) => {
            responseText += chunk;
            addResponse(responseText);
          },
          // onComplete
          () => {
            console.log('[VoiceUI] Stream completed successfully');
            updateRequestStatus(requestId, 'Complete');
            console.log('[VoiceUI] Request status → Complete');
            setPhase('idle');
            setProcessing(false);
            setStreaming(false);
            updateSession({ currentTaskId: undefined, lastPrompt: null });
            console.log('[VoiceUI] Phase changed → idle');
            setBarHeights(Array(BAR_COUNT).fill(BASE_HEIGHT));
            setAmplitude(0);
            setTranscript('');
            setShowTranscript(false);
            
            // Restore scroll and pointer events
            document.body.style.overflow = 'auto';
            document.body.style.pointerEvents = 'auto';
            
            // Clear cleanup ref
            streamCleanupRef.current = null;
          },
          // onError
          (error) => {
            console.error('[VoiceUI] Stream error:', error);
            updateRequestStatus(requestId, 'Error', error.message);
            console.log('[VoiceUI] Request status → Error');
            
            // Restore scroll immediately on error
            document.body.style.overflow = 'auto';
            document.body.style.pointerEvents = 'auto';
            
            // Fallback to mock response
            const fallbackResponse = `Perfect! I'll create a detailed CMA for Downtown Dubai.

I'm analyzing:
• Current market pricing and AED/sqft trends
• Comparable properties and recent sales
• Days on market (DOM) statistics
• Inventory levels and absorption rates
• Future market predictions

Your CMA report will be ready shortly with all the insights you need.`;
            
            addResponse(fallbackResponse);
            setTimeout(() => {
              updateRequestStatus(requestId, 'Complete');
              console.log('[VoiceUI] Request status → Complete (fallback)');
              setPhase('idle');
              setProcessing(false);
              setStreaming(false);
              updateSession({ currentTaskId: undefined, lastPrompt: null });
              console.log('[VoiceUI] Phase changed → idle');
              setBarHeights(Array(BAR_COUNT).fill(BASE_HEIGHT));
              setAmplitude(0);
              setTranscript('');
              setShowTranscript(false);
              
              // Clear cleanup ref
              streamCleanupRef.current = null;
            }, 1000);
          }
        );
      } catch (error) {
        console.error('[VoiceUI] Generation failed:', error);
        stopProgressPolling();
        setPipelineStatus('error');
        setPipelineError(error instanceof Error ? error.message : 'Unknown error');
        setErrorSuggestions([
          'Try rephrasing your request with more details',
          'Ensure all required information is provided',
          'Check your internet connection',
        ]);
        setShowErrorDialog(true);
        
        updateRequestStatus(requestId, 'Error', error instanceof Error ? error.message : 'Unknown error');
        console.log('[VoiceUI] Request status → Error');
        
        // Restore UI on orchestration error
        document.body.style.overflow = 'auto';
        document.body.style.pointerEvents = 'auto';
        setPhase('idle');
        setProcessing(false);
        setStreaming(false);
        updateSession({ currentTaskId: undefined, lastPrompt: null });
        console.log('[VoiceUI] Phase changed → idle');
        setBarHeights(Array(BAR_COUNT).fill(BASE_HEIGHT));
        setAmplitude(0);
        setTranscript('');
        setShowTranscript(false);
      }
    }, 1200);
  };

  const isListening = phase === 'listening';
  const isPaused = phase === 'paused';
  const isStopped = phase === 'stopped';
  const isResponding = phase === 'responding' || phase === 'thinking';
  const isIdle = phase === 'idle';
  
  // Auto-switch back to waveform view when resuming recording
  useEffect(() => {
    if (isListening && showTranscript) {
      setShowTranscript(false);
    }
  }, [isListening, showTranscript]);

  // Session restoration: handle UI state when resuming from navigation
  useEffect(() => {
    if (sessionState.resumePending) {
      console.log('[VoiceUI] Resuming session with state:', sessionState);
      
      if (sessionState.isRecording && phase === 'idle') {
        console.log('[VoiceUI] Resuming recording session');
        setPhase('listening');
        setShowTranscript(false);
      }
      
      if (sessionState.isProcessing && !sessionState.isStreaming) {
        console.log('[VoiceUI] Resuming processing session');
        setPhase('thinking');
        setShowTranscript(false);
      }
      
      if (sessionState.isStreaming) {
        console.log('[VoiceUI] Resuming streaming session');
        setPhase('responding');
        setShowTranscript(false);
        if (sessionState.streamingText) {
          setTranscript(sessionState.streamingText);
          setShowTranscript(true);
        }
      }
      
      // Clear resume pending flag after restoration
      updateSession({ resumePending: false });
    }
  }, [sessionState, phase, updateSession]);

  return (
    <div className="w-full flex flex-col items-center pb-4">
      {/* Waveform / Transcription Container */}
      <div className="relative w-full h-24 mt-4 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <AnimatePresence mode="wait">
          {showTranscript ? (
            <motion.div
              key="transcript"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="h-full p-4 flex flex-col justify-center"
            >
              {isTranscribing ? (
                <div className="flex items-center justify-center gap-2 text-gray-500">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Transcribing...</span>
                </div>
              ) : (
                <>
                  <p className="text-sm text-gray-800 leading-relaxed max-h-[80px] overflow-y-auto">
                    {transcript || 'Listening...'}
                  </p>
                  {transcript && (
                    <div className="flex items-center gap-1 mt-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
                      <span className="text-xs text-gray-500">Transcribed</span>
                    </div>
                  )}
                </>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="waveform"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              transition={{ duration: 0.3 }}
              className="h-full flex items-center justify-center"
            >
              <motion.div
                className="flex items-center justify-center gap-[4px]"
                animate={{ opacity: isResponding ? 0.6 : 1 }}
                transition={{ duration: 0.3 }}
              >
                {barHeights.map((h, i) => (
                  <motion.div
                    key={i}
                    className="w-[3px] rounded-full bg-slate-800"
                    style={{ height: `${h}px` }}
                    transition={{
                      type: 'spring',
                      stiffness: 300,
                      damping: 30,
                    }}
                  />
                ))}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Transcription Toggle Button */}
        {(isListening || isPaused || isStopped) && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={() => setShowTranscript(!showTranscript)}
            className={`absolute top-2 right-2 p-1.5 rounded-md transition-colors ${
              showTranscript ? 'bg-gray-200 text-gray-700' : 'bg-gray-50 text-gray-500 hover:bg-gray-100 hover:text-gray-700'
            }`}
            title="View transcription"
          >
            <MessageSquare className="w-5 h-5" />
          </motion.button>
        )}

        {/* Recording Indicator */}
        {isListening && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="absolute top-2 left-3 flex items-center gap-1.5"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
            </span>
            <span className="text-xs font-medium text-gray-600">Recording</span>
          </motion.div>
        )}

        {/* Paused Indicator */}
        {isPaused && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="absolute top-2 left-3 flex items-center gap-1.5"
          >
            <Pause className="w-3 h-3 text-gray-600" />
            <span className="text-xs font-medium text-gray-600">Paused</span>
          </motion.div>
        )}
      </div>

      {/* Dynamic Button Layout */}
      <div className="flex gap-4 items-center justify-center mt-4">
        <AnimatePresence mode="wait">
          {isIdle && !isResponding && (
            <motion.button
              key="mic-button"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={startRecording}
              className="w-16 h-16 rounded-full bg-blue-500 text-white shadow-[0_2px_8px_rgba(59,130,246,0.3)] hover:bg-blue-600 transition-all flex items-center justify-center"
              aria-label="Start Recording"
            >
              <Mic className="w-7 h-7" />
            </motion.button>
          )}

          {(isListening || isPaused || isStopped) && !isResponding && (
            <motion.div
              key="control-buttons"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              transition={{ duration: 0.3 }}
              className="flex gap-3 items-center"
            >
              {/* Pause/Resume Button (only when recording or paused) */}
              {(isListening || isPaused) && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={togglePause}
                  className="w-14 h-14 rounded-full bg-gray-500 text-white shadow-[0_2px_6px_rgba(0,0,0,0.15)] hover:bg-gray-600 transition-all flex items-center justify-center"
                  aria-label={isPaused ? 'Resume Recording' : 'Pause Recording'}
                >
                  {isPaused ? <Play className="w-6 h-6" /> : <Pause className="w-6 h-6" />}
                </motion.button>
              )}

              {/* Stop Button (only when recording or paused) */}
              {(isListening || isPaused) && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={stopRecording}
                  className="w-14 h-14 rounded-full bg-red-500 text-white shadow-[0_2px_6px_rgba(0,0,0,0.15)] hover:bg-red-600 transition-all flex items-center justify-center"
                  aria-label="Stop Recording"
                >
                  <Square className="w-6 h-6 fill-current" />
                </motion.button>
              )}

              {/* Delete Button (only when stopped) */}
              {isStopped && (
                <motion.button
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={deleteRecording}
                  className="w-14 h-14 rounded-full bg-gray-500 text-white shadow-[0_2px_6px_rgba(0,0,0,0.15)] hover:bg-gray-600 transition-all flex items-center justify-center"
                  aria-label="Delete Recording"
                >
                  <Trash2 className="w-6 h-6" />
                </motion.button>
              )}

              {/* Send Button (always visible when controls are shown) */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={sendCommand}
                disabled={isResponding || (isStopped && !transcript)}
                className="w-14 h-14 rounded-full bg-blue-500 text-white shadow-[0_2px_6px_rgba(59,130,246,0.3)] hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center justify-center"
                aria-label={isListening || isPaused ? "Stop & Send Command" : "Send Command"}
              >
                <Send className="w-6 h-6" />
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Status Text */}
      <p className="text-center text-xs font-medium text-gray-600 mt-3">
        {sessionState.resumePending && '⏮️ Restoring session…'}
        {!sessionState.resumePending && isIdle && 'Tap mic to start recording'}
        {!sessionState.resumePending && isListening && 'Recording…'}
        {!sessionState.resumePending && isPaused && 'Paused'}
        {!sessionState.resumePending && isStopped && (transcript ? 'Review and send' : 'Processing...')}
        {!sessionState.resumePending && phase === 'thinking' && 'Aura is thinking…'}
        {!sessionState.resumePending && phase === 'responding' && 'Aura is crafting response…'}
      </p>
      
      {/* Transcription Mode Indicator */}
      <p className="text-center text-[10px] text-gray-400 mt-1">
        {import.meta.env.VITE_USE_REAL_TRANSCRIPTION === 'true' ? '🎙️ Real transcription' : '⚙️ Mock transcription'}
      </p>

      {/* Processing Card - replaced with Progress Tracker */}
      {isResponding && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full mt-4"
        >
          <ProgressTracker
            currentStep={pipelineStep}
            progress={pipelineProgress}
            status={pipelineStatus}
            error={pipelineError}
          />
        </motion.div>
      )}
    </div>
  );
}

// Main CommandCenter Component
export default function CommandCenter() {
  const { 
    isOpen, close, mode, addHistory, addResponse, addRequest, updateRequestStatus, linkTasks, requests,
    sessionState, restoreSession, cacheSession, setProcessing, setStreaming, updateSession
  } = useCommandStore();
  const [input, setInput] = useState('');
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [isSyncActive, setIsSyncActive] = useState(false);
  const [followUpSuggestion, setFollowUpSuggestion] = useState<FollowUpSuggestion | null>(null);
  const [isGeneratingFollowUp, setIsGeneratingFollowUp] = useState(false);
  const [isExecutingFollowUp, setIsExecutingFollowUp] = useState(false);
  const [showFollowUp, setShowFollowUp] = useState(false);
  const [pipelineProgress, setPipelineProgress] = useState(0);
  const [pipelineStep, setPipelineStep] = useState<string>('idle');
  const [pipelineStatus, setPipelineStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [pipelineError, setPipelineError] = useState<string | undefined>();
  const [showErrorDialog, setShowErrorDialog] = useState(false);
  const [errorSuggestions, setErrorSuggestions] = useState<string[]>([]);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const streamCleanupRef = useRef<(() => void) | null>(null);
  const followUpTimeoutRef = useRef<number | null>(null);
  const progressPollInterval = useRef<number | null>(null);

  // Progress polling functions
  const startProgressPolling = (requestId: string) => {
    console.log('[CommandCenter] Starting progress polling for:', requestId);
    
    // Clear any existing interval
    if (progressPollInterval.current) {
      clearInterval(progressPollInterval.current);
    }

    // Poll every 500ms
    progressPollInterval.current = window.setInterval(() => {
      const status = getGenerationStatus(requestId);
      
      if (status) {
        setPipelineProgress(status.progress || 0);
        setPipelineStep(status.currentStep || 'processing');
        
        // Stop polling when complete or error
        if (status.status === 'completed' || status.status === 'error') {
          console.log('[CommandCenter] Pipeline finished:', status.status);
          if (progressPollInterval.current) {
            clearInterval(progressPollInterval.current);
            progressPollInterval.current = null;
          }
          
          setPipelineStatus(status.status === 'completed' ? 'success' : 'error');
        }
      }
    }, 500);
  };

  const stopProgressPolling = () => {
    console.log('[CommandCenter] Stopping progress polling');
    if (progressPollInterval.current) {
      clearInterval(progressPollInterval.current);
      progressPollInterval.current = null;
    }
  };

  // Session lifecycle management
  useEffect(() => {
    // Restore session on mount
    console.log('[CommandCenter] Restoring session on mount');
    restoreSession();
    
    return () => {
      // Cache session on unmount
      console.log('[CommandCenter] Caching session on unmount');
      cacheSession();
    };
  }, [restoreSession, cacheSession]);

  // Monitor session state changes and cache them
  useEffect(() => {
    if (sessionState.isRecording || sessionState.isProcessing || sessionState.isStreaming) {
      cacheSession();
    }
  }, [sessionState.isRecording, sessionState.isProcessing, sessionState.isStreaming, cacheSession]);

  // Session restoration for text mode
  useEffect(() => {
    if (sessionState.resumePending && mode === 'text') {
      console.log('[CommandCenter] Resuming text session with state:', sessionState);
      
      if (sessionState.isProcessing) {
        setIsStreaming(true);
        console.log('[CommandCenter] Resuming processing in text mode');
      }
      
      if (sessionState.isStreaming && sessionState.streamingText) {
        setStreamingText(sessionState.streamingText);
        setIsStreaming(true);
        console.log('[CommandCenter] Resuming streaming in text mode');
      }
      
      if (sessionState.lastPrompt) {
        setInput(sessionState.lastPrompt);
        console.log('[CommandCenter] Restored last prompt:', sessionState.lastPrompt);
      }
    }
  }, [sessionState, mode]);

  // Task sync lifecycle management
  useEffect(() => {
    // Start task sync when component mounts
    startTaskSync();
    setIsSyncActive(true);
    
    return () => {
      // Stop task sync on unmount
      stopTaskSync();
      setIsSyncActive(false);
    };
  }, []);

  // Check sync status periodically for UI indicator
  useEffect(() => {
    const checkSyncStatus = () => {
      setIsSyncActive(isTaskSyncActive());
    };
    
    const interval = setInterval(checkSyncStatus, 2000); // Check every 2 seconds
    return () => clearInterval(interval);
  }, []);

  // Reset follow-up state when mode changes to prevent stale cards
  useEffect(() => {
    console.log('[CommandCenter] Mode changed to:', mode);
    setFollowUpSuggestion(null);
    setIsGeneratingFollowUp(false);
    setIsExecutingFollowUp(false);
    setShowFollowUp(false);
    
    // Clear any existing timeout
    if (followUpTimeoutRef.current) {
      clearTimeout(followUpTimeoutRef.current);
      followUpTimeoutRef.current = null;
    }
  }, [mode]);

  // Follow-up generation function
  const generateFollowUpSuggestion = async (completedTaskId: string) => {
    const completedTask = requests.find(req => req.id === completedTaskId);
    if (!completedTask || !shouldGenerateFollowUp(completedTask)) {
      return;
    }

    setIsGeneratingFollowUp(true);
    try {
      console.log('[CommandCenter] Generating follow-up for task:', completedTask.title);
      const suggestion = await generateFollowUp(completedTask);
      
      if (suggestion) {
        setFollowUpSuggestion(suggestion);
        console.log('[CommandCenter] Follow-up suggestion generated:', suggestion.message);
      }
    } catch (error) {
      console.error('[CommandCenter] Failed to generate follow-up:', error);
    } finally {
      setIsGeneratingFollowUp(false);
    }
  };

  // Handle follow-up acceptance
  const handleFollowUpAccept = async () => {
    if (!followUpSuggestion) return;

    setIsExecutingFollowUp(true);
    try {
      // Generate command text for the follow-up
      const command = generateFollowUpCommand(followUpSuggestion);
      
      // Add the follow-up request
      const followUpId = addRequest(
        command,
        followUpSuggestion.intent as any,
        followUpSuggestion.actionData,
        followUpSuggestion.parentId
      );

      // Link the tasks
      linkTasks(followUpSuggestion.parentId, followUpId);

      // Start orchestration for the follow-up
      console.log('[CommandCenter] Executing follow-up:', command);
      await orchestrateCommand(command, followUpSuggestion.parentId);
      
      // Clear the suggestion
      setFollowUpSuggestion(null);
    } catch (error) {
      console.error('[CommandCenter] Failed to execute follow-up:', error);
    } finally {
      setIsExecutingFollowUp(false);
    }
  };


  // Monitor request status changes to trigger follow-ups
  useEffect(() => {
    const completedRequests = requests.filter(req => req.status === 'Complete');
    
    // Check for newly completed tasks that need follow-ups
    completedRequests.forEach(req => {
      if (shouldGenerateFollowUp(req) && !followUpSuggestion) {
        generateFollowUpSuggestion(req.id);
      }
    });
  }, [requests, followUpSuggestion]);

  // Contextual visibility logic for follow-up cards
  useEffect(() => {
    // Clear any existing timeout
    if (followUpTimeoutRef.current) {
      clearTimeout(followUpTimeoutRef.current);
      followUpTimeoutRef.current = null;
    }

    // Check if we should show the follow-up card
    const hasQualitySuggestion = followUpSuggestion && followUpSuggestion.confidence >= 0.6;
    const notBusyProcessing = !isStreaming && !isGeneratingFollowUp;
    
    // Show in both voice and text modes when not actively processing
    const shouldShow = hasQualitySuggestion && notBusyProcessing;

    if (shouldShow) {
      console.log('[FollowUp] Showing contextual follow-up card:', followUpSuggestion.message);
      setShowFollowUp(true);
      
      // Auto-dismiss after 10 seconds
      followUpTimeoutRef.current = window.setTimeout(() => {
        console.log('[FollowUp] Auto-dismiss triggered after 10 seconds');
        setShowFollowUp(false);
        followUpTimeoutRef.current = null;
      }, 10000);
    } else {
      setShowFollowUp(false);
    }

    return () => {
      if (followUpTimeoutRef.current) {
        clearTimeout(followUpTimeoutRef.current);
        followUpTimeoutRef.current = null;
      }
    };
  }, [followUpSuggestion, isStreaming, isGeneratingFollowUp, mode]);

  // Development logging for follow-up visibility states
  useEffect(() => {
    console.info('[FollowUp Debug]', {
      showFollowUp,
      hasFollowUp: !!followUpSuggestion,
      confidence: followUpSuggestion?.confidence,
      mode,
      isStreaming,
      isGeneratingFollowUp
    });
  }, [showFollowUp, followUpSuggestion, mode, isStreaming, isGeneratingFollowUp]);

  // Cleanup on unmount: ensure stream is closed and scroll is restored
  useEffect(() => {
    return () => {
      // Stop progress polling
      stopProgressPolling();
      
      // Cleanup streaming connection if active
      if (streamCleanupRef.current) {
        console.log('[CommandCenter] Cleaning up stream on unmount');
        streamCleanupRef.current();
        streamCleanupRef.current = null;
      }
      // Restore scroll
      document.body.style.overflow = 'auto';
      document.body.style.pointerEvents = 'auto';
    };
  }, []);

  // Simulate AI response streaming
  const simulateStreaming = (fullText: string) => {
    setIsStreaming(true);
    setStreamingText('');
    let index = 0;

    const interval = setInterval(() => {
      if (index < fullText.length) {
        setStreamingText((prev) => prev + fullText[index]);
        index++;
      } else {
        clearInterval(interval);
        setIsStreaming(false);
      }
    }, 30);

    return () => clearInterval(interval);
  };

  // Handle text command submission
  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const command = input.trim();
    console.log('[CommandCenter] Starting command processing:', command);
    
    // Add request to queue
    const requestId = addRequest(command);
    
    // Update session state for background continuation
    setProcessing(true);
    updateSession({ currentTaskId: requestId, lastPrompt: command });
    
    addHistory(command, 'text');
    setInput('');

    setIsStreaming(true);
    setStreamingText('');
    
    // Lock scroll during processing
    document.body.style.overflow = 'hidden';
    
    // Short delay before processing
    setTimeout(async () => {
      try {
        // Close any existing stream before starting new one
        if (streamCleanupRef.current) {
          console.log('[CommandCenter] Closing previous stream before starting new one');
          streamCleanupRef.current();
          streamCleanupRef.current = null;
        }
        
        updateRequestStatus(requestId, 'Processing');
        setStreaming(true);
        console.log('[CommandCenter] Request status → Processing');
        
        // Initialize progress tracking
        setPipelineStatus('processing');
        setPipelineProgress(0);
        setPipelineStep('normalizing');
        startProgressPolling(requestId);
        
        // Use new orchestrator
        console.log('[CommandCenter] Calling generateContent...');
        const result = await generateContent({
          userInput: command,
          requestId,
        });
        
        if (!result.success) {
          throw new Error(result.error || 'Generation failed');
        }
        
        stopProgressPolling();
        setPipelineStatus('success');
        setPipelineProgress(100);
        
        console.log('[CommandCenter] Content ID:', result.contentId);
        console.log('[CommandCenter] Logs:', result.logs);
        
        let responseText = '';
        
        // Start streaming AI response
        console.log('[CommandCenter] Starting SSE stream...');
        streamCleanupRef.current = streamAIResponse(
          command,
          // onChunk
          (chunk) => {
            responseText += chunk;
            setStreamingText(responseText);
          },
          // onComplete
          () => {
            console.log('[CommandCenter] Stream completed successfully');
            addResponse(responseText);
            updateRequestStatus(requestId, 'Complete');
            console.log('[CommandCenter] Request status → Complete');
            setIsStreaming(false);
            setProcessing(false);
            setStreaming(false);
            updateSession({ currentTaskId: undefined, lastPrompt: null });
            
            // Restore scroll and pointer events
            document.body.style.overflow = 'auto';
            document.body.style.pointerEvents = 'auto';
            
            // Clear cleanup ref
            streamCleanupRef.current = null;
          },
          // onError
          (error) => {
            console.error('[CommandCenter] Stream error:', error);
            updateRequestStatus(requestId, 'Error', error.message);
            console.log('[CommandCenter] Request status → Error');
            
            // Restore scroll immediately on error
            document.body.style.overflow = 'auto';
            document.body.style.pointerEvents = 'auto';
            
            // Fallback to mock response
            const fallbackResponse = `Perfect! I'll help you with "${command}".

Here's what I can do:
• Analyze market trends and pricing
• Generate comprehensive CMA reports
• Create compelling listing presentations
• Provide detailed property valuations
• Automate marketing campaigns

Would you like me to proceed?`;

            addResponse(fallbackResponse);
            simulateStreaming(fallbackResponse);
            updateRequestStatus(requestId, 'Complete');
            setProcessing(false);
            setStreaming(false);
            updateSession({ currentTaskId: undefined, lastPrompt: null });
            console.log('[CommandCenter] Request status → Complete (fallback)');
            
            // Clear cleanup ref
            streamCleanupRef.current = null;
          }
        );
      } catch (error) {
        console.error('[CommandCenter] Generation failed:', error);
        stopProgressPolling();
        setPipelineStatus('error');
        setPipelineError(error instanceof Error ? error.message : 'Unknown error');
        setErrorSuggestions([
          'Try rephrasing your request with more details',
          'Ensure all required information is provided',
          'Check your internet connection',
        ]);
        setShowErrorDialog(true);
        
        updateRequestStatus(requestId, 'Error', error instanceof Error ? error.message : 'Unknown error');
        console.log('[CommandCenter] Request status → Error');
        
        // Restore UI on orchestration error
        document.body.style.overflow = 'auto';
        document.body.style.pointerEvents = 'auto';
        setIsStreaming(false);
        setProcessing(false);
        setStreaming(false);
        updateSession({ currentTaskId: undefined, lastPrompt: null });
      }
    }, 500);
  };

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        close();
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter' && isOpen && mode === 'text') {
        e.preventDefault();
        handleSend();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, close, mode, input, isStreaming]);

  // Focus input when opening in text mode
  useEffect(() => {
    if (isOpen && mode === 'text' && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen, mode]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop - Mobile only */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={close}
        className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
      />

      {/* Command Center Panel - Above Bottom Nav */}
      <motion.div
        initial={{ opacity: 0, y: 80 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 80 }}
        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        className="fixed bottom-[5rem] left-0 right-0 md:bottom-[4.5rem] lg:right-8 lg:bottom-[3.5rem] mx-auto max-w-md bg-white/95 backdrop-blur-sm rounded-3xl shadow-[0_-6px_16px_rgba(0,0,0,0.08)] border border-gray-200 z-50 flex flex-col items-center pointer-events-auto"
        style={{ paddingBottom: 'calc(env(safe-area-inset-bottom) + 2rem)' }}
      >
        {/* Header */}
        <div className="w-full flex items-center justify-between mb-4 px-6 pt-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-100 to-purple-100 rounded-xl">
              <Bot className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="font-semibold text-gray-900 text-sm">Aura</h2>
              <p className="text-xs text-gray-500">Voice-first AI assistant</p>
            </div>
          </div>
          <button
            onClick={close}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close Command Center"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Mode Toggle */}
        <div className="w-full mb-5 px-6">
          <ModeToggle />
        </div>

        {/* Content Area */}
        <div className="w-full px-6 pb-2">
          {mode === 'voice' ? (
            <VoiceUI />
          ) : (
            <>
              {/* Text Input */}
              <textarea
                ref={inputRef}
                disabled={isStreaming}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Ask Aura anything..."
                rows={4}
                className="w-full p-4 border border-gray-200 rounded-xl text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500 mb-3"
              />

              <p className="text-xs text-gray-400 text-right mb-4">
                ⌘ + Enter to send
              </p>

              {/* Send Button */}
              <button
                onClick={handleSend}
                disabled={!input.trim() || isStreaming}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm font-medium transition-all shadow-lg"
              >
                {isStreaming ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Thinking...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Send
                  </>
                )}
              </button>

              {/* Response Container */}
              {(isStreaming || streamingText) && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-blue-100"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-white rounded-lg shadow-sm">
                      <Bot className="w-4 h-4 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                        {streamingText}
                        {isStreaming && (
                          <motion.span
                            animate={{ opacity: [1, 0] }}
                            transition={{ duration: 0.8, repeat: Infinity }}
                            className="inline-block w-0.5 h-4 bg-blue-600 ml-1"
                          />
                        )}
                      </p>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Progress Tracker for Text Mode */}
              {(pipelineStatus === 'processing' || pipelineStatus === 'success' || pipelineStatus === 'error') && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4"
                >
                  <ProgressTracker
                    currentStep={pipelineStep}
                    progress={pipelineProgress}
                    status={pipelineStatus}
                    error={pipelineError}
                  />
                </motion.div>
              )}

            </>
          )}
          
          {/* Contextual Follow-up Suggestion Card */}
          <AnimatePresence>
            {showFollowUp && followUpSuggestion && (
              <motion.div
                key="followup-card"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 8 }}
                transition={{ duration: 0.25, ease: 'easeOut' }}
              >
                <FollowUpCard
                  suggestion={followUpSuggestion}
                  onAccept={handleFollowUpAccept}
                  onDismiss={() => {
                    console.log('[FollowUp] Dismissed by user');
                    setShowFollowUp(false);
                    if (followUpTimeoutRef.current) {
                      clearTimeout(followUpTimeoutRef.current);
                      followUpTimeoutRef.current = null;
                    }
                  }}
                  isGenerating={isGeneratingFollowUp}
                  isExecuting={isExecutingFollowUp}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        
        {/* Mock Mode Indicator */}
        {import.meta.env.VITE_AURA_MOCK_MODE === 'true' && (
          <div className="w-full px-6 pb-2">
            <p className="text-center text-[10px] text-orange-500 italic flex items-center justify-center gap-1">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-pulse inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-orange-500"></span>
              </span>
              ⚙️ Mock Transcription Mode Active
            </p>
          </div>
        )}
        
        {/* Sync Status Indicator */}
        <div className="w-full px-6 pb-6">
          <p className="text-center text-[10px] text-gray-400 flex items-center justify-center gap-1">
            {isSyncActive ? (
              <>
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
                </span>
                🔄 Live sync active
              </>
            ) : (
              <>
                <span className="inline-flex h-1.5 w-1.5 rounded-full bg-gray-400"></span>
                🔄 Sync offline
              </>
            )}
          </p>
        </div>
      </motion.div>
      
      {/* Error Dialog */}
      <ErrorDialog
        isOpen={showErrorDialog}
        error={pipelineError || 'An unknown error occurred'}
        onRetry={() => {
          setShowErrorDialog(false);
          // Retry logic will be handled in handleSend update
        }}
        onDismiss={() => setShowErrorDialog(false)}
        suggestions={errorSuggestions}
      />
    </>
  );
}
