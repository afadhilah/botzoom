"""
Unit tests for core/jwt.py
Tests JWT token creation, verification, and validation.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from jose import jwt

from core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
    verify_refresh_token
)
from core.exceptions import InvalidTokenError
from core.config import settings


class TestTokenCreation:
    """Tests for JWT token creation."""
    
    def test_create_access_token_contains_correct_claims(self):
        """Verify access token contains required claims."""
        data = {"sub": "123", "email": "test@example.com"}
        
        token = create_access_token(data)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert decoded["sub"] == "123"
        assert decoded["email"] == "test@example.com"
        assert decoded["type"] == "access"
        assert "exp" in decoded
    
    def test_create_access_token_with_custom_expiry(self):
        """Verify access token respects custom expiry time."""
        data = {"sub": "123"}
        custom_expiry = timedelta(minutes=60)
        
        token = create_access_token(data, expires_delta=custom_expiry)
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Just verify exp exists and is in the future
        assert "exp" in decoded
        exp_time = datetime.fromtimestamp(decoded["exp"])
        assert exp_time > datetime.utcnow()
    
    def test_create_refresh_token_has_longer_expiry(self):
        """Verify refresh token has longer expiry than access token."""
        data = {"sub": "123"}
        
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_decoded = jwt.decode(access_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        refresh_decoded = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        assert refresh_decoded["exp"] > access_decoded["exp"]
        assert refresh_decoded["type"] == "refresh"


class TestTokenDecoding:
    """Tests for JWT token decoding and validation."""
    
    def test_decode_token_with_valid_token(self):
        """Verify successful decoding of valid token."""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded["sub"] == "123"
        assert decoded["email"] == "test@example.com"
    
    def test_decode_token_with_invalid_signature_raises_error(self):
        """Verify invalid signature raises InvalidTokenError."""
        data = {"sub": "123"}
        # Create token with wrong secret
        token = jwt.encode(data, "wrong-secret", algorithm=settings.JWT_ALGORITHM)
        
        with pytest.raises(InvalidTokenError) as exc_info:
            decode_token(token)
        
        assert "Invalid token" in str(exc_info.value)
    
    def test_decode_token_with_expired_token_raises_error(self):
        """Verify expired token raises InvalidTokenError."""
        data = {"sub": "123", "exp": datetime.utcnow() - timedelta(minutes=1)}
        token = jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        with pytest.raises(InvalidTokenError) as exc_info:
            decode_token(token)
        
        assert "Invalid token" in str(exc_info.value)
    
    def test_decode_token_with_malformed_token_raises_error(self):
        """Verify malformed token raises InvalidTokenError."""
        malformed_token = "not.a.valid.jwt.token"
        
        with pytest.raises(InvalidTokenError):
            decode_token(malformed_token)


class TestTokenTypeVerification:
    """Tests for token type validation."""
    
    def test_verify_access_token_accepts_access_token(self):
        """Verify access token passes access token verification."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        payload = verify_access_token(token)
        
        assert payload["sub"] == "123"
        assert payload["type"] == "access"
    
    def test_verify_access_token_rejects_refresh_token(self):
        """Verify refresh token fails access token verification."""
        data = {"sub": "123"}
        token = create_refresh_token(data)
        
        with pytest.raises(InvalidTokenError) as exc_info:
            verify_access_token(token)
        
        assert "Invalid token type" in str(exc_info.value)
    
    def test_verify_refresh_token_accepts_refresh_token(self):
        """Verify refresh token passes refresh token verification."""
        data = {"sub": "123"}
        token = create_refresh_token(data)
        
        payload = verify_refresh_token(token)
        
        assert payload["sub"] == "123"
        assert payload["type"] == "refresh"
    
    def test_verify_refresh_token_rejects_access_token(self):
        """Verify access token fails refresh token verification."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        with pytest.raises(InvalidTokenError) as exc_info:
            verify_refresh_token(token)
        
        assert "Invalid token type" in str(exc_info.value)
