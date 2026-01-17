"use client";

import { useState, useEffect } from 'react';
import { apiClient, DocumentInfo } from '@/lib/api';

interface DocumentManagerProps {
    onDocumentSelect?: (filename: string | undefined) => void;
}

export default function DocumentManager({ onDocumentSelect }: DocumentManagerProps) {
    const [documents, setDocuments] = useState<DocumentInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedDoc, setSelectedDoc] = useState<string | undefined>();

    const loadDocuments = async () => {
        try {
            setLoading(true);
            const result = await apiClient.listDocuments();
            setDocuments(result.documents);
        } catch (error) {
            console.error('Failed to load documents:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDocuments();
    }, []);

    const handleDelete = async (filename: string) => {
        if (!confirm(`Delete ${filename}?`)) return;

        try {
            await apiClient.deleteDocument(filename);
            await loadDocuments();
            if (selectedDoc === filename) {
                setSelectedDoc(undefined);
                onDocumentSelect?.(undefined);
            }
        } catch (error: any) {
            alert(`Failed to delete: ${error.message}`);
        }
    };

    const handleSelect = (filename: string) => {
        const newSelection = selectedDoc === filename ? undefined : filename;
        setSelectedDoc(newSelection);
        onDocumentSelect?.(newSelection);
    };

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="p-5 border-b border-purple-500/30">
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-black gradient-text">
                        KNOWLEDGE BASE
                    </h2>
                    <button
                        onClick={loadDocuments}
                        className="p-2.5 glass-effect hover:neon-glow rounded-xl transition-all duration-300 hover:scale-110
                                 border border-purple-500/30 text-purple-300"
                        title="Refresh"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </button>
                </div>
                <p className="text-xs text-purple-300/50 mt-2">
                    {documents.length} document{documents.length !== 1 ? 's' : ''} indexed
                </p>
            </div>

            {/* Documents List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {loading ? (
                    <div className="text-center py-12">
                        <div className="inline-block p-4 glass-effect rounded-2xl">
                            <div className="flex gap-2">
                                <div className="w-2 h-2 rounded-full bg-purple-500 animate-bounce"></div>
                                <div className="w-2 h-2 rounded-full bg-pink-500 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                            </div>
                        </div>
                        <p className="text-purple-300/70 mt-3 text-sm">Scanning...</p>
                    </div>
                ) : documents.length === 0 ? (
                    <div className="text-center py-12 px-4">
                        <div className="inline-block p-6 glass-effect rounded-3xl neon-glow mb-4">
                            <svg className="w-16 h-16 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <p className="text-purple-200 font-bold">No documents yet</p>
                        <p className="text-purple-300/60 text-sm mt-2">Upload files to begin</p>
                    </div>
                ) : (
                    documents.map((doc) => (
                        <div
                            key={doc.filename}
                            onClick={() => handleSelect(doc.filename)}
                            className={`p-4 rounded-2xl cursor-pointer border transition-all duration-300 hover:scale-[1.02]
                                     ${selectedDoc === doc.filename
                                    ? 'glass-effect border-cyan-400/60 shadow-xl shadow-cyan-500/20 bg-gradient-to-br from-cyan-500/10 to-purple-500/10'
                                    : 'glass-effect border-purple-500/20 hover:border-purple-400/40'
                                }`}
                            style={{ animation: 'slide-in 0.3s ease-out' }}
                        >
                            <div className="flex items-start justify-between gap-3">
                                <div className="flex-1 min-w-0">
                                    {/* Filename */}
                                    <h3 className={`font-bold truncate mb-2 ${selectedDoc === doc.filename ? 'text-cyan-300' : 'text-purple-100'
                                        }`}>
                                        {doc.filename}
                                    </h3>

                                    {/* Metadata pills */}
                                    <div className="flex flex-wrap items-center gap-2">
                                        <span className="px-2.5 py-1 bg-purple-500/20 border border-purple-400/30 rounded-lg text-xs font-bold text-purple-300">
                                            {doc.metadata.file_type.toUpperCase()}
                                        </span>
                                        <span className="px-2.5 py-1 bg-pink-500/20 border border-pink-400/30 rounded-lg text-xs font-bold text-pink-300">
                                            {doc.chunk_count} chunks
                                        </span>
                                        {doc.metadata.total_pages > 1 && (
                                            <span className="px-2.5 py-1 bg-blue-500/20 border border-blue-400/30 rounded-lg text-xs font-bold text-blue-300">
                                                {doc.metadata.total_pages} pg
                                            </span>
                                        )}
                                    </div>
                                </div>

                                {/* Delete button */}
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleDelete(doc.filename);
                                    }}
                                    className="p-2.5 glass-effect hover:bg-red-500/20 rounded-xl transition-all duration-300
                                             border border-red-500/30 text-red-400 hover:text-red-300 hover:scale-110"
                                    title="Delete"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </button>
                            </div>

                            {/* Selection indicator */}
                            {selectedDoc === doc.filename && (
                                <div className="mt-3 pt-3 border-t border-cyan-400/30 flex items-center gap-2 text-xs text-cyan-300">
                                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
                                    <span>Active Target</span>
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
