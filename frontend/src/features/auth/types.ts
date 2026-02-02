export interface User {
    id: number;
    email: string;
    full_name: string;
    is_active: boolean;
    is_verified: boolean;
    created_at: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface SignupRequest {
    email: string;
    full_name: string;
    password: string;
}

export interface OTPVerifyRequest {
    email: string;
    otp_code: string;
}

export interface RefreshTokenRequest {
    refresh_token: string;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface MessageResponse {
    message: string;
}

export interface AuthState {
    user: User | null;
    accessToken: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
}
