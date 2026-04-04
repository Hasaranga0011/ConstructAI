from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    PROJECT_MANAGER = "project_manager"
    SITE_ENGINEER = "site_engineer"

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRoleEnum = Field(default=UserRoleEnum.SITE_ENGINEER)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRoleEnum
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None