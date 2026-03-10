const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export class TokenService {
    static getAccessToken(): string | null {
        return localStorage.getItem(TOKEN_KEY);
    }

    static getRefreshToken(): string | null {
        return localStorage.getItem(REFRESH_TOKEN_KEY);
    }

    static setTokens(accessToken: string, refreshToken: string): void {
        localStorage.setItem(TOKEN_KEY, accessToken);
        localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }

    static clearTokens(): void {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
    }

    static hasValidToken(): boolean {
        const token = this.getAccessToken();
        if (!token) return false;

        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const exp = payload.exp * 1000; // Convert to milliseconds
            return Date.now() < exp;
        } catch {
            return false;
        }
    }

    static isTokenExpiringSoon(): boolean {
        const token = this.getAccessToken();
        if (!token) return false;

        try {
            const parts = token.split('.');
            if (parts.length !== 3) return false;
            
            const payload = JSON.parse(atob(parts[1]));
            const exp = payload.exp * 1000; // Convert to milliseconds
            const now = Date.now();
            const timeUntilExpiry = exp - now;
            
            // Token expires in less than 5 minutes
            return timeUntilExpiry < 5 * 60 * 1000 && timeUntilExpiry > 0;
        } catch {
            return false;
        }
    }

    static getTokenExpiryTime(): number | null {
        const token = this.getAccessToken();
        if (!token) return null;

        try {
            const parts = token.split('.');
            if (parts.length !== 3) return null;
            
            const payload = JSON.parse(atob(parts[1]));
            return payload.exp * 1000; // Convert to milliseconds
        } catch {
            return null;
        }
    }
}
