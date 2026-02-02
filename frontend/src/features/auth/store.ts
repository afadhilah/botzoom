import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authApi } from './api';
import { TokenService } from '@/services/token.service';
import { setAuthToken, clearAuthToken } from '@/services/auth.interceptor';
import type { User, LoginRequest, SignupRequest, OTPVerifyRequest } from './types';

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null);
    const isLoading = ref(false);
    const error = ref<string | null>(null);

    const isAuthenticated = computed(() => !!user.value && TokenService.hasValidToken());

    async function signup(data: SignupRequest): Promise<string> {
        isLoading.value = true;
        error.value = null;

        try {
            const response = await authApi.signup(data);
            return response.message;
        } catch (err: any) {
            error.value = err.message || 'Signup failed';
            throw err;
        } finally {
            isLoading.value = false;
        }
    }

    async function verifyOTP(data: OTPVerifyRequest): Promise<void> {
        isLoading.value = true;
        error.value = null;

        try {
            const response = await authApi.verifyOTP(data);

            TokenService.setTokens(response.access_token, response.refresh_token);
            setAuthToken(response.access_token);

            await fetchCurrentUser();
        } catch (err: any) {
            error.value = err.message || 'OTP verification failed';
            throw err;
        } finally {
            isLoading.value = false;
        }
    }

    async function login(data: LoginRequest): Promise<void> {
        isLoading.value = true;
        error.value = null;

        try {
            const response = await authApi.login(data);

            TokenService.setTokens(response.access_token, response.refresh_token);
            setAuthToken(response.access_token);

            await fetchCurrentUser();
        } catch (err: any) {
            error.value = err.message || 'Login failed';
            throw err;
        } finally {
            isLoading.value = false;
        }
    }

    async function fetchCurrentUser(): Promise<void> {
        try {
            user.value = await authApi.getCurrentUser();
        } catch (err: any) {
            error.value = err.message || 'Failed to fetch user';
            logout();
            throw err;
        }
    }

    async function refreshSession(): Promise<void> {
        const refreshToken = TokenService.getRefreshToken();
        if (!refreshToken) {
            logout();
            return;
        }

        try {
            const response = await authApi.refreshToken({ refresh_token: refreshToken });
            TokenService.setTokens(response.access_token, response.refresh_token);
            setAuthToken(response.access_token);
            await fetchCurrentUser();
        } catch (err) {
            logout();
            throw err;
        }
    }

    async function initializeAuth(): Promise<void> {
        const token = TokenService.getAccessToken();

        if (!token) {
            return;
        }

        if (TokenService.hasValidToken()) {
            setAuthToken(token);
            try {
                await fetchCurrentUser();
            } catch {
                logout();
            }
        } else {
            await refreshSession();
        }
    }

    function logout(): void {
        user.value = null;
        TokenService.clearTokens();
        clearAuthToken();
    }

    function clearError(): void {
        error.value = null;
    }

    return {
        user,
        isLoading,
        error,
        isAuthenticated,
        signup,
        verifyOTP,
        login,
        logout,
        fetchCurrentUser,
        refreshSession,
        initializeAuth,
        clearError
    };
});
