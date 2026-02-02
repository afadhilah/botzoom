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
}
