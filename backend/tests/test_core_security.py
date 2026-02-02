"""
Unit tests for core/security.py
Tests password hashing, verification, and OTP generation.
"""
import pytest
from core.security import hash_password, verify_password, generate_otp, generate_random_token


class TestPasswordHashing:
    """Tests for password hashing and verification."""
    
    def test_hash_password_returns_different_hash_each_time(self):
        """Verify that bcrypt generates different hashes for same password (salting)."""
        password = "mypassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2, "Hashes should be different due to random salt"
        assert len(hash1) > 0
        assert len(hash2) > 0
    
    def test_verify_password_with_correct_password(self):
        """Verify that correct password passes verification."""
        password = "correctpassword"
        hashed = hash_password(password)
        
        result = verify_password(password, hashed)
        
        assert result is True
    
    def test_verify_password_with_wrong_password(self):
        """Verify that wrong password fails verification."""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False
    
    def test_verify_password_with_empty_password(self):
        """Verify that empty password fails verification."""
        password = "correctpassword"
        hashed = hash_password(password)
        
        result = verify_password("", hashed)
        
        assert result is False


class TestOTPGeneration:
    """Tests for OTP generation."""
    
    def test_generate_otp_returns_6_digits(self):
        """Verify OTP has correct length."""
        otp = generate_otp(6)
        
        assert len(otp) == 6
    
    def test_generate_otp_is_numeric(self):
        """Verify OTP contains only digits."""
        otp = generate_otp(6)
        
        assert otp.isdigit(), "OTP should contain only numeric characters"
    
    def test_generate_otp_custom_length(self):
        """Verify OTP respects custom length parameter."""
        otp_4 = generate_otp(4)
        otp_8 = generate_otp(8)
        
        assert len(otp_4) == 4
        assert len(otp_8) == 8
    
    def test_generate_otp_is_random(self):
        """Verify OTP generation produces different values."""
        otp1 = generate_otp(6)
        otp2 = generate_otp(6)
        
        # Very unlikely to be the same (1 in 1 million chance)
        assert otp1 != otp2


class TestRandomTokenGeneration:
    """Tests for random token generation."""
    
    def test_generate_random_token_default_length(self):
        """Verify token generation with default length."""
        token = generate_random_token()
        
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_generate_random_token_custom_length(self):
        """Verify token respects custom length parameter."""
        token_16 = generate_random_token(16)
        token_64 = generate_random_token(64)
        
        # URL-safe base64 encoding may vary in length slightly
        assert len(token_16) > 0
        assert len(token_64) > len(token_16)
    
    def test_generate_random_token_is_unique(self):
        """Verify token generation produces unique values."""
        token1 = generate_random_token(32)
        token2 = generate_random_token(32)
        
        assert token1 != token2
