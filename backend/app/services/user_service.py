"""
User service layer
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取用户列表"""
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """获取单个用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        if user:
            # Fetch password from local_auth
            from sqlalchemy import text
            auth_result = await self.db.execute(
                text("SELECT hashed_password FROM local_auth WHERE user_id = :uid"),
                {"uid": user.id}
            )
            auth_row = auth_result.fetchone()
            if auth_row:
                user.hashed_password = auth_row[0]
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, user_in: UserCreate) -> User:
        """创建用户"""
        # hashed_password is not in User model anymore
        user = User(
            username=user_in.username,
            email=user_in.email,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            # hashed_password=get_password_hash(user_in.password),
            is_active=user_in.is_active,
            is_staff=user_in.is_staff,
            is_superuser=user_in.is_superuser,
            badge_number=user_in.badge_number,
            phone=user_in.phone,
            # Set required fields with defaults
            domain='LOCAL',
            is_technician=False,
            training_required=False,
            is_service_personnel=False,
            is_facility_manager=False,
            is_accounting_officer=False,
            is_user_office=False
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # Insert password into local_auth
        hashed = get_password_hash(user_in.password)
        await self.db.execute(
            text("INSERT INTO local_auth (user_id, hashed_password) VALUES (:uid, :pwd)"),
            {"uid": user.id, "pwd": hashed}
        )
        await self.db.commit()
        
        user.hashed_password = hashed
        return user
    
    async def update_user(self, user_id: int, user_in: UserUpdate) -> Optional[User]:
        """更新用户"""
        user = await self.get_user(user_id)
        if not user:
            return None
        
        update_data = user_in.model_dump(exclude_unset=True)
        
        # 如果更新密码，需要哈希
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user = await self.get_user(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        return True
    
    async def update_last_login(self, user_id: int) -> None:
        """更新最后登录时间"""
        user = await self.get_user(user_id)
        if user:
            user.last_login = datetime.utcnow()
            await self.db.commit()
