from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from core.config import settings
from core.exceptions import InvalidTokenError


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")


def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify access token and return payload."""
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid token type")
    
    return payload


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Verify refresh token and return payload."""
    payload = decode_token(token)
    
    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid token type")
    
    return payload
