import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/features/auth/store';
import type { LoginRequest, SignupRequest } from '@/features/auth/types';

/**
 * Composable for login functionality
 * Use this in your existing LoginForm component
 */
export function useLogin() {
    const router = useRouter();
    const authStore = useAuthStore();

    const formData = ref<LoginRequest>({
        email: '',
        password: ''
    });

    const isLoading = ref(false);
    const error = ref<string | null>(null);

    async function handleLogin() {
        isLoading.value = true;
        error.value = null;

        try {
            await authStore.login(formData.value);
            router.push('/dashboard');
        } catch (err: any) {
            error.value = err.message || 'Login failed';
        } finally {
            isLoading.value = false;
        }
    }

    return {
        formData,
        isLoading,
        error,
        handleLogin
    };
}

/**
 * Composable for signup functionality
 * Use this in your existing SignupForm component
 */
export function useSignup() {
    const router = useRouter();
    const authStore = useAuthStore();

    const formData = ref<SignupRequest>({
        email: '',
        full_name: '',
        password: ''
    });

    const isLoading = ref(false);
    const error = ref<string | null>(null);
    const successMessage = ref<string | null>(null);

    async function handleSignup() {
        isLoading.value = true;
        error.value = null;

        try {
            // OTP DISABLED - Auto-login after signup
            await authStore.signup(formData.value);
            
            // Auto-login with same credentials
            await authStore.login({
                email: formData.value.email,
                password: formData.value.password
            });
            
            successMessage.value = 'Registration successful! Redirecting...';
            
            setTimeout(() => {
                router.push('/dashboard');
            }, 1500);
        } catch (err: any) {
            error.value = err.message || 'Signup failed';
        } finally {
            isLoading.value = false;
        }
    }

    return {
        formData,
        isLoading,
        error,
        successMessage,
        handleSignup
    };
}

// OTP DISABLED - useOTPVerification removed
/*
export function useOTPVerification() {
    const router = useRouter();
    const authStore = useAuthStore();

    const email = ref('');
    const otpCode = ref('');
    const isLoading = ref(false);
    const error = ref<string | null>(null);

    function initializeEmail(emailFromQuery: string) {
        email.value = emailFromQuery;
        if (!email.value) {
            router.push('/auth/signup');
        }
    }

    async function handleVerifyOTP() {
        isLoading.value = true;
        error.value = null;

        try {
            await authStore.verifyOTP({
                email: email.value,
                otp_code: otpCode.value
            });
            router.push('/dashboard');
        } catch (err: any) {
            error.value = err.message || 'OTP verification failed';
        } finally {
            isLoading.value = false;
        }
    }

    return {
        email,
        otpCode,
        isLoading,
        error,
        initializeEmail,
        handleVerifyOTP
    };
}
*/