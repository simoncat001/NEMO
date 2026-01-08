from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.account import Account, AccountType
from app.models.user import User
from app.schemas.account import AccountCreate, AccountTypeCreate, AccountTypeUpdate, AccountUpdate


class AccountService:
    """账户服务"""

    @staticmethod
    async def get_or_create_user_account(db: AsyncSession, user: User) -> Account:
        """Get or create the single account bound to a user.

        Behavior:
        - If an account already exists with account.user_id == user.id, return it.
        - Else, if a legacy account exists named like the username and has NULL user_id, bind it.
        - Else, create a new account (name=username, user_id=user.id).
        """
        existing = await db.scalar(select(Account).where(Account.user_id == user.id))
        if existing:
            return existing

        legacy = await db.scalar(
            select(Account).where(Account.user_id.is_(None), Account.name == user.username)
        )
        if legacy:
            legacy.user_id = user.id
            if legacy.active is None:
                legacy.active = True
            await db.commit()
            await db.refresh(legacy)
            return legacy

        account = Account(name=user.username, user_id=user.id, active=True)
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account

    @staticmethod
    async def get_account_types(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[AccountType]:
        """获取账户类型列表"""
        result = await db.execute(
            select(AccountType)
            .order_by(AccountType.display_order, AccountType.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_account_type(db: AsyncSession, type_id: int) -> Optional[AccountType]:
        """获取单个账户类型"""
        result = await db.execute(
            select(AccountType).where(AccountType.id == type_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_account_type(
        db: AsyncSession,
        account_type_data: AccountTypeCreate
    ) -> AccountType:
        """创建账户类型"""
        account_type = AccountType(**account_type_data.model_dump())
        db.add(account_type)
        await db.commit()
        await db.refresh(account_type)
        return account_type

    @staticmethod
    async def update_account_type(
        db: AsyncSession,
        type_id: int,
        account_type_data: AccountTypeUpdate
    ) -> Optional[AccountType]:
        """更新账户类型"""
        result = await db.execute(
            select(AccountType).where(AccountType.id == type_id)
        )
        account_type = result.scalar_one_or_none()
        
        if not account_type:
            return None
        
        update_data = account_type_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account_type, field, value)
        
        await db.commit()
        await db.refresh(account_type)
        return account_type

    @staticmethod
    async def delete_account_type(db: AsyncSession, type_id: int) -> bool:
        """删除账户类型"""
        result = await db.execute(
            select(AccountType).where(AccountType.id == type_id)
        )
        account_type = result.scalar_one_or_none()
        
        if not account_type:
            return False
        
        await db.delete(account_type)
        await db.commit()
        return True

    @staticmethod
    async def get_accounts(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> List[Account]:
        """获取账户列表"""
        query = select(Account).options(selectinload(Account.type))
        
        if active_only:
            query = query.where(Account.active == True)
        
        query = query.order_by(Account.name).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_account(db: AsyncSession, account_id: int) -> Optional[Account]:
        """获取单个账户"""
        result = await db.execute(
            select(Account)
            .options(
                selectinload(Account.type),
                selectinload(Account.projects)
            )
            .where(Account.id == account_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_account_by_name(db: AsyncSession, name: str) -> Optional[Account]:
        """根据名称获取账户"""
        result = await db.execute(
            select(Account).where(Account.name == name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_account(
        db: AsyncSession,
        account_data: AccountCreate
    ) -> Account:
        """创建账户"""
        account = Account(**account_data.model_dump())
        db.add(account)
        await db.commit()
        await db.refresh(account)
        return account

    @staticmethod
    async def update_account(
        db: AsyncSession,
        account_id: int,
        account_data: AccountUpdate
    ) -> Optional[Account]:
        """更新账户"""
        result = await db.execute(
            select(Account).where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            return None
        
        update_data = account_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(account, field, value)
        
        await db.commit()
        await db.refresh(account)
        return account

    @staticmethod
    async def delete_account(db: AsyncSession, account_id: int) -> bool:
        """删除账户"""
        result = await db.execute(
            select(Account).where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            return False
        
        await db.delete(account)
        await db.commit()
        return True

    @staticmethod
    async def activate_account(db: AsyncSession, account_id: int) -> Optional[Account]:
        """激活账户"""
        result = await db.execute(
            select(Account).where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            return None
        
        account.active = True
        await db.commit()
        await db.refresh(account)
        return account

    @staticmethod
    async def deactivate_account(db: AsyncSession, account_id: int) -> Optional[Account]:
        """停用账户"""
        result = await db.execute(
            select(Account).where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            return None
        
        account.active = False
        await db.commit()
        await db.refresh(account)
        return account
