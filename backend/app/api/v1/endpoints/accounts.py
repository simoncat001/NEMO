from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.account import (
    AccountCreate,
    AccountDetail,
    AccountResponse,
    AccountTypeCreate,
    AccountTypeResponse,
    AccountTypeUpdate,
    AccountUpdate,
)
from app.services.account_service import AccountService

router = APIRouter()


# AccountType endpoints
@router.get("/account-types", response_model=List[AccountTypeResponse])
async def get_account_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取账户类型列表"""
    return await AccountService.get_account_types(db, skip, limit)


@router.post("/account-types", response_model=AccountTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_account_type(
    account_type: AccountTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建账户类型（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can create account types"
        )
    return await AccountService.create_account_type(db, account_type)


@router.get("/account-types/{type_id}", response_model=AccountTypeResponse)
async def get_account_type(
    type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取账户类型详情"""
    account_type = await AccountService.get_account_type(db, type_id)
    if not account_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account type not found"
        )
    return account_type


@router.put("/account-types/{type_id}", response_model=AccountTypeResponse)
async def update_account_type(
    type_id: int,
    account_type: AccountTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新账户类型（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update account types"
        )
    
    updated = await AccountService.update_account_type(db, type_id, account_type)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account type not found"
        )
    return updated


@router.delete("/account-types/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account_type(
    type_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除账户类型（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can delete account types"
        )
    
    deleted = await AccountService.delete_account_type(db, type_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account type not found"
        )


# Account endpoints
@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取账户列表"""
    if not current_user.is_staff and not current_user.is_superuser:
        return []
        
    return await AccountService.get_accounts(db, skip, limit, active_only)


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建账户（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can create accounts"
        )
    
    # 检查名称是否已存在
    existing = await AccountService.get_account_by_name(db, account.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account with this name already exists"
        )
    
    return await AccountService.create_account(db, account)


@router.get("/{account_id}", response_model=AccountDetail)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取账户详情"""
    account = await AccountService.get_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新账户（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update accounts"
        )
    
    updated = await AccountService.update_account(db, account_id, account)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return updated


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除账户（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can delete accounts"
        )
    
    deleted = await AccountService.delete_account(db, account_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )


@router.post("/accounts/{account_id}/activate", response_model=AccountResponse)
async def activate_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """激活账户（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can activate accounts"
        )
    
    account = await AccountService.activate_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account


@router.post("/accounts/{account_id}/deactivate", response_model=AccountResponse)
async def deactivate_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """停用账户（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can deactivate accounts"
        )
    
    account = await AccountService.deactivate_account(db, account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account
