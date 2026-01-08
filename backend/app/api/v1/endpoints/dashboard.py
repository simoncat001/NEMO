from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.reservation import Reservation
from app.models.task import Task
from app.models.tool import Tool
from app.models.user import User
from app.schemas.dashboard import (
    DashboardPendingTask,
    DashboardRecentReservation,
    DashboardResponse,
    DashboardStats,
)

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """仪表盘数据。

    Notes:
    - 普通用户只统计自己的预约/任务；管理员统计全局。
    - 时间使用本地 naive datetime，与项目其他逻辑一致。
    """

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)

    # Tools
    tool_filters = []
    if not current_user.is_staff and not current_user.is_superuser:
        tool_filters.append(Tool.visible == True)
    tool_count_stmt = select(func.count()).select_from(Tool)
    if tool_filters:
        tool_count_stmt = tool_count_stmt.where(*tool_filters)
    total_tools = await db.scalar(tool_count_stmt)

    # Reservations today
    reservation_filters = [
        Reservation.cancelled == False,
        Reservation.start >= today_start,
        Reservation.start < tomorrow_start,
    ]
    if not current_user.is_staff and not current_user.is_superuser:
        reservation_filters.append(Reservation.user_id == current_user.id)
    today_reservations = await db.scalar(
        select(func.count()).select_from(Reservation).where(*reservation_filters)
    )

    # Active (open) tasks
    task_filters = [Task.cancelled == False, Task.resolved == False]
    if not current_user.is_staff and not current_user.is_superuser:
        task_filters.append(Task.creator_id == current_user.id)
    active_tasks = await db.scalar(select(func.count()).select_from(Task).where(*task_filters))

    # Active users
    active_users = await db.scalar(select(func.count()).select_from(User).where(User.is_active == True))

    # Recent reservations
    recent_q = (
        select(Reservation)
        .options(selectinload(Reservation.tool))
        .where(Reservation.cancelled == False)
        .order_by(Reservation.start.desc())
        .limit(5)
    )
    if not current_user.is_staff and not current_user.is_superuser:
        recent_q = recent_q.where(Reservation.user_id == current_user.id)

    recent_reservations = (await db.execute(recent_q)).scalars().all()
    recent_rows: List[DashboardRecentReservation] = [
        DashboardRecentReservation(
            tool_name=(r.tool.name if getattr(r, "tool", None) else None),
            start=r.start.replace(tzinfo=None) if r.start.tzinfo else r.start,
            end=r.end.replace(tzinfo=None) if r.end.tzinfo else r.end,
        )
        for r in recent_reservations
    ]

    # Pending tasks
    pending_q = (
        select(Task)
        .options(selectinload(Task.tool))
        .where(Task.cancelled == False, Task.resolved == False)
        .order_by(Task.creation_time.desc())
        .limit(5)
    )
    if not current_user.is_staff and not current_user.is_superuser:
        pending_q = pending_q.where(Task.creator_id == current_user.id)

    pending_tasks = (await db.execute(pending_q)).scalars().all()
    pending_rows: List[DashboardPendingTask] = [
        DashboardPendingTask(
            tool_name=(t.tool.name if getattr(t, "tool", None) else None),
            problem_description=t.problem_description,
            urgency=int(t.urgency),
        )
        for t in pending_tasks
    ]

    return DashboardResponse(
        stats=DashboardStats(
            total_tools=int(total_tools or 0),
            today_reservations=int(today_reservations or 0),
            active_tasks=int(active_tasks or 0),
            active_users=int(active_users or 0),
        ),
        recent_reservations=recent_rows,
        pending_tasks=pending_rows,
    )
