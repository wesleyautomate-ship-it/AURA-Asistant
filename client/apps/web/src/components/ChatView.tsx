import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '../types';
import ViewHeader from './ViewHeader';

const QUICK_ACTIONS = [
    { label: '📝 Create Property Description', prompt: 'Create a property description for a new listing at ' },
    { label: '📱 Generate Social Media Post', prompt: 'Generate a social media post for a new property.' },
    { label: '📊 Analyze Market Data', prompt: 'Analyze the market data for the downtown area.' },
    { label: '📧 Draft Client Email', prompt: 'Draft a follow-up email to a potential buyer.' },
];

const INITIAL_MESSAGE: ChatMessage = { id: 1, text: "Hello! I'm your AI Advisor. How can I help you today?", sender: 'ai' };


const ChatView: React.FC = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_MESSAGE]);
    const [input, setInput] = useState('');
    
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);


    const handleSend = (e: React.FormEvent, messageText?: string) => {
        e.preventDefault();
        const textToSend = messageText || input;
        if (textToSend.trim() === '') return;

        const newUserMessage: ChatMessage = { id: Date.now(), text: textToSend, sender: 'user' };
        setMessages(prev => [...prev, newUserMessage]);
        setInput('');
        
        // Simulate AI response for UI/UX demo
        setTimeout(() => {
            const cannedResponse: ChatMessage = {
                id: Date.now() + 1,
                text: "This is a simulated response. The AI functionality has been disabled for this UI/UX demo.",
                sender: 'ai',
                suggestions: ["What else can you do?", "Tell me about marketing", "Show me my tasks"]
            };
            setMessages(prev => [...prev, cannedResponse]);
        }, 1000);
    };

    const handleQuickAction = (prompt: string) => {
        setInput(prompt);
        inputRef.current?.focus();
    };

    const handleSuggestionClick = (suggestion: string) => {
        const fakeEvent = { preventDefault: () => {} } as React.FormEvent;
        handleSend(fakeEvent, suggestion);
    };
    
    const handleNewChat = () => {
        setMessages([INITIAL_MESSAGE]);
        setInput('');
    };

    const lastAiMessage = messages.slice().reverse().find(m => m.sender === 'ai');
    const currentSuggestions = lastAiMessage?.suggestions;

    return (
        <div className="flex flex-col h-full bg-gray-50">
            <ViewHeader title="AI Chat" actions={
                <button onClick={handleNewChat} className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors">New Chat</button>
            } />
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex items-end space-x-2 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] p-3 rounded-2xl ${msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-gray-200 text-gray-800'}`}>
                            <p className="text-sm">{msg.text}</p>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            <div className="px-4 pb-2">
                {currentSuggestions && currentSuggestions.length > 0 ? (
                    <div className="flex flex-wrap gap-2 mb-2">
                        {currentSuggestions.map((s, i) => (
                            <button key={i} onClick={() => handleSuggestionClick(s)} className="px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-100 rounded-full hover:bg-blue-200 transition-colors">
                                {s}
                            </button>
                        ))}
                    </div>
                ) : messages.length <= 1 && (
                    <div className="grid grid-cols-2 gap-2 mb-2">
                        {QUICK_ACTIONS.map((action) => (
                            <button key={action.label} onClick={() => handleQuickAction(action.prompt)} className="p-2 text-left text-xs font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                                {action.label}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            <div className="p-4 bg-white border-t border-gray-200">
                <form onSubmit={handleSend} className="flex items-center space-x-2">
                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask me anything..."
                        className="flex-1 w-full px-4 py-2 text-sm text-gray-800 bg-gray-100 border-transparent rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button type="submit" disabled={!input.trim()} className="p-2 bg-blue-600 text-white rounded-full disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                         <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.428A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" /></svg>
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatView;
