import API_CONFIG from './config';

interface RequestConfig extends RequestInit {
    params?: Record<string, string | number | boolean>;
}

interface ApiResponse<T = any> {
    data?: T;
    error?: string;
    message?: string;
}

class HttpClient {
    private baseURL: string;
    private defaultHeaders: HeadersInit;

    constructor(baseURL: string = API_CONFIG.baseURL) {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    private buildURL(endpoint: string, params?: Record<string, string | number | boolean>): string {
        // Handle relative baseURL (like /api)
        let fullURL: string;
        if (this.baseURL.startsWith('http')) {
            // Absolute URL
            fullURL = new URL(endpoint, this.baseURL).toString();
        } else {
            // Relative URL - just concatenate
            const base = this.baseURL.endsWith('/') ? this.baseURL.slice(0, -1) : this.baseURL;
            const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
            fullURL = `${base}${path}`;
        }

        if (params) {
            const url = new URL(fullURL, window.location.origin);
            Object.entries(params).forEach(([key, value]) => {
                url.searchParams.append(key, String(value));
            });
            return url.toString();
        }

        return fullURL;
    }

    private async handleResponse<T>(response: Response): Promise<T> {
        const contentType = response.headers.get('content-type');
        const isJson = contentType?.includes('application/json');

        if (!response.ok) {
            const errorData = isJson ? await response.json() : { detail: await response.text() };
            throw new Error(errorData.detail || errorData.message || 'Request failed');
        }

        return isJson ? response.json() : response.text();
    }

    async get<T = any>(endpoint: string, config?: RequestConfig): Promise<T> {
        const url = this.buildURL(endpoint, config?.params);

        const response = await fetch(url, {
            method: 'GET',
            headers: { ...this.defaultHeaders, ...config?.headers },
            ...config,
        });

        return this.handleResponse<T>(response);
    }

    async post<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
        const url = this.buildURL(endpoint, config?.params);

        const response = await fetch(url, {
            method: 'POST',
            headers: { ...this.defaultHeaders, ...config?.headers },
            body: data ? JSON.stringify(data) : undefined,
            ...config,
        });

        return this.handleResponse<T>(response);
    }

    async put<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
        const url = this.buildURL(endpoint, config?.params);

        const response = await fetch(url, {
            method: 'PUT',
            headers: { ...this.defaultHeaders, ...config?.headers },
            body: data ? JSON.stringify(data) : undefined,
            ...config,
        });

        return this.handleResponse<T>(response);
    }

    async delete<T = any>(endpoint: string, config?: RequestConfig): Promise<T> {
        const url = this.buildURL(endpoint, config?.params);

        const response = await fetch(url, {
            method: 'DELETE',
            headers: { ...this.defaultHeaders, ...config?.headers },
            ...config,
        });

        return this.handleResponse<T>(response);
    }

    setAuthToken(token: string | null) {
        if (token) {
            this.defaultHeaders = {
                ...this.defaultHeaders,
                'Authorization': `Bearer ${token}`,
            };
        } else {
            const { Authorization, ...rest } = this.defaultHeaders as any;
            this.defaultHeaders = rest;
        }
    }
}

export const http = new HttpClient();
export type { RequestConfig, ApiResponse };
