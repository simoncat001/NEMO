from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.consumable import Consumable, ConsumableCreate, ConsumableUpdate
from app.services.consumable_service import ConsumableService
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Consumable])
async def read_consumables(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取耗材列表"""
    service = ConsumableService(db)
    return await service.get_consumables(skip=skip, limit=limit)

@router.post("/", response_model=Consumable)
async def create_consumable(
    consumable: ConsumableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建耗材"""
    service = ConsumableService(db)
    return await service.create_consumable(consumable)

@router.get("/{consumable_id}", response_model=Consumable)
async def read_consumable(
    consumable_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取特定耗材"""
    service = ConsumableService(db)
    db_consumable = await service.get_consumable(consumable_id)
    if db_consumable is None:
        raise HTTPException(status_code=404, detail="Consumable not found")
    return db_consumable

@router.put("/{consumable_id}", response_model=Consumable)
async def update_consumable(
    consumable_id: int,
    consumable: ConsumableUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新耗材"""
    service = ConsumableService(db)
    db_consumable = await service.update_consumable(consumable_id, consumable)
    if db_consumable is None:
        raise HTTPException(status_code=404, detail="Consumable not found")
    return db_consumable

@router.delete("/{consumable_id}", response_model=bool)
async def delete_consumable(
    consumable_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除耗材"""
    service = ConsumableService(db)
    success = await service.delete_consumable(consumable_id)
    if not success:
        raise HTTPException(status_code=404, detail="Consumable not found")
    return True
