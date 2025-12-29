"""
Project Pydantic schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """项目基础模型"""
    name: str = Field(..., min_length=1, max_length=200)
    application_identifier: str = Field(..., min_length=1, max_length=200)
    active: bool = True


class ProjectCreate(ProjectBase):
    """创建项目"""
    account_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    """更新项目"""
    name: Optional[str] = None
    active: Optional[bool] = None
    account_id: Optional[int] = None


class ProjectInDB(ProjectBase):
    """数据库中的项目"""
    id: int
    start_date: Optional[datetime] = None
    account_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class Project(ProjectInDB):
    """返回给客户端的项目"""
    pass
