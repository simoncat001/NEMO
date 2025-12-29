from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# AccountType Schemas
class AccountTypeBase(BaseModel):
    """账户类型基础模型"""
    name: str = Field(..., max_length=200, description="账户类型名称")
    display_order: int = Field(default=0, description="显示顺序")


class AccountTypeCreate(AccountTypeBase):
    """创建账户类型"""
    pass


class AccountTypeUpdate(BaseModel):
    """更新账户类型"""
    name: Optional[str] = Field(None, max_length=200)
    display_order: Optional[int] = None


class AccountTypeResponse(AccountTypeBase):
    """账户类型响应"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


# Account Schemas
class AccountBase(BaseModel):
    """账户基础模型"""
    name: str = Field(..., max_length=100, description="账户名称")
    note: Optional[str] = Field(None, description="备注")
    type_id: Optional[int] = Field(None, description="账户类型ID")
    start_date: Optional[date] = Field(None, description="开始日期")
    active: bool = Field(default=True, description="是否激活")


class AccountCreate(AccountBase):
    """创建账户"""
    pass


class AccountUpdate(BaseModel):
    """更新账户"""
    name: Optional[str] = Field(None, max_length=100)
    note: Optional[str] = None
    type_id: Optional[int] = None
    start_date: Optional[date] = None
    active: Optional[bool] = None


class AccountResponse(AccountBase):
    """账户响应"""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class AccountDetail(AccountResponse):
    """账户详情（包含关系）"""
    type: Optional[AccountTypeResponse] = None
    
    model_config = ConfigDict(from_attributes=True)
