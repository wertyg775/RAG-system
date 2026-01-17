"use client";

import { useState } from 'react';
import DocumentUploader from '@/components/DocumentUploader';
import ChatInterface from '@/components/ChatInterface';
import DocumentManager from '@/components/DocumentManager';

export default function Home() {
  const [selectedDocument, setSelectedDocument] = useState<string | undefined>();
  const [showUploader, setShowUploader] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = () => {
    setShowUploader(false);
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="h-screen flex flex-col relative particles-bg">
      {/* Animated background grid */}
      <div className="absolute inset-0 z-0 opacity-20">
        <div className="absolute inset-0"
          style={{
            backgroundImage: 'linear-gradient(rgba(168, 85, 247, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(168, 85, 247, 0.1) 1px, transparent 1px)',
            backgroundSize: '50px 50px'
          }}>
        </div>
      </div>

      {/* Header with futuristic design */}
      <header className="glass-effect neon-glow border-b border-purple-500/30 shadow-2xl relative z-10">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Animated logo icon */}
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center shadow-lg"
                style={{ animation: 'pulse-glow 3s ease-in-out infinite' }}>
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>

              <div>
                <h1 className="text-4xl font-black gradient-text tracking-tight">
                  NEURAL DOCS
                </h1>
                <p className="text-sm text-purple-300/80 mt-1 font-medium">
                  AI-Powered Knowledge Extraction System
                </p>
              </div>
            </div>

            <button
              onClick={() => setShowUploader(!showUploader)}
              className="btn-neon px-8 py-4 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 text-white rounded-2xl font-bold
                       hover:shadow-2xl hover:scale-105 transform transition-all duration-300
                       border border-white/20 relative z-10"
            >
              <span className="relative z-10 flex items-center gap-2">
                {showUploader ? '✕ Close' : '⬆ Upload File'}
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* Upload Section with slide-in animation */}
      {showUploader && (
        <div
          className="glass-effect border-b border-purple-500/30 p-6 relative z-10"
          style={{ animation: 'slide-in 0.3s ease-out' }}
        >
          <DocumentUploader onUploadSuccess={handleUploadSuccess} />
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden relative z-10">
        {/* Futuristic Sidebar */}
        <aside className="w-80 glass-effect border-r border-purple-500/30 overflow-hidden relative">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent"></div>
          <DocumentManager
            key={refreshKey}
            onDocumentSelect={setSelectedDocument}
          />
        </aside>

        {/* Chat Area with neon accents */}
        <main className="flex-1 relative">
          <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500 to-transparent"></div>
          <ChatInterface selectedDocument={selectedDocument} />
        </main>
      </div>

      {/* Footer status bar */}
      <div className="glass-effect border-t border-purple-500/30 px-6 py-2 flex items-center justify-between text-xs text-purple-300/60 relative z-10">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            System Online
          </span>
          <span>RAG v3.0</span>
        </div>
        <div className="flex items-center gap-2">
          <span>Powered by Gemini 3</span>
          <span className="text-purple-400">⚡</span>
        </div>
      </div>
    </div>
  );
}
