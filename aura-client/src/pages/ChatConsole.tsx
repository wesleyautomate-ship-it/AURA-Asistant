import React, { useState } from 'react';
import { useChatStore } from '../store/chatStore';
import ThreadList from '../components/chat/ThreadList';
import MessageList from '../components/chat/MessageList';
import ContextPanel from '../components/chat/ContextPanel';
import ToolChips from '../components/chat/ToolChips';

export default function ChatConsole() {
  const { startChat, isStreaming } = useChatStore();
  const { lastToolEvent } = useChatStore();
  const [input, setInput] = useState('');

  const onSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    startChat(trimmed);
    setInput('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white px-4 py-6">
      <div className="relative h-[80vh] grid grid-cols-12 gap-4">
        {/* Left rail */}
        <div className="col-span-3 bg-white border rounded-2xl overflow-hidden">
          <ThreadList />
        </div>
        {/* Message pane */}
        <div className="col-span-6 bg-white border rounded-2xl flex flex-col overflow-hidden">
          <div className="border-b p-3 flex items-center justify-between">
            <div className="font-semibold text-gray-900">Agentic Chat</div>
            <ToolChips />
          </div>
          <MessageList />
          <div className="border-t p-3 flex items-center gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 rounded-lg border px-3 py-2"
              onKeyDown={(e) => { if (e.key === 'Enter') onSend(); }}
            />
            <button
              onClick={onSend}
              disabled={isStreaming}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg disabled:opacity-50"
            >
              Send
            </button>
            <button
              title="Voice input"
              className="px-3 py-2 border rounded-lg"
              onClick={() => {
                // Hook: open existing mic/transcription UI when available; paste result into input
                alert('Voice hook placeholder');
              }}
            >🎤</button>
          </div>
        </div>
        {/* Right rail */}
        <div className="col-span-3 bg-white border rounded-2xl overflow-hidden">
          <ContextPanel />
        </div>

        {/* Tool toast */}
        {lastToolEvent && (
          <div className="absolute top-2 right-2 bg-white shadow-lg border rounded-lg px-3 py-2 text-sm flex items-center gap-3">
            <div>
              Tool invoked: <span className="font-semibold">{lastToolEvent.name}</span>
              <div className="text-xs text-gray-500">task: {lastToolEvent.task_id.slice(0, 8)}…</div>
            </div>
            <a href="/tasks" className="px-2 py-1 bg-purple-600 text-white rounded">View Task</a>
          </div>
        )}
      </div>
    </div>
  );
}
