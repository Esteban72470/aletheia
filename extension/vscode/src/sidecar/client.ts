/**
 * Sidecar HTTP Client
 *
 * Communicates with the Aletheia sidecar service.
 */

import * as fs from 'fs';
import * as path from 'path';

// Types
interface ParseResult {
    document_id: string;
    pages: PageResult[];
    metadata: {
        total_pages: number;
        processing_time_ms: number;
    };
}

interface PageResult {
    page_number: number;
    width: number;
    height: number;
    blocks: BlockResult[];
    tables: TableResult[];
    figures: FigureResult[];
}

interface BlockResult {
    id: string;
    type: string;
    bbox: number[];
    text: string;
    confidence: number;
}

interface TableResult {
    id: string;
    bbox: number[];
    rows: number;
    columns: number;
    cells: string[][];
    csv?: string;
}

interface FigureResult {
    id: string;
    bbox: number[];
    caption?: string;
}

interface HealthResult {
    status: string;
    version: string;
    uptime_seconds: number;
    models_loaded: string[];
}

/**
 * HTTP client for the Aletheia sidecar service.
 */
export class SidecarClient {
    private baseUrl: string;
    private timeout: number;

    constructor(host: string = '127.0.0.1', port: number = 8420, timeout: number = 30000) {
        this.baseUrl = `http://${host}:${port}`;
        this.timeout = timeout;
    }

    /**
     * Check sidecar health.
     */
    async health(): Promise<HealthResult> {
        const response = await this.request('GET', '/health');
        return response as HealthResult;
    }

    /**
     * Parse a file.
     */
    async parseFile(filePath: string, options: Record<string, any> = {}): Promise<ParseResult> {
        const content = fs.readFileSync(filePath);
        const filename = path.basename(filePath);

        // For now, use JSON body
        // TODO: Implement proper multipart form data
        const response = await this.request('POST', '/api/v1/parse', {
            filename,
            content: content.toString('base64'),
            options
        });

        return response as ParseResult;
    }

    /**
     * Query a parsed document.
     */
    async query(documentId: string, query: string): Promise<any> {
        return this.request('POST', '/api/v1/query', {
            document_id: documentId,
            query
        });
    }

    /**
     * Make an HTTP request.
     */
    private async request(
        method: string,
        path: string,
        body?: any
    ): Promise<any> {
        const url = `${this.baseUrl}${path}`;

        const options: RequestInit = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        // Use dynamic import for fetch
        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return response.json();
    }
}
