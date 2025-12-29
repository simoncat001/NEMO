"""
Tool Pydantic schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class ToolBase(BaseModel):
    """工具基础模型"""
    name: str = Field(..., min_length=1, max_length=200)
    visible: bool = True
    operational: bool = False
    description: str = ""
    location: Optional[str] = None
    phone_number: Optional[str] = None


class ToolCreate(ToolBase):
    """创建工具"""
    primary_owner_id: int


class ToolUpdate(BaseModel):
    """更新工具"""
    name: Optional[str] = None
    visible: Optional[bool] = None
    operational: Optional[bool] = None
    description: Optional[str] = None
    location: Optional[str] = None
    phone_number: Optional[str] = None


class ToolInDB(ToolBase):
    """数据库中的工具"""
    id: int
    _primary_owner_id: int
    
    class Config:
        from_attributes = True


class Tool(ToolInDB):
    """返回给客户端的工具"""
    pass
