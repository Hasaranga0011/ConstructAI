from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import AuthService
from app.config.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **email**: valid email address
    - **username**: unique username (3-50 characters)
    - **password**: strong password (8-100 characters)
    - **full_name**: optional full name
    """
    return AuthService.register_user(db, user_data)

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user with email and password
    
    Returns JWT access token
    """
    result = AuthService.login_user(
        db, 
        user_credentials.email, 
        user_credentials.password
    )
    return {"access_token": result["access_token"], "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current logged in user information
    """
    return current_user

@router.get("/verify-token")
def verify_token(current_user: User = Depends(get_current_user)):
    """
    Verify if token is valid
    """
    return {"valid": True, "user_id": current_user.id}