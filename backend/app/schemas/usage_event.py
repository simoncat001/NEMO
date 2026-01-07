from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UsageEventBase(BaseModel):
    """使用记录基础模型"""
    user_id: int = Field(..., description="使用用户ID")
    operator_id: int = Field(..., description="操作员ID")
    project_id: int = Field(..., description="项目ID")
    tool_id: int = Field(..., description="工具ID")
    note: Optional[str] = Field(None, description="备注")
    remote_work: bool = Field(default=False, description="是否远程工作")
    training: bool = Field(default=False, description="是否培训")


class UsageEventCreate(UsageEventBase):
    """创建使用记录"""
    start: Optional[datetime] = Field(None, description="开始时间（默认当前时间）")
    pre_run_data: Optional[str] = Field(None, description="运行前数据（JSON）")


class UsageEventUpdate(BaseModel):
    """更新使用记录"""
    end: Optional[datetime] = Field(None, description="结束时间")
    note: Optional[str] = None
    run_data: Optional[str] = Field(None, description="运行数据（JSON）")
    validated: Optional[bool] = Field(None, description="是否已验证")
    validated_by_id: Optional[int] = Field(None, description="验证人ID")


class UsageEventEnd(BaseModel):
    """结束使用记录"""
    run_data: Optional[str] = Field(None, description="运行数据（JSON）")


class UsageEventResponse(UsageEventBase):
    """使用记录响应"""
    id: int
    start: datetime
    end: Optional[datetime] = None
    has_ended: int
    validated: bool
    validated_by_id: Optional[int] = None
    waived: bool
    waived_on: Optional[datetime] = None
    waived_by_id: Optional[int] = None
    pre_run_data: Optional[str] = None
    run_data: Optional[str] = None
    amount: float = Field(0.0, description="费用金额")
    
    model_config = ConfigDict(from_attributes=True)


class UsageEventDetail(UsageEventResponse):
    """使用记录详情（包含关系）"""
    # 可以添加用户、工具、项目的基本信息
    duration_minutes: Optional[int] = None
    is_in_progress: bool = False
    self_usage: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class UsageEventStats(BaseModel):
    """使用记录统计"""
    total_count: int
    total_duration_minutes: int
    average_duration_minutes: float
    validated_count: int
    pending_count: int
    by_tool: dict[int, int]  # tool_id -> count
    by_user: dict[int, int]  # user_id -> count
