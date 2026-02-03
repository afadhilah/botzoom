from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.session import get_db
from domains.auth.schemas import (
    LoginRequest,
    SignupRequest,
    OTPVerifyRequest,
    RefreshTokenRequest,
    TokenResponse,
    MessageResponse
)
from domains.auth.service import AuthService
from core.exceptions import AppException


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(signup_data: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user (OTP disabled - auto login)."""
    try:
        user = AuthService.signup(db, signup_data)
        
        # Auto-login after signup (OTP disabled)
        from core.jwt import create_access_token, create_refresh_token
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(verify_data: OTPVerifyRequest, db: Session = Depends(get_db)):
    """Verify OTP and activate user account."""
    try:
        user = AuthService.verify_otp(db, verify_data)
        
        # Auto-login after verification
        login_data = LoginRequest(email=user.email, password="")
        # We need to generate tokens directly since we already verified
        from core.jwt import create_access_token, create_refresh_token
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    try:
        return AuthService.login(db, login_data)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(token_data: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        return AuthService.refresh_access_token(token_data.refresh_token)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
