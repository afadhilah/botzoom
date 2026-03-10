from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from core.jwt import verify_access_token
from core.exceptions import InvalidTokenError
from domains.user.model import User
from domains.user.service import UserService
from database.session import get_db


security = HTTPBearer(auto_error=False)  # Auto_error=False makes it optional


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    
    # ============================================================
    # AUTH DISABLED - Return first user without token validation
    # ============================================================
    print("[AUTH] ⚠️ Token validation disabled - returning first user")
    
    try:
        users = db.query(User).limit(1).all()
        if users:
            return users[0]
            
        # No users in DB, create dummy
        print("[AUTH] No users in database, returning dummy user")
        dummy = User(
            id=999,
            email="demo@example.com",
            full_name="Demo User",
            is_active=True,
            is_verified=True
        )
        return dummy
    except Exception as e:
        print(f"[AUTH] Error: {e}, returning dummy user")
        dummy = User(
            id=999,
            email="demo@example.com",
            full_name="Demo User",
            is_active=True,
            is_verified=True
        )
        return dummy
    
    # ============================================================
    # ORIGINAL CODE - DISABLED
    # ============================================================
    # try:
    #     token = credentials.credentials
    #     payload = verify_access_token(token)
    #     user_id = int(payload.get("sub"))
    #     
    #     user = UserService.get_by_id(db, user_id)
    #     
    #     if not user.is_active:
    #         raise HTTPException(
    #             status_code=status.HTTP_403_FORBIDDEN,
    #             detail="User account is deactivated"
    #         )
    #     
    #     return user
    #     
    # except InvalidTokenError as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail=str(e),
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Could not validate credentials",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )


def get_current_active_user(
    db: Session = Depends(get_db)
) -> User:
    """Get current active and verified user."""
    
    # ============================================================
    # AUTH DISABLED - Return dummy user without validation
    # ============================================================
    print("[AUTH] ⚠️ Authentication disabled - using first user or dummy")
    
    # Try to get first user from database
    try:
        users = db.query(User).filter(User.is_active == True).limit(1).all()
        if users:
            print(f"[AUTH] Using user: {users[0].email}")
            return users[0]
    except Exception as e:
        print(f"[AUTH] Error getting user from DB: {e}")
    
    # Return dummy user object if DB fail
    print("[AUTH] Using dummy user object")
    dummy_user = User(
        id=999,
        email="demo@localhost.com",
        full_name="Demo User (Auth Disabled)",
        is_active=True,
        is_verified=True
    )
    return dummy_user
