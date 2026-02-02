import { http } from './http';
import { TokenService } from './token.service';

export function setupAuthInterceptor() {
    // Set initial token if exists
    const token = TokenService.getAccessToken();
    if (token) {
        http.setAuthToken(token);
    }
}

export function setAuthToken(token: string | null) {
    http.setAuthToken(token);
}

export function clearAuthToken() {
    http.setAuthToken(null);
}
