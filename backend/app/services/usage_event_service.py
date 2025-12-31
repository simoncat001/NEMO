from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.usage_event import UsageEvent
from app.schemas.usage_event import UsageEventCreate, UsageEventEnd, UsageEventUpdate


class UsageEventService:
    """使用记录服务"""

    @staticmethod
    async def get_usage_events(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        tool_id: Optional[int] = None,
        project_id: Optional[int] = None,
        in_progress_only: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[UsageEvent]:
        """获取使用记录列表"""
        query = select(UsageEvent).options(
            selectinload(UsageEvent.user),
            selectinload(UsageEvent.operator),
            selectinload(UsageEvent.tool),
            selectinload(UsageEvent.project)
        )
        
        # 应用过滤条件
        filters = []
        if user_id:
            filters.append(UsageEvent.user_id == user_id)
        if tool_id:
            filters.append(UsageEvent.tool_id == tool_id)
        if project_id:
            filters.append(UsageEvent.project_id == project_id)
        if in_progress_only:
            filters.append(UsageEvent.end == None)
        if start_date:
            filters.append(UsageEvent.start >= start_date)
        if end_date:
            filters.append(UsageEvent.start <= end_date)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(UsageEvent.start.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_usage_event(db: AsyncSession, event_id: int) -> Optional[UsageEvent]:
        """获取单个使用记录"""
        result = await db.execute(
            select(UsageEvent)
            .options(
                selectinload(UsageEvent.user),
                selectinload(UsageEvent.operator),
                selectinload(UsageEvent.tool),
                selectinload(UsageEvent.project),
                selectinload(UsageEvent.validated_by),
                selectinload(UsageEvent.waived_by)
            )
            .where(UsageEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_usage_event(
        db: AsyncSession,
        event_data: UsageEventCreate,
        creator_id: int
    ) -> UsageEvent:
        """创建使用记录（开始使用工具）"""
        event_dict = event_data.model_dump()
        
        # 设置开始时间
        if not event_dict.get("start"):
            event_dict["start"] = datetime.utcnow()
        
        event = UsageEvent(**event_dict)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def end_usage_event(
        db: AsyncSession,
        event_id: int,
        end_data: UsageEventEnd
    ) -> Optional[UsageEvent]:
        """结束使用记录"""
        result = await db.execute(
            select(UsageEvent)
            .options(selectinload(UsageEvent.tool))
            .where(UsageEvent.id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            return None
        
        if event.end is not None:
            raise ValueError("Usage event has already ended")
        
        event.end = datetime.utcnow()
        if end_data.run_data:
            event.run_data = end_data.run_data
        
        # 计算费用
        if event.tool:
            if event.tool.price_type == 0:  # 按次收费
                event.amount = float(event.tool.price_per_use)
            elif event.tool.price_type == 1:  # 按时收费
                duration_hours = (event.end - event.start).total_seconds() / 3600
                # 向上取整到0.5小时或1小时？这里暂时按实际时间计算
                event.amount = float(event.tool.price_per_hour) * duration_hours
        
        # 设置 has_ended 值
        last_custom = await db.execute(
            select(func.max(UsageEvent.has_ended))
        )
        max_has_ended = last_custom.scalar() or 0
        event.has_ended = max_has_ended + 1
        
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def update_usage_event(
        db: AsyncSession,
        event_id: int,
        event_data: UsageEventUpdate
    ) -> Optional[UsageEvent]:
        """更新使用记录"""
        result = await db.execute(
            select(UsageEvent).where(UsageEvent.id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            return None
        
        update_data = event_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def delete_usage_event(db: AsyncSession, event_id: int) -> bool:
        """删除使用记录"""
        result = await db.execute(
            select(UsageEvent).where(UsageEvent.id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            return False
        
        await db.delete(event)
        await db.commit()
        return True

    @staticmethod
    async def get_active_usage_for_tool(
        db: AsyncSession,
        tool_id: int
    ) -> Optional[UsageEvent]:
        """获取工具当前的使用记录"""
        result = await db.execute(
            select(UsageEvent)
            .where(
                and_(
                    UsageEvent.tool_id == tool_id,
                    UsageEvent.end == None
                )
            )
            .order_by(UsageEvent.start.desc())
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_usage_for_user(
        db: AsyncSession,
        user_id: int
    ) -> List[UsageEvent]:
        """获取用户当前的所有使用记录"""
        result = await db.execute(
            select(UsageEvent)
            .options(selectinload(UsageEvent.tool))
            .where(
                and_(
                    UsageEvent.user_id == user_id,
                    UsageEvent.end == None
                )
            )
            .order_by(UsageEvent.start.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def validate_usage_event(
        db: AsyncSession,
        event_id: int,
        validator_id: int
    ) -> Optional[UsageEvent]:
        """验证使用记录"""
        result = await db.execute(
            select(UsageEvent).where(UsageEvent.id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            return None
        
        event.validated = True
        event.validated_by_id = validator_id
        
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def waive_usage_event(
        db: AsyncSession,
        event_id: int,
        waiver_id: int
    ) -> Optional[UsageEvent]:
        """豁免使用记录（不计费）"""
        result = await db.execute(
            select(UsageEvent).where(UsageEvent.id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if not event:
            return None
        
        event.waived = True
        event.waived_on = datetime.utcnow()
        event.waived_by_id = waiver_id
        
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def get_usage_stats(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tool_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> dict:
        """获取使用统计"""
        filters = []
        if start_date:
            filters.append(UsageEvent.start >= start_date)
        if end_date:
            filters.append(UsageEvent.start <= end_date)
        if tool_id:
            filters.append(UsageEvent.tool_id == tool_id)
        if user_id:
            filters.append(UsageEvent.user_id == user_id)
        
        # 只统计已结束的记录
        filters.append(UsageEvent.end != None)
        
        query = select(UsageEvent)
        if filters:
            query = query.where(and_(*filters))
        
        result = await db.execute(query)
        events = result.scalars().all()
        
        total_count = len(events)
        total_minutes = sum(e.duration_minutes() or 0 for e in events)
        avg_minutes = total_minutes / total_count if total_count > 0 else 0
        
        # 按工具统计
        by_tool = {}
        for event in events:
            by_tool[event.tool_id] = by_tool.get(event.tool_id, 0) + 1
        
        # 按用户统计
        by_user = {}
        for event in events:
            by_user[event.user_id] = by_user.get(event.user_id, 0) + 1
        
        return {
            "total_count": total_count,
            "total_duration_minutes": total_minutes,
            "average_duration_minutes": avg_minutes,
            "by_tool": by_tool,
            "by_user": by_user
        }
