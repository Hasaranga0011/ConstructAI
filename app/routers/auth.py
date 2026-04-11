from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth_service import AuthService
from app.config.database import get_db
from app.models.user import User
from app.schemas.auth import ForgotPasswordRequest, PasswordResetRequest, TokenResponse, UserLoginRequest
from app.core.security import decode_access_token, create_password_reset_token, verify_password_reset_token, get_password_hash

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    user = AuthService.register_user(db, user_data)
    return user

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user and get access token"""
    result = AuthService.login_user(db, user_data.email, user_data.password)
    return result

@router.get("/me", response_model=UserResponse)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current logged-in user"""
    token_data = decode_access_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    user = AuthService.get_current_user(db, token_data.email)
    return user

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset - send reset link to email"""
    return AuthService.request_password_reset(db, request.email)

@router.post("/reset-password")
def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Reset password using token from email"""
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    return AuthService.reset_password(db, request.token, request.new_password)