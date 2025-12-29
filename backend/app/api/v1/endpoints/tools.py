"""
Tool API endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.tool import Tool, ToolCreate, ToolUpdate
from app.services.tool_service import ToolService

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
    db: AsyncSession = Depends(get_db)
):
    """创建新工具"""
    service = ToolService(db)
    
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
