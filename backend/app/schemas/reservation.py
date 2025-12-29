"""
Reservation Pydantic schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ReservationBase(BaseModel):
    """预约基础模型"""
    tool_id: Optional[int] = None
    area_id: Optional[int] = None
    project_id: int
    start: datetime
    end: datetime
    additional_information: str = ""


class ReservationCreate(ReservationBase):
    """创建预约"""
    user_id: int


class ReservationUpdate(BaseModel):
    """更新预约"""
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    additional_information: Optional[str] = None
    cancelled: Optional[bool] = None


class ReservationInDB(ReservationBase):
    """数据库中的预约"""
    id: int
    user_id: int
    cancelled: bool = False
    missed: bool = False
    
    class Config:
        from_attributes = True


class Reservation(ReservationInDB):
    """返回给客户端的预约"""
    pass
