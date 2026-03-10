import API_CONFIG from './config';
import { TokenService } from './token.service';

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
    private isRefreshing = false;
    private refreshPromise: Promise<void> | null = null;

    constructor(baseURL: string = API_CONFIG.baseURL) {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    private async refreshTokenIfNeeded(): Promise<void> {
        // If already refreshing, wait for it
        if (this.isRefreshing && this.refreshPromise) {
            await this.refreshPromise;
            return;
        }

        // Check if token is expiring soon
        if (TokenService.isTokenExpiringSoon()) {
            this.isRefreshing = true;
            this.refreshPromise = this.performTokenRefresh();
            
            try {
                await this.refreshPromise;
            } finally {
                this.isRefreshing = false;
                this.refreshPromise = null;
            }
        }
    }

    private async performTokenRefresh(): Promise<void> {
        const refreshToken = TokenService.getRefreshToken();
        if (!refreshToken) {
            console.warn('[HTTP] No refresh token available');
            return;
        }

        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                TokenService.setTokens(data.access_token, data.refresh_token);
                console.log('[HTTP] Token refreshed successfully');
            } else {
                console.error('[HTTP] Token refresh failed, clearing tokens');
                TokenService.clearTokens();
                // Redirect to login or show notification
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('[HTTP] Token refresh error:', error);
            TokenService.clearTokens();
        }
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

    private getHeaders(customHeaders?: HeadersInit): HeadersInit {
        // Always get fresh token from localStorage
        const token = localStorage.getItem('access_token');
        const headers: HeadersInit = { ...this.defaultHeaders };
        
        if (token) {
            (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
        }
        
        if (customHeaders) {
            Object.assign(headers, customHeaders);
        }
        
        return headers;
    }

    async get<T = any>(endpoint: string, config?: RequestConfig): Promise<T> {
        await this.refreshTokenIfNeeded();
        const url = this.buildURL(endpoint, config?.params);

        const response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders(config?.headers),
            ...config,
        });

        return this.handleResponse<T>(response);
    }

    async post<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
        await this.refreshTokenIfNeeded();
        const url = this.buildURL(endpoint, config?.params);

        const response = await fetch(url, {
            method: 'POST',
            headers: this.getHeaders(config?.headers),
            body: data ? JSON.stringify(data) : undefined,
            ...config,
        });

        return this.handleResponse<T>(response);
    }

    async put<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
        await this.refreshTokenIfNeeded();
        const url = this.buildURL(endpoint, config?.params);

        const response = await fetch(url, {
            method: 'PUT',
            headers: this.getHeaders(config?.headers),
            body: data ? JSON.stringify(data) : undefined,
            ...config,
        });

        return this.handleResponse<T>(response);
    }

    async delete<T = any>(endpoint: string, config?: RequestConfig): Promise<T> {
        await this.refreshTokenIfNeeded();
        const url = this.buildURL(endpoint, config?.params);

        const response = await fetch(url, {
            method: 'DELETE',
            headers: this.getHeaders(config?.headers),
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
