from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import verify_password, get_password_hash, create_access_token
from core.config import settings
from api.deps import get_current_user
from models.user import User
from schemas.user import UserResponse, UserCreate
from schemas.token import Token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Create a new user.
    """
    print(f"DEBUG: Attempting to register email: {user_in.email}")
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        print(f"DEBUG: User already exists: {user_in.email}")
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    try:
        hashed_password = get_password_hash(user_in.password)
        user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"DEBUG: User created successfully: {user.id}")
        return user
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to create user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "has_profile": bool(user.user_info)
    }


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user.
    """
    return current_user
