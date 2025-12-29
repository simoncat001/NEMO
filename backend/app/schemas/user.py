"""
User Pydantic schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    badge_number: Optional[int] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    """创建用户"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """更新用户"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_staff: Optional[bool] = None
    badge_number: Optional[int] = None
    phone: Optional[str] = None


class UserInDB(UserBase):
    """数据库中的用户"""
    id: int
    date_joined: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """返回给客户端的用户"""
    pass


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class Token(BaseModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[User] = None


class TokenData(BaseModel):
    """Token数据"""
    username: Optional[str] = None
