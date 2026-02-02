from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.session import get_db
from domains.auth.utils import get_current_active_user
from domains.user.model import User
from domains.user.schemas import UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user information."""
    return current_user
