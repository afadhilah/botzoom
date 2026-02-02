from passlib.context import CryptContext
import secrets
import string


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_otp(length: int = 6) -> str:
    """Generate a random numeric OTP."""
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_random_token(length: int = 32) -> str:
    """Generate a random secure token."""
    return secrets.token_urlsafe(length)
