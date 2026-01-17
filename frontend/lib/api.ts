// API client for frontend communication
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface QueryRequest {
    query: string;
    top_k?: number;
    filename?: string;
    stream?: boolean;
}

export interface Source {
    text: string;
    metadata: {
        filename?: string;
        page?: number;
        chunk_index?: number;
        [key: string]: any;
    };
    score: number;
}

export interface QueryResponse {
    answer: string;
    sources: Source[];
    query: string;
}

export interface DocumentInfo {
    filename: string;
    metadata: {
        filename: string;
        file_type: string;
        total_pages: number;
        author?: string;
        title?: string;
        upload_time?: string;
    };
    chunk_count: number;
    chunk_ids: string[];
}

export class APIClient {
    private baseURL: string;

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    async uploadDocument(file: File): Promise<any> {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.baseURL}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        return response.json();
    }

    async query(request: QueryRequest): Promise<QueryResponse> {
        const response = await fetch(`${this.baseURL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Query failed');
        }

        return response.json();
    }

    async *queryStream(request: QueryRequest): AsyncGenerator<any> {
        const response = await fetch(`${this.baseURL}/query/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Query failed');
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response body');

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    yield data;
                }
            }
        }
    }

    async listDocuments(): Promise<{ documents: DocumentInfo[]; total_count: number }> {
        const response = await fetch(`${this.baseURL}/documents`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to list documents');
        }

        return response.json();
    }

    async deleteDocument(filename: string): Promise<any> {
        const response = await fetch(`${this.baseURL}/documents/${encodeURIComponent(filename)}`, {
            method: 'DELETE',
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete document');
        }

        return response.json();
    }

    async healthCheck(): Promise<any> {
        const response = await fetch(`${this.baseURL}/`);
        return response.json();
    }
}

export const apiClient = new APIClient();
