from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from domains.user.model import User
from domains.user.service import UserService
from domains.user.schemas import UserCreate
from domains.auth.schemas import LoginRequest, SignupRequest, OTPVerifyRequest, TokenResponse
from core.security import verify_password, generate_otp
from core.jwt import create_access_token, create_refresh_token, verify_refresh_token
from core.config import settings
from core.exceptions import (
    InvalidCredentialsError,
    InvalidOTPError,
    UserAlreadyExistsError,
    UserNotFoundError
)


class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def signup(db: Session, signup_data: SignupRequest) -> User:
        """Register a new user and generate OTP."""
        user = UserService.create(db, UserCreate(**signup_data.dict()))
        
        # ====== OTP DISABLED - AUTO VERIFY USER ======
        # Bypass OTP verification for development
        user = UserService.verify_user(db, user)
        print(f"✅ [DEV] User {user.email} auto-verified (OTP disabled)")
        return user
        
        # ====== ORIGINAL OTP CODE (DISABLED) ======
        # # Generate and set OTP
        # otp_code = generate_otp(settings.OTP_LENGTH)
        # expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        # UserService.set_otp(db, user, otp_code, expires_at)
        # 
        # # Send OTP via email (with fallback to console in dev mode)
        # if settings.MAIL_USERNAME and settings.MAIL_SERVER:
        #     from utils.email import send_otp_email
        #     try:
        #         send_otp_email(user.email, user.full_name, otp_code)
        #         print(f"✅ OTP email sent to {user.email}")
        #     except Exception as e:
        #         print(f"⚠️ Failed to send OTP email: {e}")
        #         # In development, also print to console as fallback
        #         if settings.DEBUG:
        #             print(f"🔐 [DEV] OTP for {user.email}: {otp_code}")
        # else:
        #     # Email not configured, print to console in dev mode
        #     if settings.DEBUG:
        #         print(f"🔐 [DEV] Email not configured. OTP for {user.email}: {otp_code}")
        # 
        # return user
    
    @staticmethod
    def verify_otp(db: Session, verify_data: OTPVerifyRequest) -> User:
        """Verify OTP and activate user."""
        user = UserService.get_by_email(db, verify_data.email)
        if not user:
            raise UserNotFoundError()
        
        # Check OTP validity
        if not user.otp_code or not user.otp_expires_at:
            raise InvalidOTPError("No OTP found for this user")
        
        if user.otp_code != verify_data.otp_code:
            raise InvalidOTPError("Invalid OTP code")
        
        if datetime.utcnow() > user.otp_expires_at:
            raise InvalidOTPError("OTP has expired")
        
        # Mark user as verified
        user = UserService.verify_user(db, user)
        return user
    
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = UserService.get_by_email(db, login_data.email)
        if not user:
            raise InvalidCredentialsError()
        
        if not verify_password(login_data.password, user.hashed_password):
            raise InvalidCredentialsError()
        
        if not user.is_verified:
            raise InvalidCredentialsError("Please verify your email first")
        
        if not user.is_active:
            raise InvalidCredentialsError("Account is deactivated")
        
        # Generate tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> TokenResponse:
        """Generate new access token from refresh token."""
        payload = verify_refresh_token(refresh_token)
        
        token_data = {"sub": payload["sub"], "email": payload["email"]}
        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )
