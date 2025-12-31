from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.consumable import Consumable
from app.schemas.consumable import ConsumableCreate, ConsumableUpdate

class ConsumableService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_consumables(self, skip: int = 0, limit: int = 100) -> List[Consumable]:
        result = await self.db.execute(select(Consumable).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_consumable(self, consumable_id: int) -> Optional[Consumable]:
        result = await self.db.execute(select(Consumable).where(Consumable.id == consumable_id))
        return result.scalar_one_or_none()

    async def create_consumable(self, consumable: ConsumableCreate) -> Consumable:
        db_consumable = Consumable(**consumable.model_dump())
        self.db.add(db_consumable)
        await self.db.commit()
        await self.db.refresh(db_consumable)
        return db_consumable

    async def update_consumable(self, consumable_id: int, consumable: ConsumableUpdate) -> Optional[Consumable]:
        db_consumable = await self.get_consumable(consumable_id)
        if not db_consumable:
            return None
        
        update_data = consumable.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_consumable, key, value)
            
        await self.db.commit()
        await self.db.refresh(db_consumable)
        return db_consumable

    async def delete_consumable(self, consumable_id: int) -> bool:
        db_consumable = await self.get_consumable(consumable_id)
        if not db_consumable:
            return False
            
        await self.db.delete(db_consumable)
        await self.db.commit()
        return True
