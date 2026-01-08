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
    requires_reservation: bool = True
    description: str = ""
    location: Optional[str] = None
    phone_number: Optional[str] = None


class ToolCreate(ToolBase):
    """创建工具"""
    primary_owner_id: Optional[int] = None


class ToolUpdate(BaseModel):
    """更新工具"""
    name: Optional[str] = None
    visible: Optional[bool] = None
    operational: Optional[bool] = None
    requires_reservation: Optional[bool] = None
    description: Optional[str] = None
    location: Optional[str] = None
    price_type: Optional[int] = None
    price_per_use: Optional[float] = None
    price_per_hour: Optional[float] = None
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


class ToolEnable(BaseModel):
    """启用工具请求"""
    user_id: int = Field(..., description="使用用户ID")
    project_id: int = Field(..., description="项目ID")
    operator_id: Optional[int] = Field(None, description="操作员ID（如果不传则为当前用户）")
    note: Optional[str] = None


class ToolDisable(BaseModel):
    """禁用工具请求"""
    note: Optional[str] = None
    run_data: Optional[str] = None
