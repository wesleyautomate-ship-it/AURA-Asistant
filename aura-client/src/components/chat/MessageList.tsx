import React, { useEffect, useRef } from 'react';
import Message from './Message';
import { useChatStore } from '../../store/chatStore';

export default function MessageList() {
  const { currentThreadId, messagesByThread } = useChatStore();
  const listRef = useRef<HTMLDivElement>(null);
  const messages = (currentThreadId && messagesByThread[currentThreadId]) || [];

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages.length]);

  return (
    <div ref={listRef} className="flex-1 overflow-y-auto px-4">
      {messages.map((m) => (
        <Message key={m.id} msg={m} />
      ))}
    </div>
  );
}

