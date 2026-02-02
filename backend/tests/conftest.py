"""
Pytest configuration and shared fixtures for unit tests.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock
from sqlalchemy.orm import Session

from domains.user.model import User
from core.config import settings


@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy database session."""
    session = MagicMock(spec=Session)
    # Setup method chaining for query().filter().first()
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_filter.first.return_value = None
    mock_query.filter.return_value = mock_filter
    session.query.return_value = mock_query
    return session


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qvLmvPGS2",  # "password123"
        is_active=True,
        is_verified=True,
        otp_code=None,
        otp_expires_at=None,
        created_at=datetime.utcnow(),
        updated_at=None
    )
    return user


@pytest.fixture
def unverified_user():
    """Create an unverified user for testing."""
    user = User(
        id=2,
        email="unverified@example.com",
        full_name="Unverified User",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qvLmvPGS2",
        is_active=True,
        is_verified=False,
        otp_code="123456",
        otp_expires_at=datetime.utcnow() + timedelta(minutes=10),
        created_at=datetime.utcnow(),
        updated_at=None
    )
    return user


@pytest.fixture
def expired_otp_user():
    """Create a user with expired OTP."""
    user = User(
        id=3,
        email="expired@example.com",
        full_name="Expired OTP User",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7qvLmvPGS2",
        is_active=True,
        is_verified=False,
        otp_code="654321",
        otp_expires_at=datetime.utcnow() - timedelta(minutes=1),  # Expired
        created_at=datetime.utcnow(),
        updated_at=None
    )
    return user


@pytest.fixture
def valid_jwt_payload():
    """Sample JWT payload for testing."""
    return {
        "sub": "1",
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    mock_config = Mock()
    mock_config.JWT_SECRET_KEY = "test-secret-key"
    mock_config.JWT_ALGORITHM = "HS256"
    mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    mock_config.REFRESH_TOKEN_EXPIRE_DAYS = 7
    mock_config.OTP_LENGTH = 6
    mock_config.OTP_EXPIRE_MINUTES = 10
    mock_config.PASSWORD_MIN_LENGTH = 8
    return mock_config
