from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.usage_event import (
    UsageEventCreate,
    UsageEventDetail,
    UsageEventEnd,
    UsageEventResponse,
    UsageEventSyncResult,
    UsageEventStats,
    UsageEventUpdate,
)
from app.services.usage_event_service import UsageEventService

router = APIRouter()


@router.get("/", response_model=List[UsageEventResponse])
async def get_usage_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None),
    tool_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    in_progress_only: bool = Query(False),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取使用记录列表"""
    # Determine effective user scope
    effective_user_id: Optional[int] = user_id
    if not current_user.is_staff and not current_user.is_superuser:
        effective_user_id = current_user.id

    # Auto-sync: ensure completed reservations are reflected in usage events.
    # Keep sync bounded so listing usage events stays responsive.
    lookback_days: Optional[int] = None
    if start_date is not None:
        delta_days = (datetime.now() - start_date.replace(tzinfo=None)).days
        lookback_days = max(1, min(3650, delta_days + 1))
    elif end_date is not None:
        delta_days = (datetime.now() - end_date.replace(tzinfo=None)).days
        lookback_days = max(1, min(3650, delta_days + 1))
    else:
        lookback_days = 30

    # For non-staff users we sync only their own reservations.
    await UsageEventService.sync_from_reservations(
        db,
        include_missed=False,
        lookback_days=lookback_days,
        user_id=effective_user_id,
        tool_id=tool_id,
    )

    return await UsageEventService.get_usage_events(
        db, skip, limit, effective_user_id, tool_id, project_id,
        in_progress_only, start_date, end_date
    )


@router.post("/", response_model=UsageEventResponse, status_code=status.HTTP_201_CREATED)
async def create_usage_event(
    event: UsageEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建使用记录（开始使用工具）"""
    # 普通用户只能为自己开启
    if not current_user.is_staff and not current_user.is_superuser:
        event.user_id = current_user.id
        event.operator_id = current_user.id

    # 检查工具是否已被占用
    active_usage = await UsageEventService.get_active_usage_for_tool(db, event.tool_id)
    if active_usage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool is currently in use by user {active_usage.user_id}"
        )
    
    return await UsageEventService.create_usage_event(db, event, current_user.id)


@router.get("/stats", response_model=UsageEventStats)
async def get_usage_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    tool_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取使用统计"""
    # 普通用户只能查看自己的统计
    if not current_user.is_staff and not current_user.is_superuser:
        user_id = current_user.id
    
    return await UsageEventService.get_usage_stats(
        db, start_date, end_date, tool_id, user_id
    )


@router.post("/sync-from-reservations", response_model=UsageEventSyncResult)
async def sync_usage_from_reservations(
    include_missed: bool = Query(False, description="是否包含 missed 的预约"),
    lookback_days: Optional[int] = Query(None, ge=1, le=3650, description="只同步最近 N 天内结束的预约"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """将已完成的预约同步到使用记录（需要 staff 权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can sync usage events from reservations",
        )

    return await UsageEventService.sync_from_reservations(
        db,
        include_missed=include_missed,
        lookback_days=lookback_days,
    )


@router.get("/{event_id}", response_model=UsageEventDetail)
async def get_usage_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取使用记录详情"""
    event = await UsageEventService.get_usage_event(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage event not found"
        )
    
    # 添加计算属性
    response = UsageEventDetail.model_validate(event)
    response.duration_minutes = event.duration_minutes()
    response.is_in_progress = event.is_in_progress
    response.self_usage = event.self_usage()
    
    return response


@router.post("/{event_id}/end", response_model=UsageEventResponse)
async def end_usage_event(
    event_id: int,
    end_data: UsageEventEnd = Body(default_factory=UsageEventEnd),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """结束使用记录"""
    event = await UsageEventService.get_usage_event(db, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage event not found"
        )
    
    # 只有操作员或管理员可以结束使用
    if event.operator_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the operator or staff can end this usage"
        )
    
    try:
        return await UsageEventService.end_usage_event(db, event_id, end_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{event_id}", response_model=UsageEventResponse)
async def update_usage_event(
    event_id: int,
    event: UsageEventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新使用记录（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update usage events"
        )
    
    updated = await UsageEventService.update_usage_event(db, event_id, event)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage event not found"
        )
    return updated


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usage_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除使用记录（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can delete usage events"
        )
    
    deleted = await UsageEventService.delete_usage_event(db, event_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage event not found"
        )


@router.get("/tool/{tool_id}/active", response_model=UsageEventResponse)
async def get_active_usage_for_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取工具当前的使用记录"""
    event = await UsageEventService.get_active_usage_for_tool(db, tool_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active usage for this tool"
        )
    return event


@router.get("/user/{user_id}/active", response_model=List[UsageEventResponse])
async def get_active_usage_for_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取用户当前的所有使用记录"""
    # 只能查看自己的或管理员可以查看所有
    if user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own active usage"
        )
    
    return await UsageEventService.get_active_usage_for_user(db, user_id)


@router.post("/{event_id}/validate", response_model=UsageEventResponse)
async def validate_usage_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """验证使用记录（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can validate usage events"
        )
    
    event = await UsageEventService.validate_usage_event(db, event_id, current_user.id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage event not found"
        )
    return event


@router.post("/{event_id}/waive", response_model=UsageEventResponse)
async def waive_usage_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """豁免使用记录（不计费，需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can waive usage events"
        )
    
    event = await UsageEventService.waive_usage_event(db, event_id, current_user.id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usage event not found"
        )
    return event
