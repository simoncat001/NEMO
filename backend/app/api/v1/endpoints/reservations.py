"""
Reservation API endpoints
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.reservation import Reservation, ReservationCreate, ReservationUpdate
from app.services.reservation_service import ReservationService

router = APIRouter()


@router.get("/", response_model=List[Reservation])
async def get_reservations(
    skip: int = 0,
    limit: int = 100,
    user_id: int = None,
    tool_id: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    db: AsyncSession = Depends(get_db)
):
    """获取预约列表"""
    service = ReservationService(db)
    reservations = await service.get_reservations(
        skip=skip,
        limit=limit,
        user_id=user_id,
        tool_id=tool_id,
        start_date=start_date,
        end_date=end_date
    )
    return reservations


@router.get("/{reservation_id}", response_model=Reservation)
async def get_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个预约"""
    service = ReservationService(db)
    reservation = await service.get_reservation(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    return reservation


@router.post("/", response_model=Reservation, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation_in: ReservationCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新预约"""
    service = ReservationService(db)
    
    # 验证时间
    if reservation_in.start >= reservation_in.end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # 检查冲突
    has_conflict = await service.check_reservation_conflict(
        tool_id=reservation_in.tool_id,
        start=reservation_in.start,
        end=reservation_in.end
    )
    if has_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot is already reserved"
        )
    
    reservation = await service.create_reservation(reservation_in)
    return reservation


@router.put("/{reservation_id}", response_model=Reservation)
async def update_reservation(
    reservation_id: int,
    reservation_in: ReservationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新预约"""
    service = ReservationService(db)
    reservation = await service.update_reservation(reservation_id, reservation_in)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """取消预约"""
    service = ReservationService(db)
    success = await service.cancel_reservation(reservation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    return None
