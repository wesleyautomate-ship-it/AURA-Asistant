import React from 'react';
import type { ChatMessage } from '../../store/chatStore';

export default function Message({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} my-2`}>
      <div className={`${isUser ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-900'} rounded-2xl px-3 py-2 max-w-[75%] whitespace-pre-wrap`}>
        {msg.text}
      </div>
    </div>
  );
}

