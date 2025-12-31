"""
User API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """获取当前登录用户信息"""
    return current_user


@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    service = UserService(db)
    users = await service.get_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个用户"""
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新用户"""
    service = UserService(db)
    
    # 检查用户名是否已存在
    existing_user = await service.get_user_by_username(user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 检查邮箱是否已存在
    existing_email = await service.get_user_by_email(user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = await service.create_user(user_in)
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新用户"""
    service = UserService(db)
    user = await service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除用户"""
    service = UserService(db)
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None
