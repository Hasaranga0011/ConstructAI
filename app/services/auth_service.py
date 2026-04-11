from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta

class AuthService:
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate):
        """Register a new user"""
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User registration failed"
            )
    
    @staticmethod
    def login_user(db: Session, email: str, password: str):
        """Authenticate user and return token"""
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "is_active": user.is_active
            }
        }
    
    @staticmethod
    def get_current_user(db: Session, email: str):
        """Get user by email"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def request_password_reset(db: Session, email: str):
        """Request password reset - send email with reset link"""
        from app.core.security import create_password_reset_token
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists (security best practice)
            return {"message": "If email exists, reset link has been sent"}
        
        # Generate reset token
        reset_token = create_password_reset_token(email)
        
        # TODO: Send email with reset token
        # For now, just return the token (in production, send via email)
        return {
            "message": "Password reset link sent to your email",
            "reset_token": reset_token  # Remove in production!
        }
    
    @staticmethod
    def reset_password(db: Session, token: str, new_password: str):
        """Reset password using token"""
        from app.core.security import verify_password_reset_token
        
        email = verify_password_reset_token(token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        return {"message": "Password reset successfully"}