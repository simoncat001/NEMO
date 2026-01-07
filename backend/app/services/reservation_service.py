"""
Reservation service layer
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationUpdate


class ReservationService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_reservations(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: int = None,
        tool_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Reservation]:
        """获取预约列表"""
        query = select(Reservation).where(Reservation.cancelled == False)
        
        if user_id:
            query = query.where(Reservation.user_id == user_id)
        if tool_id:
            query = query.where(Reservation.tool_id == tool_id)
        if start_date:
            query = query.where(Reservation.end >= start_date)
        if end_date:
            query = query.where(Reservation.start <= end_date)
        
        query = query.offset(skip).limit(limit).order_by(Reservation.start.desc())
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_reservation(self, reservation_id: int) -> Optional[Reservation]:
        """获取单个预约"""
        result = await self.db.execute(
            select(Reservation).where(Reservation.id == reservation_id)
        )
        return result.scalar_one_or_none()
    
    async def check_reservation_conflict(
        self,
        tool_id: int,
        start: datetime,
        end: datetime,
        exclude_id: int = None
    ) -> bool:
        """检查预约冲突"""
        query = select(Reservation).where(
            and_(
                Reservation.tool_id == tool_id,
                Reservation.cancelled == False,
                or_(
                    and_(Reservation.start < end, Reservation.end > start),
                )
            )
        )
        
        if exclude_id:
            query = query.where(Reservation.id != exclude_id)
        
        result = await self.db.execute(query)
        conflicts = result.scalars().all()
        return len(conflicts) > 0
    
    async def create_reservation(self, reservation_in: ReservationCreate, creator_id: int) -> Reservation:
        """创建预约"""
        reservation = Reservation(
            user_id=reservation_in.user_id,
            creator_id=creator_id,
            # creation_time=datetime.utcnow(),
            # title="",
            short_notice=False,
            tool_id=reservation_in.tool_id,
            area_id=reservation_in.area_id,
            project_id=reservation_in.project_id,
            start=reservation_in.start,
            end=reservation_in.end,
            additional_information=reservation_in.additional_information,
        )
        self.db.add(reservation)
        await self.db.commit()
        await self.db.refresh(reservation)
        return reservation
    
    async def update_reservation(
        self,
        reservation_id: int,
        reservation_in: ReservationUpdate
    ) -> Optional[Reservation]:
        """更新预约"""
        reservation = await self.get_reservation(reservation_id)
        if not reservation:
            return None
        
        update_data = reservation_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(reservation, field, value)
        
        await self.db.commit()
        await self.db.refresh(reservation)
        return reservation
    
    async def cancel_reservation(self, reservation_id: int) -> bool:
        """取消预约"""
        reservation = await self.get_reservation(reservation_id)
        if not reservation:
            return False
        
        reservation.cancelled = True
        reservation.cancellation_time = datetime.utcnow()
        await self.db.commit()
        return True
