import React, { useEffect, useMemo, useState } from 'react';
import { ACTION_ITEMS } from '../constants.tsx';
import type { CommandMode, CommandStatus } from '../store/uiStore';
import type { CommandRequest } from '../types';
import { audioService, type AudioRecordingResult } from '../services/audioService';

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

const quickActionLabels = ['Listing campaign', 'Schedule showing', 'Draft follow-up', 'Analyze pricing'];

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

  useEffect(() => {
    let timer: ReturnType<typeof setInterval> | undefined;
    if (commandStatus === 'recording') {
      timer = setInterval(() => {
        setElapsed(audioService.getRecordingDuration());
      }, 200);
    } else {
      setElapsed(recording?.duration ?? 0);
      if (timer) clearInterval(timer);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [commandStatus, recording]);

  const handleModeToggle = (mode: CommandMode) => {
    if (mode === commandMode) return;
    onModeChange(mode);
    if (mode === 'audio') {
      setRecording(null);
      onTranscriptChange('');
    }
  };

  const startRecording = async () => {
    setSupportError(null);
    if (!audioService.isMediaRecorderSupported() || !audioService.isGetUserMediaSupported()) {
      setSupportError('Voice capture unavailable on this device.');
      return;
    }

    try {
      await audioService.startRecording();
      onStatusChange('recording');
      setRecording(null);
      onTranscriptChange('');
    } catch (error) {
      console.error('Failed to start recording', error);
      setSupportError('Microphone access denied.');
      onStatusChange('idle');
    }
  };

  const stopRecording = async () => {
    try {
      const result = await audioService.stopRecording();
      setRecording(result);
      onStatusChange('reviewing');
    } catch (error) {
      console.error('Failed to stop recording', error);
      setSupportError('Recording failed.');
      onStatusChange('idle');
    }
  };

  const sendAudio = () => {
    if (!recording) return;
    void onSubmit({
      kind: 'audio',
      transcript: commandTranscript,
      mimeType: recording.mimeType,
      duration: recording.duration,
      audioBlob: recording.audioBlob,
    });
  };

  const sendText = () => {
    if (!commandText.trim()) return;
    void onSubmit({ kind: 'text', prompt: commandText.trim(), quickAction: null });
  };

  const quickActions = useMemo(() => ACTION_ITEMS.slice(0, 4), []);

  return (
    <div className="fixed inset-0 z-40 flex flex-col bg-slate-900/40 backdrop-blur-sm">
      <div className="mt-auto w-full rounded-t-3xl bg-white p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">Command Center</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600"
          >
            Close
          </button>
        </div>

        <div className="mb-4 flex items-center gap-2 rounded-full bg-slate-100 p-1">
          <button
            type="button"
            onClick={() => handleModeToggle('audio')}
            className={`flex-1 rounded-full px-3 py-2 text-xs font-semibold ${
              commandMode === 'audio' ? 'bg-slate-900 text-white shadow' : 'text-slate-600'
            }`}
          >
            Audio
          </button>
          <button
            type="button"
            onClick={() => handleModeToggle('text')}
            className={`flex-1 rounded-full px-3 py-2 text-xs font-semibold ${
              commandMode === 'text' ? 'bg-slate-900 text-white shadow' : 'text-slate-600'
            }`}
          >
            Text
          </button>
        </div>

        {commandMode === 'audio' ? (
          <div className="mb-4 space-y-3 rounded-2xl bg-slate-900 p-5 text-white">
            <div className="flex items-center justify-between text-xs">
              <span>Voice Command</span>
              <span>{Math.max(0, Math.round(elapsed / 1000))}s</span>
            </div>
            <div className="flex h-24 items-center justify-center rounded-xl bg-black/20">
              <span className="h-3 w-3 rounded-full bg-white/50" />
            </div>
            <div className="flex flex-wrap items-center gap-3">
              {commandStatus === 'recording' ? (
                <button
                  type="button"
                  onClick={stopRecording}
                  className="rounded-full bg-white px-4 py-2 text-xs font-semibold text-slate-900"
                >
                  Stop
                </button>
              ) : (
                <button
                  type="button"
                  onClick={startRecording}
                  className="rounded-full bg-red-500 px-4 py-2 text-xs font-semibold text-white"
                >
                  {recording ? 'Re-record' : 'Record'}
                </button>
              )}
              {recording && (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      setRecording(null);
                      onTranscriptChange('');
                      onStatusChange('idle');
                    }}
                    className="rounded-full border border-white/30 px-3 py-2 text-xs"
                  >
                    Delete
                  </button>
                  <button
                    type="button"
                    onClick={sendAudio}
                    className="rounded-full bg-blue-400 px-4 py-2 text-xs font-semibold text-white"
                  >
                    Send
                  </button>
                </>
              )}
            </div>
            {supportError && <p className="text-[11px] text-red-200">{supportError}</p>}
            {commandError && <p className="text-[11px] text-orange-200">{commandError}</p>}
          </div>
        ) : (
          <div className="mb-4 space-y-3">
            <textarea
              value={commandText}
              onChange={(event) => onTextChange(event.target.value)}
              placeholder="Tell PropertyPro AI what to do…"
              className="h-32 w-full rounded-2xl border border-slate-200 bg-slate-50 p-3 text-sm"
            />
            <button
              type="button"
              onClick={sendText}
              disabled={!commandText.trim()}
              className="w-full rounded-full bg-slate-900 py-3 text-sm font-semibold text-white disabled:bg-slate-400"
            >
              Send
            </button>
            {commandError && <p className="text-[11px] text-red-500">{commandError}</p>}
          </div>
        )}

        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase text-slate-500">Quick actions</h3>
          <div className="grid grid-cols-2 gap-2">
            {quickActions.map((item, index) => (
              <button
                key={item.id}
                type="button"
                onClick={() => onSubmit({ kind: 'text', prompt: `Open ${item.title} workspace`, quickAction: item.id })}
                className="rounded-2xl border border-slate-200 bg-white p-3 text-left text-xs font-semibold text-slate-700"
              >
                {quickActionLabels[index] ?? item.title}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommandCenter;
