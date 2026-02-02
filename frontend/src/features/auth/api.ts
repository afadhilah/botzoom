import { http } from '@/services/http';
import type {
    LoginRequest,
    SignupRequest,
    OTPVerifyRequest,
    RefreshTokenRequest,
    TokenResponse,
    MessageResponse,
    User
} from './types';

export const authApi = {
    async signup(data: SignupRequest): Promise<MessageResponse> {
        return http.post<MessageResponse>('/auth/signup', data);
    },

    async verifyOTP(data: OTPVerifyRequest): Promise<TokenResponse> {
        return http.post<TokenResponse>('/auth/verify-otp', data);
    },

    async login(data: LoginRequest): Promise<TokenResponse> {
        return http.post<TokenResponse>('/auth/login', data);
    },

    async refreshToken(data: RefreshTokenRequest): Promise<TokenResponse> {
        return http.post<TokenResponse>('/auth/refresh', data);
    },

    async getCurrentUser(): Promise<User> {
        return http.get<User>('/users/me');
    }
};
