"""
Unit tests for domains/auth/service.py
Tests authentication business logic including signup, login, OTP verification, and token refresh.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from domains.auth.service import AuthService
from domains.auth.schemas import SignupRequest, LoginRequest, OTPVerifyRequest
from domains.user.schemas import UserCreate
from core.exceptions import (
    InvalidCredentialsError,
    InvalidOTPError,
    UserNotFoundError
)


class TestAuthServiceSignup:
    """Tests for user signup functionality."""
    
    @patch('domains.auth.service.UserService')
    @patch('domains.auth.service.generate_otp')
    def test_signup_creates_user_and_generates_otp(self, mock_generate_otp, mock_user_service):
        """Verify signup creates user and sets OTP."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        signup_data = SignupRequest(
            email="newuser@example.com",
            full_name="New User",
            password="password123"
        )
        mock_user = Mock()
        mock_user.email = signup_data.email
        mock_user_service.create.return_value = mock_user
        mock_generate_otp.return_value = "123456"
        
        # Act
        result = AuthService.signup(mock_db, signup_data)
        
        # Assert
        mock_user_service.create.assert_called_once()
        mock_generate_otp.assert_called_once()
        mock_user_service.set_otp.assert_called_once()
        assert result == mock_user
    
    @patch('domains.auth.service.UserService')
    def test_signup_with_duplicate_email_raises_error(self, mock_user_service):
        """Verify signup with existing email raises UserAlreadyExistsError."""
        # Arrange
        from core.exceptions import UserAlreadyExistsError
        mock_db = MagicMock(spec=Session)
        signup_data = SignupRequest(
            email="existing@example.com",
            full_name="Existing User",
            password="password123"
        )
        mock_user_service.create.side_effect = UserAlreadyExistsError()
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            AuthService.signup(mock_db, signup_data)


class TestAuthServiceOTPVerification:
    """Tests for OTP verification functionality."""
    
    @patch('domains.auth.service.UserService')
    def test_verify_otp_with_valid_code_marks_user_verified(self, mock_user_service):
        """Verify valid OTP marks user as verified."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        verify_data = OTPVerifyRequest(email="test@example.com", otp_code="123456")
        
        mock_user = Mock()
        mock_user.otp_code = "123456"
        mock_user.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        mock_user_service.get_by_email.return_value = mock_user
        mock_user_service.verify_user.return_value = mock_user
        
        # Act
        result = AuthService.verify_otp(mock_db, verify_data)
        
        # Assert
        mock_user_service.verify_user.assert_called_once_with(mock_db, mock_user)
        assert result == mock_user
    
    @patch('domains.auth.service.UserService')
    def test_verify_otp_with_invalid_code_raises_error(self, mock_user_service):
        """Verify invalid OTP code raises InvalidOTPError."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        verify_data = OTPVerifyRequest(email="test@example.com", otp_code="999999")  # Wrong but valid format
        
        mock_user = Mock()
        mock_user.otp_code = "123456"
        mock_user.otp_expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        mock_user_service.get_by_email.return_value = mock_user
        
        # Act & Assert
        with pytest.raises(InvalidOTPError) as exc_info:
            AuthService.verify_otp(mock_db, verify_data)
        
        assert "Invalid OTP code" in str(exc_info.value)
    
    @patch('domains.auth.service.UserService')
    def test_verify_otp_with_expired_code_raises_error(self, mock_user_service):
        """Verify expired OTP raises InvalidOTPError."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        verify_data = OTPVerifyRequest(email="test@example.com", otp_code="123456")
        
        mock_user = Mock()
        mock_user.otp_code = "123456"
        mock_user.otp_expires_at = datetime.utcnow() - timedelta(minutes=1)  # Expired
        
        mock_user_service.get_by_email.return_value = mock_user
        
        # Act & Assert
        with pytest.raises(InvalidOTPError) as exc_info:
            AuthService.verify_otp(mock_db, verify_data)
        
        assert "expired" in str(exc_info.value).lower()
    
    @patch('domains.auth.service.UserService')
    def test_verify_otp_with_nonexistent_user_raises_error(self, mock_user_service):
        """Verify OTP verification for non-existent user raises UserNotFoundError."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        verify_data = OTPVerifyRequest(email="nonexistent@example.com", otp_code="123456")
        mock_user_service.get_by_email.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundError):
            AuthService.verify_otp(mock_db, verify_data)


