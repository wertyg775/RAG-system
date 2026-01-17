"use client";

import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api';

interface DocumentUploaderProps {
    onUploadSuccess?: () => void;
}

export default function DocumentUploader({ onUploadSuccess }: DocumentUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<{
        type: 'success' | 'error' | null;
        message: string;
    }>({ type: null, message: '' });

    const handleFile = async (file: File) => {
        const validExtensions = ['.pdf', '.docx', '.doc', '.md', '.markdown', '.txt'];
        const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

        if (!validExtensions.includes(fileExt)) {
            setUploadStatus({
                type: 'error',
                message: `⚠️ Unsupported format. Accepted: ${validExtensions.join(', ')}`
            });
            return;
        }

        setUploading(true);
        setUploadStatus({ type: null, message: '' });

        try {
            const result = await apiClient.uploadDocument(file);
            setUploadStatus({
                type: 'success',
                message: `✓ ${result.filename} uploaded • ${result.chunks_created} chunks indexed`
            });

            if (onUploadSuccess) {
                setTimeout(() => onUploadSuccess(), 1500);
            }
        } catch (error: any) {
            setUploadStatus({
                type: 'error',
                message: `✕ ${error.message || 'Upload failed'}`
            });
        } finally {
            setUploading(false);
        }
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            handleFile(files[0]);
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto">
            <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300
                          ${isDragging
                        ? 'border-cyan-400 bg-cyan-500/10 scale-105 neon-glow'
                        : 'border-purple-500/30 glass-effect hover:border-purple-400/50'
                    }
                          ${uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-[1.02]'}
                `}
            >
                <input
                    type="file"
                    id="file-upload-neural"
                    className="hidden"
                    accept=".pdf,.docx,.doc,.md,.markdown,.txt"
                    onChange={handleFileInput}
                    disabled={uploading}
                />

                <label htmlFor="file-upload-neural" className="cursor-pointer">
                    <div className="flex flex-col items-center gap-6">
                        {/* Animated upload icon */}
                        <div className={`p-6 rounded-3xl glass-effect border border-purple-500/30 ${uploading ? 'animate-pulse' : 'hover:neon-glow'
                            }`}>
                            <svg
                                className={`w-16 h-16 transition-all duration-300 ${isDragging ? 'text-cyan-400 scale-110' : 'text-purple-400'
                                    }`}
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                                />
                            </svg>
                        </div>

                        {/* Text */}
                        <div>
                            <p className="text-2xl font-black gradient-text mb-2">
                                {uploading ? 'Processing...' : isDragging ? 'Drop to Upload' : 'Upload Document'}
                            </p>
                            <p className="text-purple-300/70 font-medium">
                                {uploading ? 'Analyzing and indexing' : 'Drag & drop or click to browse'}
                            </p>
                            <p className="text-sm text-purple-400/60 mt-3 font-mono">
                                PDF • DOCX • Markdown • TXT
                            </p>
                        </div>

                        {/* Upload progress indicator */}
                        {uploading && (
                            <div className="flex gap-2">
                                <div className="w-2 h-2 rounded-full bg-purple-500 animate-bounce"></div>
                                <div className="w-2 h-2 rounded-full bg-pink-500 animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                <div className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                            </div>
                        )}
                    </div>
                </label>

                {/* Decorative corner accents */}
                <div className="absolute top-3 left-3 w-4 h-4 border-t-2 border-l-2 border-purple-500/50 rounded-tl-lg"></div>
                <div className="absolute top-3 right-3 w-4 h-4 border-t-2 border-r-2 border-purple-500/50 rounded-tr-lg"></div>
                <div className="absolute bottom-3 left-3 w-4 h-4 border-b-2 border-l-2 border-purple-500/50 rounded-bl-lg"></div>
                <div className="absolute bottom-3 right-3 w-4 h-4 border-b-2 border-r-2 border-purple-500/50 rounded-br-lg"></div>
            </div>

            {/* Status message */}
            {uploadStatus.message && (
                <div
                    className={`mt-5 px-6 py-4 rounded-2xl font-bold border transition-all duration-300
                              ${uploadStatus.type === 'success'
                            ? 'glass-effect border-green-400/50 text-green-300 shadow-lg shadow-green-500/20'
                            : 'glass-effect border-red-400/50 text-red-300 shadow-lg shadow-red-500/20'
                        }`}
                    style={{ animation: 'slide-in 0.3s ease-out' }}
                >
                    {uploadStatus.message}
                </div>
            )}
        </div>
    );
}
