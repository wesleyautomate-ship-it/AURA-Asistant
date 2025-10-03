import React, { useEffect, useMemo, useRef, useState } from 'react';
import { ACTION_ITEMS } from '../constants.tsx';
import type { CommandMode, CommandStatus } from '../store/uiStore';
import type { CommandRequest } from '../types';
import { audioService, type AudioRecordingResult } from '../services/audioService';
import WaveformVisualizer from './WaveformVisualizer.tsx';

interface CommandContext {
  commandMode: CommandMode;
  commandStatus: CommandStatus;
  commandText: string;
  commandTranscript: string;
  commandError: string | null;
}

interface Props {
  onClose: () => void;
  onModeChange: (mode: CommandMode) => void;
  onStatusChange: (status: CommandStatus) => void;
  onTextChange: (text: string) => void;
  onTranscriptChange: (transcript: string) => void;
  onSubmit: (request: CommandRequest) => Promise<void> | void;
  context: CommandContext;
}

const QUICK_ACTIONS = [
  'Generate listing campaign',
  'Prep for pricing analysis',
  'Draft client follow-up email',
  'Plan social media week',
];

function formatDuration(ms: number): string {
  const totalSeconds = Math.max(0, Math.round(ms / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

const WAVEFORM_BUCKETS = 48;
const createZeroLevels = () => Array(WAVEFORM_BUCKETS).fill(0);

const CommandCenter: React.FC<Props> = ({
  onClose,
  onModeChange,
  onStatusChange,
  onTextChange,
  onTranscriptChange,
  onSubmit,
  context,
}) => {
  const { commandMode, commandStatus, commandText, commandTranscript, commandError } = context;
  const [recording, setRecording] = useState<AudioRecordingResult | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [supportError, setSupportError] = useState<string | null>(null);
  const [waveformLevels, setWaveformLevels] = useState<number[]>(() => createZeroLevels());
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (commandStatus !== 'recording') {
      setElapsed(recording?.duration ?? 0);
      return;
    }

    setElapsed(audioService.getRecordingDuration());
    const timer = setInterval(() => {
      setElapsed(audioService.getRecordingDuration());
    }, 200);

    return () => {
      clearInterval(timer);
    };
  }, [commandStatus, recording]);

  useEffect(() => {
    if (commandStatus !== 'recording') {
      setWaveformLevels(createZeroLevels());
      return;
    }

    if (typeof window === 'undefined' || typeof window.AudioContext === 'undefined') {
      return;
    }

    const stream = audioService.getCurrentStream();
    if (!stream) {
      return;
    }

    const AudioContextCtor: typeof AudioContext = window.AudioContext || (window as any).webkitAudioContext;
    const context = audioContextRef.current ?? new AudioContextCtor();
    audioContextRef.current = context;

    if (context.state === 'suspended') {
      void context.resume().catch(() => undefined);
    }

    const source = context.createMediaStreamSource(stream);
    sourceNodeRef.current = source;

    const analyser = context.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.8;
    source.connect(analyser);
    analyserRef.current = analyser;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const bucketSize = Math.max(1, Math.floor(bufferLength / WAVEFORM_BUCKETS));

    const updateWaveform = () => {
      analyser.getByteFrequencyData(dataArray);
      const levels = Array.from({ length: WAVEFORM_BUCKETS }, (_, idx) => {
        const start = idx * bucketSize;
        const end = Math.min(start + bucketSize, bufferLength);
        let sum = 0;
        for (let i = start; i < end; i += 1) {
          sum += dataArray[i];
        }
        const average = sum / (end - start || 1);
        return average / 255;
      });
      setWaveformLevels(levels);
      animationFrameRef.current = requestAnimationFrame(updateWaveform);
    };

    updateWaveform();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      try {
        source.disconnect();
      } catch (error) {
        console.warn('Waveform source disconnect failed', error);
      }
      if (analyserRef.current) {
        try {
          analyserRef.current.disconnect();
        } catch (error) {
          console.warn('Waveform analyser disconnect failed', error);
        }
        analyserRef.current = null;
      }
      sourceNodeRef.current = null;
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        void audioContextRef.current.close().catch(() => undefined);
      }
      audioContextRef.current = null;
    };
  }, [commandStatus]);

  useEffect(() => () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      void audioContextRef.current.close().catch(() => undefined);
    }
  }, []);

  const quickActionItems = useMemo(() => ACTION_ITEMS.slice(0, 6), []);

  const handleModeToggle = (mode: CommandMode) => {
    if (mode === commandMode) {
      return;
    }

    onModeChange(mode);

    if (mode === 'audio') {
      setRecording(null);
      onTranscriptChange('');
      onStatusChange('idle');
      setSupportError(null);
    } else {
      onStatusChange(commandText.trim().length > 0 ? 'typing' : 'idle');
    }
  };

  const startRecording = async () => {
    setSupportError(null);
    if (!audioService.isMediaRecorderSupported() || !audioService.isGetUserMediaSupported()) {
      setSupportError('Voice capture is not supported on this device.');
      onStatusChange('idle');
      return;
    }

    try {
      await audioService.startRecording();
      onStatusChange('recording');
      setRecording(null);
      onTranscriptChange('');
    } catch (error) {
      console.error('Failed to start recording', error);
      setSupportError('Unable to access microphone. Please check permissions.');
      onStatusChange('idle');
    }
  };

  const stopRecording = async () => {
    try {
      const result = await audioService.stopRecording();
      setRecording(result);
      onStatusChange('reviewing');
      if (!commandTranscript) {
        onTranscriptChange('');
      }
    } catch (error) {
      console.error('Failed to stop recording', error);
      setSupportError('Recording failed. Please try again.');
      onStatusChange('idle');
    }
  };

  const resetAudio = () => {
    setRecording(null);
    onTranscriptChange('');
    onStatusChange('idle');
    setSupportError(null);
  };

  const handleTranscriptChange = (value: string) => {
    onTranscriptChange(value);
    if (commandStatus !== 'reviewing') {
      onStatusChange('reviewing');
    }
  };

  const sendAudio = () => {
    if (!recording) {
      return;
    }

    void onSubmit({
      kind: 'audio',
      transcript: commandTranscript,
      mimeType: recording.mimeType,
      duration: recording.duration,
      audioBlob: recording.audioBlob,
    });
  };

  const handleTextChange = (value: string) => {
    onTextChange(value);
    onStatusChange(value.trim().length > 0 ? 'typing' : 'idle');
  };

  const handleQuickAction = (label: string) => {
    const nextValue = `${commandText ? `${commandText}
` : ''}${label}`;
    handleTextChange(nextValue);
  };

  const sendText = () => {
    const trimmed = commandText.trim();
    if (!trimmed) {
      return;
    }

    void onSubmit({
      kind: 'text',
      prompt: trimmed,
      quickAction: null,
    });
  };

  const renderAudioMode = () => (
    <div className="rounded-2xl bg-slate-900 p-5 text-white shadow-inner">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-white/60">Record your instructions</p>
          <p className="text-lg font-semibold">Voice Command</p>
        </div>
        <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium">
          {formatDuration(elapsed)}
        </span>
      </div>

      <div className="flex flex-col items-center justify-center gap-4">
        <WaveformVisualizer levels={waveformLevels} isActive={commandStatus === 'recording'} />

        <div className="flex flex-wrap items-center gap-3">
          {commandStatus === 'recording' ? (
            <button
              type="button"
              onClick={stopRecording}
              className="rounded-full bg-white/90 px-6 py-2 text-sm font-semibold text-slate-900 shadow"
            >
              Stop
            </button>
          ) : (
            <button
              type="button"
              onClick={startRecording}
              className="rounded-full bg-red-500 px-6 py-2 text-sm font-semibold text-white shadow hover:bg-red-400"
            >
              {recording ? 'Re-record' : 'Start Recording'}
            </button>
          )}

          {recording && (
            <>
              <button
                type="button"
                onClick={resetAudio}
                className="rounded-full bg-white/10 px-4 py-2 text-sm font-medium text-white hover:bg-white/20"
              >
                Delete
              </button>
              <button
                type="button"
                onClick={sendAudio}
                className="rounded-full bg-blue-400 px-5 py-2 text-sm font-semibold text-white shadow hover:bg-blue-300"
              >
                Send
              </button>
            </>
          )}
        </div>

        {supportError && <p className="text-xs text-red-300">{supportError}</p>}
        {commandError && <p className="text-xs text-orange-200">{commandError}</p>}
        {(recording || commandTranscript) && (
          <textarea
            value={commandTranscript}
            onChange={(event) => handleTranscriptChange(event.target.value)}
            placeholder="Optional: add notes or correct the transcript"
            className="mt-3 w-full rounded-xl border border-white/30 bg-white/10 px-4 py-3 text-sm text-white placeholder:text-white/60 focus:border-white focus:outline-none"
          />
        )}
      </div>
    </div>
  );

  const renderTextMode = () => (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Compose prompt</p>
          <p className="text-lg font-semibold text-slate-900">Text Command</p>
        </div>
        <button
          type="button"
          onClick={sendText}
          disabled={!commandText.trim() || commandStatus === 'processing'}
          className="rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          Send
        </button>
      </div>

      <textarea
        value={commandText}
        onChange={(event) => handleTextChange(event.target.value)}
        placeholder="Tell PropertyPro AI what to do next"
        className="h-32 w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
      />

      <div className="mt-3 flex flex-wrap gap-2">
        {QUICK_ACTIONS.map((action) => (
          <button
            key={action}
            type="button"
            onClick={() => handleQuickAction(action)}
            className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-200"
          >
            {action}
          </button>
        ))}
      </div>

      {commandError && <p className="mt-3 text-xs text-red-500">{commandError}</p>}
    </div>
  );

  return (
    <div className="fixed inset-0 z-40 flex items-end justify-center bg-slate-900/40 backdrop-blur-sm sm:items-center">
      <div className="w-full sm:max-w-xl sm:rounded-t-3xl bg-white p-4 sm:p-6 shadow-2xl rounded-t-3xl">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Command Center</h2>
            <p className="text-xs text-slate-500">Tell PropertyPro AI what you need using voice or text.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 hover:bg-slate-200"
          >
            Close
          </button>
        </div>

        <div className="mb-4 flex items-center gap-2 rounded-full bg-slate-100 p-1">
          <button
            type="button"
            onClick={() => handleModeToggle('audio')}
            className={`flex-1 rounded-full px-4 py-2 text-xs font-semibold transition ${
              commandMode === 'audio' ? 'bg-slate-900 text-white shadow' : 'text-slate-600'
            }`}
          >
            Audio
          </button>
          <button
            type="button"
            onClick={() => handleModeToggle('text')}
            className={`flex-1 rounded-full px-4 py-2 text-xs font-semibold transition ${
              commandMode === 'text' ? 'bg-slate-900 text-white shadow' : 'text-slate-600'
            }`}
          >
            Text
          </button>
        </div>

        <div className="space-y-4">
          {commandMode === 'audio' ? renderAudioMode() : renderTextMode()}

          <section>
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Quick actions
              </h3>
              <span className="text-[11px] text-slate-400">Tap to open workflows</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {quickActionItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-3 py-3 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow"
                  onClick={() =>
                    onSubmit({
                      kind: 'text',
                      prompt: `Open ${item.title} workspace`,
                      quickAction: item.id,
                    })
                  }
                >
                  <span className={`flex h-10 w-10 items-center justify-center rounded-full ${item.color}`}>
                    <span className="scale-110 transform text-slate-800">{item.icon}</span>
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{item.title}</p>
                    <p className="text-xs text-slate-500">{item.subtitle}</p>
                  </div>
                </button>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default CommandCenter;
