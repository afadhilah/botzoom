"""
Unit tests for domains/user/service.py
Tests user CRUD operations, OTP management, and validation.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from domains.user.service import UserService
from domains.user.schemas import UserCreate, UserUpdate
from domains.user.model import User
from core.exceptions import UserNotFoundError, UserAlreadyExistsError


class TestUserServiceCreate:
    """Tests for user creation."""
    
    @patch('domains.user.service.hash_password')
    def test_create_user_hashes_password(self, mock_hash_password, mock_db_session):
        """Verify user creation hashes the password."""
        # Arrange
        mock_hash_password.return_value = "hashed_password_123"
        user_data = UserCreate(
            email="newuser@example.com",
            full_name="New User",
            password="plaintext_password"
        )
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = UserService.create(mock_db_session, user_data)
        
        # Assert
        mock_hash_password.assert_called_once_with("plaintext_password")
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_create_user_with_duplicate_email_raises_error(self, mock_db_session):
        """Verify creating user with existing email raises UserAlreadyExistsError."""
        # Arrange
        user_data = UserCreate(
            email="existing@example.com",
            full_name="Existing User",
            password="password123"
        )
        
        existing_user = Mock(spec=User)
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing_user
        
        # Act & Assert
        with pytest.raises(UserAlreadyExistsError):
            UserService.create(mock_db_session, user_data)
    
    @patch('domains.user.service.hash_password')
    def test_create_user_sets_default_values(self, mock_hash_password, mock_db_session):
        """Verify user creation sets correct default values."""
        # Arrange
        mock_hash_password.return_value = "hashed"
        user_data = UserCreate(
            email="test@example.com",
            full_name="Test User",
            password="password123"
        )
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        UserService.create(mock_db_session, user_data)
        
        # Assert
        # Verify add was called with a User object
        call_args = mock_db_session.add.call_args[0][0]
        assert isinstance(call_args, User)
        assert call_args.is_active is True
        assert call_args.is_verified is False


class TestUserServiceRetrieval:
    """Tests for user retrieval operations."""
    
    def test_get_by_email_returns_user(self, mock_db_session, sample_user):
        """Verify get_by_email returns user when found."""
        # Arrange
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Act
        result = UserService.get_by_email(mock_db_session, "test@example.com")
        
        # Assert
        assert result == sample_user
        assert result.email == "test@example.com"
    
    def test_get_by_email_with_nonexistent_returns_none(self, mock_db_session):
        """Verify get_by_email returns None when user not found."""
        # Arrange
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = UserService.get_by_email(mock_db_session, "nonexistent@example.com")
        
        # Assert
        assert result is None
    
    def test_get_by_id_returns_user(self, mock_db_session, sample_user):
        """Verify get_by_id returns user when found."""
        # Arrange
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        
        # Act
        result = UserService.get_by_id(mock_db_session, 1)
        
        # Assert
        assert result == sample_user
        assert result.id == 1
    
    def test_get_by_id_with_invalid_id_raises_error(self, mock_db_session):
        """Verify get_by_id raises UserNotFoundError when user not found."""
        # Arrange
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundError):
            UserService.get_by_id(mock_db_session, 999)


class TestUserServiceUpdate:
    """Tests for user update operations."""
    
    @patch('domains.user.service.hash_password')
    def test_update_user_full_name(self, mock_hash_password, mock_db_session, sample_user):
        """Verify updating user full name."""
        # Arrange
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        update_data = UserUpdate(full_name="Updated Name")
        
        # Act
        result = UserService.update(mock_db_session, sample_user.id, update_data)
        
        # Assert
        assert result.full_name == "Updated Name"
        mock_db_session.commit.assert_called_once()
    
    @patch('domains.user.service.hash_password')
    def test_update_user_password_hashes_new_password(self, mock_hash_password, mock_db_session, sample_user):
        """Verify updating password hashes the new password."""
        # Arrange
        mock_hash_password.return_value = "new_hashed_password"
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_user
        update_data = UserUpdate(password="newpassword123")
        
        # Act
        result = UserService.update(mock_db_session, sample_user.id, update_data)
        
        # Assert
        mock_hash_password.assert_called_once_with("newpassword123")
        assert result.hashed_password == "new_hashed_password"


class TestUserServiceOTPManagement:
    """Tests for OTP-related operations."""
    
    def test_set_otp_updates_user_otp_fields(self, mock_db_session, sample_user):
        """Verify set_otp updates OTP code and expiry."""
        # Arrange
        otp_code = "123456"
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        # Act
        result = UserService.set_otp(mock_db_session, sample_user, otp_code, expires_at)
        
        # Assert
        assert result.otp_code == "123456"
        assert result.otp_expires_at == expires_at
        mock_db_session.commit.assert_called_once()
    
    def test_verify_user_clears_otp_and_marks_verified(self, mock_db_session, unverified_user):
        """Verify verify_user clears OTP and marks user as verified."""
        # Act
        result = UserService.verify_user(mock_db_session, unverified_user)
        
        # Assert
        assert result.is_verified is True
        assert result.otp_code is None
        assert result.otp_expires_at is None
        mock_db_session.commit.assert_called_once()
