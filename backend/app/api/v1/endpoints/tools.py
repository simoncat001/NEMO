"""
Tool API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.tool import Tool, ToolCreate, ToolUpdate, ToolEnable, ToolDisable
from app.schemas.usage_event import UsageEventResponse
from app.services.tool_service import ToolService
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[Tool])
async def get_tools(
    skip: int = 0,
    limit: int = 100,
    visible_only: bool = False,
    operational_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """获取工具列表"""
    service = ToolService(db)
    tools = await service.get_tools(
        skip=skip,
        limit=limit,
        visible_only=visible_only,
        operational_only=operational_only
    )
    return tools


@router.get("/{tool_id}", response_model=Tool)
async def get_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个工具"""
    service = ToolService(db)
    tool = await service.get_tool(tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return tool


@router.post("/", response_model=Tool, status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool_in: ToolCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新工具"""
    service = ToolService(db)
    
    # 如果未指定负责人，默认为当前用户
    if tool_in.primary_owner_id is None:
        tool_in.primary_owner_id = current_user.id
    
    # 检查工具名称是否已存在
    existing_tool = await service.get_tool_by_name(tool_in.name)
    if existing_tool:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool name already exists"
        )
    
    tool = await service.create_tool(tool_in)
    return tool


@router.put("/{tool_id}", response_model=Tool)
async def update_tool(
    tool_id: int,
    tool_in: ToolUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新工具"""
    service = ToolService(db)
    tool = await service.update_tool(tool_id, tool_in)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除工具"""
    service = ToolService(db)
    success = await service.delete_tool(tool_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return None


@router.get("/{tool_id}/status", response_model=bool)
async def get_tool_status(
    tool_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取工具状态（是否正在使用）"""
    service = ToolService(db)
    usage = await service.get_current_usage(tool_id)
    return usage is not None


@router.post("/{tool_id}/enable", response_model=UsageEventResponse)
async def enable_tool(
    tool_id: int,
    enable_data: ToolEnable,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """启用工具"""
    service = ToolService(db)
    
    # 如果未指定操作员，默认为当前用户
    operator_id = enable_data.operator_id or current_user.id
    
    try:
        usage_event = await service.enable_tool(tool_id, enable_data, operator_id)
        return usage_event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{tool_id}/disable", response_model=UsageEventResponse)
async def disable_tool(
    tool_id: int,
    disable_data: ToolDisable,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """禁用工具"""
    service = ToolService(db)
    try:
        usage_event = await service.disable_tool(tool_id, disable_data)
        return usage_event
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
