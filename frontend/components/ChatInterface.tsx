"use client";

import { useState, useRef, useEffect } from 'react';
import { apiClient, Source } from '@/lib/api';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    sources?: Source[];
}

interface ChatInterfaceProps {
    selectedDocument?: string;
}

export default function ChatInterface({ selectedDocument }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            let fullAnswer = '';
            let sources: Source[] = [];

            const streamGen = apiClient.queryStream({
                query: input,
                top_k: 5,
                filename: selectedDocument,
                stream: true
            });

            setMessages(prev => [...prev, { role: 'assistant', content: '', sources: [] }]);

            for await (const data of streamGen) {
                if (data.type === 'sources') {
                    sources = data.sources;
                } else if (data.type === 'chunk') {
                    fullAnswer += data.content;
                    setMessages(prev => {
                        const newMessages = [...prev];
                        newMessages[newMessages.length - 1] = {
                            role: 'assistant',
                            content: fullAnswer,
                            sources: sources
                        };
                        return newMessages;
                    });
                } else if (data.type === 'error') {
                    throw new Error(data.message);
                }
            }
        } catch (error: any) {
            setMessages(prev => [
                ...prev.slice(0, -1),
                {
                    role: 'assistant',
                    content: `⚠️ Error: ${error.message}`,
                    sources: []
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-8 space-y-6">
                {messages.length === 0 && (
                    <div className="text-center mt-20">
                        <div className="inline-block p-8 glass-effect rounded-3xl neon-glow mb-6"
                            style={{ animation: 'float 3s ease-in-out infinite' }}>
                            <svg className="w-20 h-20 mx-auto text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                            </svg>
                        </div>
                        <h3 className="text-3xl font-black gradient-text mb-3">
                            Connect With Your Documents
                        </h3>
                        <p className="text-purple-300/70 text-lg">Upload files and start extracting knowledge with AI</p>
                    </div>
                )}

                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        style={{ animation: 'slide-in 0.3s ease-out' }}
                    >
                        <div
                            className={`max-w-[85%] rounded-3xl px-6 py-5 relative ${message.role === 'user'
                                    ? 'bg-gradient-to-br from-purple-600 via-pink-600 to-blue-600 text-white shadow-xl border border-white/20'
                                    : 'glass-effect text-purple-50 border border-purple-500/30 shadow-2xl'
                                }`}
                        >
                            {/* Message content with typing effect styling */}
                            <div className="whitespace-pre-wrap font-medium leading-relaxed">
                                {message.content}
                            </div>

                            {/* Enhanced sources display */}
                            {message.sources && message.sources.length > 0 && (
                                <div className="mt-6 pt-4 border-t border-purple-400/30">
                                    <p className="text-sm font-bold mb-3 text-purple-300 flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
                                        Knowledge Sources ({message.sources.length})
                                    </p>
                                    <div className="space-y-3">
                                        {message.sources.map((source, idx) => (
                                            <div
                                                key={idx}
                                                className="text-sm p-4 rounded-2xl bg-black/30 border border-purple-500/20
                                                         hover:border-cyan-400/50 transition-all duration-300 hover:scale-[1.02]"
                                            >
                                                <div className="flex items-center gap-3 mb-2">
                                                    <span className="px-2 py-1 bg-gradient-to-r from-purple-500/30 to-cyan-500/30 
                                                                   rounded-lg text-xs font-bold text-cyan-300 border border-cyan-400/30">
                                                        {idx + 1}
                                                    </span>
                                                    <span className="font-bold text-purple-300 flex-1">
                                                        {source.metadata.filename}
                                                    </span>
                                                    {source.metadata.page && (
                                                        <span className="text-xs text-purple-400/60 font-mono">
                                                            pg.{source.metadata.page}
                                                        </span>
                                                    )}
                                                    <span className="text-xs font-mono text-cyan-400">
                                                        {(source.score * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                                <p className="text-purple-200/70 text-xs line-clamp-2 italic">
                                                    {source.text}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start" style={{ animation: 'slide-in 0.3s ease-out' }}>
                        <div className="glass-effect rounded-3xl px-6 py-5 border border-purple-500/30">
                            <div className="flex gap-3">
                                <div className="w-3 h-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 animate-bounce"></div>
                                <div className="w-3 h-3 rounded-full bg-gradient-to-r from-pink-500 to-blue-500 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                <div className="w-3 h-3 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Futuristic Input Area */}
            <div className="glass-effect border-t border-purple-500/30 p-6 relative">
                <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent"></div>

                <form onSubmit={handleSubmit} className="flex gap-4">
                    <div className="flex-1 relative">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask anything..."
                            disabled={isLoading}
                            className="w-full px-6 py-4 rounded-2xl glass-effect border border-purple-500/30
                                     text-purple-50 placeholder-purple-300/40 font-medium
                                     focus:outline-none focus:border-cyan-400/50 focus:shadow-lg focus:shadow-cyan-500/20
                                     disabled:opacity-50 transition-all duration-300"
                        />
                        <div className="absolute right-4 top-1/2 -translate-y-1/2 text-purple-400/40">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="btn-neon px-8 py-4 bg-gradient-to-r from-purple-600 via-pink-600 to-cyan-600 
                                 text-white rounded-2xl font-bold hover:shadow-2xl hover:scale-105
                                 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100
                                 transition-all duration-300 border border-white/20 relative z-10"
                    >
                        <span className="relative z-10 flex items-center gap-2">
                            {isLoading ? (
                                <>
                                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                    Processing
                                </>
                            ) : (
                                <>
                                    Send
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                    </svg>
                                </>
                            )}
                        </span>
                    </button>
                </form>

                {selectedDocument && (
                    <p className="text-xs text-purple-300/50 mt-3 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                        Scanning: <span className="font-bold text-cyan-400">{selectedDocument}</span>
                    </p>
                )}
            </div>
        </div>
    );
}
