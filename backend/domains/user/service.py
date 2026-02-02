from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from domains.user.model import User
from domains.user.schemas import UserCreate, UserUpdate
from core.security import hash_password
from core.exceptions import UserNotFoundError, UserAlreadyExistsError


class UserService:
    """Service for user domain operations."""
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        """Get user by ID."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError()
        return user
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create(db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        existing_user = UserService.get_by_email(db, user_data.email)
        if existing_user:
            raise UserAlreadyExistsError()
        
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            is_active=True,
            is_verified=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """Update user information."""
        user = UserService.get_by_id(db, user_id)
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.password is not None:
            user.hashed_password = hash_password(user_data.password)
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def set_otp(db: Session, user: User, otp_code: str, expires_at: datetime) -> User:
        """Set OTP for user verification."""
        user.otp_code = otp_code
        user.otp_expires_at = expires_at
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def verify_user(db: Session, user: User) -> User:
        """Mark user as verified."""
        user.is_verified = True
        user.otp_code = None
        user.otp_expires_at = None
        db.commit()
        db.refresh(user)
        return user