class TestAuthServiceLogin:
    """Tests for user login functionality."""
    
    @patch('domains.auth.service.verify_password')
    @patch('domains.auth.service.UserService')
    @patch('domains.auth.service.create_access_token')
    @patch('domains.auth.service.create_refresh_token')
    def test_login_with_valid_credentials_returns_tokens(
        self, mock_refresh_token, mock_access_token, mock_user_service, mock_verify_password
    ):
        """Verify successful login returns access and refresh tokens."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        login_data = LoginRequest(email="test@example.com", password="password123")
        
        mock_user = Mock()
        mock_user.hashed_password = "hashed"
        mock_user.is_verified = True
        mock_user.is_active = True
        mock_user.id = 1
        mock_user.email = "test@example.com"
        
        mock_user_service.get_by_email.return_value = mock_user
        mock_verify_password.return_value = True
        mock_access_token.return_value = "access_token_123"
        mock_refresh_token.return_value = "refresh_token_456"
        
        # Act
        result = AuthService.login(mock_db, login_data)
        
        # Assert
        assert result.access_token == "access_token_123"
        assert result.refresh_token == "refresh_token_456"
        assert result.token_type == "bearer"
    
    @patch('domains.auth.service.UserService')
    def test_login_with_invalid_password_raises_error(self, mock_user_service):
        """Verify login with wrong password raises InvalidCredentialsError."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        login_data = LoginRequest(email="test@example.com", password="wrongpassword")
        
        mock_user = Mock()
        mock_user.hashed_password = "hashed"
        mock_user_service.get_by_email.return_value = mock_user
        
        with patch('domains.auth.service.verify_password', return_value=False):
            # Act & Assert
            with pytest.raises(InvalidCredentialsError):
                AuthService.login(mock_db, login_data)
    
    @patch('domains.auth.service.UserService')
    def test_login_with_unverified_user_raises_error(self, mock_user_service):
        """Verify login with unverified email raises InvalidCredentialsError."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        login_data = LoginRequest(email="test@example.com", password="password123")
        
        mock_user = Mock()
        mock_user.hashed_password = "hashed"
        mock_user.is_verified = False
        mock_user.is_active = True
        
        mock_user_service.get_by_email.return_value = mock_user
        
        with patch('domains.auth.service.verify_password', return_value=True):
            # Act & Assert
            with pytest.raises(InvalidCredentialsError) as exc_info:
                AuthService.login(mock_db, login_data)
            
            assert "verify" in str(exc_info.value).lower()
    
    @patch('domains.auth.service.UserService')
    def test_login_with_nonexistent_user_raises_error(self, mock_user_service):
        """Verify login with non-existent email raises InvalidCredentialsError."""
        # Arrange
        mock_db = MagicMock(spec=Session)
        login_data = LoginRequest(email="nonexistent@example.com", password="password123")
        mock_user_service.get_by_email.return_value = None
        
        # Act & Assert
        with pytest.raises(InvalidCredentialsError):
            AuthService.login(mock_db, login_data)


class TestAuthServiceTokenRefresh:
    """Tests for token refresh functionality."""
    
    @patch('domains.auth.service.verify_refresh_token')
    @patch('domains.auth.service.create_access_token')
    @patch('domains.auth.service.create_refresh_token')
    def test_refresh_access_token_generates_new_tokens(
        self, mock_create_refresh, mock_create_access, mock_verify_refresh
    ):
        """Verify token refresh generates new access and refresh tokens."""
        # Arrange
        refresh_token = "old_refresh_token"
        mock_verify_refresh.return_value = {"sub": "1", "email": "test@example.com"}
        mock_create_access.return_value = "new_access_token"
        mock_create_refresh.return_value = "new_refresh_token"
        
        # Act
        result = AuthService.refresh_access_token(refresh_token)
        
        # Assert
        assert result.access_token == "new_access_token"
        assert result.refresh_token == "new_refresh_token"
        mock_verify_refresh.assert_called_once_with(refresh_token)
