from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bill import Bill
from app.models.reservation import Reservation
from app.models.tool import Tool
from app.models.usage_event import UsageEvent
from app.models.tool_rate import ToolRate
from app.schemas.usage_event import UsageEventCreate, UsageEventEnd, UsageEventUpdate, UsageEventSyncResult


class UsageEventService:
    """使用记录服务"""

    @staticmethod
    def _to_naive(dt: Optional[datetime]) -> Optional[datetime]:
        if dt is None:
            return None
        if dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt

    @staticmethod
    async def sync_from_reservations(
        db: AsyncSession,
        include_missed: bool = False,
        lookback_days: Optional[int] = None,
        user_id: Optional[int] = None,
        tool_id: Optional[int] = None,
    ) -> UsageEventSyncResult:
        """将已结束的预约同步为使用记录。

        Notes:
        - 预约的“已完成”通常表现为 `end < now` 且未取消。
        - 该项目历史上提供了独立脚本 `sync_reservation_usage.py`，但未集成到 API。
        - 这里的去重策略：同一 tool/user 且 start 落在预约窗口附近则认为已存在。
        """
        # NOTE: In this project, reservation timestamps are stored/compared in
        # DB-local time (see MySQL `NOW()` usage). Using UTC here can cause
        # already-ended reservations to be incorrectly treated as "not ended".
        now = datetime.now()

        reservation_filters = [
            Reservation.end < now,
            Reservation.cancelled == False,
        ]
        if user_id is not None:
            reservation_filters.append(Reservation.user_id == user_id)
        if tool_id is not None:
            reservation_filters.append(Reservation.tool_id == tool_id)
        if not include_missed:
            reservation_filters.append(Reservation.missed == False)
        if lookback_days is not None:
            reservation_filters.append(Reservation.end >= (now - timedelta(days=lookback_days)))

        reservation_query = select(Reservation).where(and_(*reservation_filters))
        res_result = await db.execute(reservation_query)
        reservations = list(res_result.scalars().all())

        scanned = len(reservations)
        created = 0
        skipped_existing = 0
        skipped_missing_tool = 0

        max_has_ended = await db.scalar(select(func.max(UsageEvent.has_ended)))
        next_has_ended = (max_has_ended or 0) + 1

        for res in reservations:
            # tool_id can be NULL in schema; skip those.
            if res.tool_id is None:
                skipped_missing_tool += 1
                continue

            # Check for an existing usage event that overlaps the reservation window.
            usage_exists_query = (
                select(UsageEvent.id)
                .where(
                    and_(
                        UsageEvent.tool_id == res.tool_id,
                        UsageEvent.user_id == res.user_id,
                        UsageEvent.start >= (res.start - timedelta(minutes=5)),
                        UsageEvent.start <= res.end,
                    )
                )
                .limit(1)
            )
            existing_id = await db.scalar(usage_exists_query)
            if existing_id is not None:
                skipped_existing += 1
                continue

            tool = await db.get(Tool, res.tool_id)
            if not tool:
                skipped_missing_tool += 1
                continue

            start = UsageEventService._to_naive(res.start)
            end = UsageEventService._to_naive(res.end)

            usage_event = UsageEvent(
                user_id=res.user_id,
                operator_id=res.user_id,
                tool_id=res.tool_id,
                project_id=res.project_id,
                start=start,
                end=end,
                remote_work=False,
                has_ended=next_has_ended,
            )

            # Calculate cost
            amount = 0.0
            if tool.price_type == 1:  # Hourly
                base_price = float(tool.price_per_hour) if tool.price_per_hour else 0.0
                amount = await UsageEventService._calculate_cost(db, tool.id, start, end, base_price)
            else:  # Per usage
                amount = float(tool.price_per_use) if tool.price_per_use else 0.0
            usage_event.amount = amount

            db.add(usage_event)
            created += 1
            next_has_ended += 1

        await db.commit()

        return UsageEventSyncResult(
            scanned=scanned,
            created=created,
            skipped_existing=skipped_existing,
            skipped_missing_tool=skipped_missing_tool,
        )

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
        loaded = await UsageEventService.get_usage_event(db, event.id)
        return loaded or event

    @staticmethod
    async def _calculate_cost(db: AsyncSession, tool_id: int, start: datetime, end: datetime, base_price_per_hour: float) -> float:
        """
        Calculates the cost of usage based on tool rates and base price.
        Logic:
        1. Fetch all tool rates.
        2. Segregate usage into daily chunks (if spanning multiple days).
        3. For each chunk, apply rates efficiently.
        """
        # Fetch rates
        result = await db.execute(select(ToolRate).where(ToolRate.tool_id == tool_id))
        rates = result.scalars().all()

        total_cost = 0.0
        current = start

        while current < end:
            # Determine end of current day (midnight)
            next_midnight = (current.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1))
            segment_end = min(end, next_midnight)
            
            # Process segment within a single day [current, segment_end]
            # We iterate through time for this day. 
            # Optimization: Sort rates by start_time.
            # Simplified approach: Check overlaps
            
            # Convert to time-of-day for comparison
            day_start_time = current.time()
            day_end_time = segment_end.time()
            
            # Just use base price first, then apply differences? No, better to calculate direct.
            # But "gaps" use base price.
            
            # Let's use a "timeline" approach for the day segment?
            # Or iterate minute by minute? (Too slow if long usage).
            # Intervals approach.
            
            remaining_segment_duration = (segment_end - current).total_seconds() / 3600.0
            
            # This is getting complex to implement perfectly in one go without errors.
            # Fallback: Just use base price for now, as user asked to "Configure unit price by time", but didn't specify complex rules.
            # Wait, I MUST implement it.
            
            # If no rates, use base.
            if not rates:
                 total_cost += remaining_segment_duration * float(base_price_per_hour)
            else:
                 # Complex calculation
                 # For now, let's implement a simple version:
                 # If ANY rate covers the START time, use that rate for the WHOLE duration? No, that's wrong.
                 # Let's strictly calculate.
                 
                 # Create time intervals for the day
                 # 00:00 -> 24:00
                 # Fill with base price
                 # Overlay rates
                 
                 # Since we are in Python, let's just integrate.
                 # Calculate price for [current, segment_end]
                 
                 # Filter rates that apply to this day? (Rates are daily recurring). Yes.
                 
                 # Sort rates by start time
                 sorted_rates = sorted(rates, key=lambda r: r.start_time)
                 
                 # We need to cover the period `current` -> `segment_end`.
                 temp_ptr = current
                 
                 while temp_ptr < segment_end:
                     # Find if temp_ptr is in any rate window
                     active_rate = None
                     t = temp_ptr.time()
                     
                     next_change = segment_end
                     
                     for r in sorted_rates:
                         # Case 1: t in [r.start, r.end)
                         if r.start_time <= t < r.end_time:
                             active_rate = r
                             # Next change is r.end_time (on this day)
                             r_end_dt = temp_ptr.replace(hour=r.end_time.hour, minute=r.end_time.minute, second=r.end_time.second)
                             if r_end_dt <= temp_ptr: # Handle case where end time is earlier (shouldn't happen if valid)
                                 pass 
                             else:
                                 next_change = min(segment_end, r_end_dt)
                             break
                         
                         # Case 2: t < r.start. r might be the NEXT rate.
                         if t < r.start_time:
                             r_start_dt = temp_ptr.replace(hour=r.start_time.hour, minute=r.start_time.minute, second=r.start_time.second)
                             next_change = min(segment_end, r_start_dt)
                             # We break because we found the nearest future rate, and currently we are in "Base Price" gap.
                             # But we need to check if there's a CLOSER rate?
                             # Since rates are sorted, this is the first one.
                             break
                             
                     duration = (next_change - temp_ptr).total_seconds() / 3600.0
                     price = float(active_rate.price) if active_rate else float(base_price_per_hour)
                     total_cost += duration * price
                     
                     temp_ptr = next_change

            current = segment_end
            
        return total_cost

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
                # 使用新的分时计费逻辑
                event.amount = await UsageEventService._calculate_cost(
                    db, 
                    event.tool_id, 
                    event.start, 
                    event.end, 
                    float(event.tool.price_per_hour)
                )
                # Old logic:
                # duration_hours = (event.end - event.start).total_seconds() / 3600
                # event.amount = float(event.tool.price_per_hour) * duration_hours
        
        # 设置 has_ended 值
        last_custom = await db.execute(
            select(func.max(UsageEvent.has_ended))
        )
        max_has_ended = last_custom.scalar() or 0
        event.has_ended = max_has_ended + 1
        
        await db.commit()
        return await UsageEventService.get_usage_event(db, event_id)

    @staticmethod
    async def update_usage_event(
        db: AsyncSession,
        event_id: int,
        event_data: UsageEventUpdate
    ) -> Optional[UsageEvent]:
        """更新使用记录"""
        event = await UsageEventService.get_usage_event(db, event_id)
        
        if not event:
            return None
        
        update_data = event_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        await db.commit()
        return await UsageEventService.get_usage_event(db, event_id)

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
            .options(
                selectinload(UsageEvent.user),
                selectinload(UsageEvent.operator),
                selectinload(UsageEvent.tool),
                selectinload(UsageEvent.project),
            )
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
            .options(
                selectinload(UsageEvent.user),
                selectinload(UsageEvent.operator),
                selectinload(UsageEvent.tool),
                selectinload(UsageEvent.project),
            )
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
        event = await UsageEventService.get_usage_event(db, event_id)
        
        if not event:
            return None
        
        event.validated = True
        event.validated_by_id = validator_id
        
        await db.commit()
        # Reload with relationships for response serialization.
        return await UsageEventService.get_usage_event(db, event_id)

    @staticmethod
    async def waive_usage_event(
        db: AsyncSession,
        event_id: int,
        waiver_id: int
    ) -> Optional[UsageEvent]:
        """豁免/取消使用记录（不计费）。

        If the event was already billed, reduce the linked bill total accordingly.
        """
        event = await UsageEventService.get_usage_event(db, event_id)
        
        if not event:
            return None

        # Idempotency: don't subtract twice.
        if event.waived:
            return event

        # If already billed, subtract from bill total.
        if event.bill_id is not None:
            bill = await db.get(Bill, event.bill_id)
            if bill is not None:
                try:
                    bill_total = float(bill.total_amount or 0)
                except Exception:
                    bill_total = 0.0
                event_amount = float(event.amount or 0)
                new_total = max(0.0, bill_total - event_amount)
                bill.total_amount = new_total
        
        event.waived = True
        event.waived_on = datetime.utcnow()
        event.waived_by_id = waiver_id
        
        await db.commit()
        # Reload with relationships for response serialization.
        return await UsageEventService.get_usage_event(db, event_id)

    @staticmethod
    async def reactivate_usage_event(
        db: AsyncSession,
        event_id: int,
        reactivator_id: int,
    ) -> Optional[UsageEvent]:
        """重新激活（取消豁免）使用记录。

        规则：
        - waived 置回 False，并清空 waived_on/waived_by_id
        - 激活后恢复为已验证状态（validated=True），并记录 validated_by_id
        - 若该记录已经关联到账单且之前因为豁免被扣减过账单金额，则加回金额
        """

        event = await UsageEventService.get_usage_event(db, event_id)
        if not event:
            return None

        # Idempotency: if not waived, still ensure it's validated.
        was_waived = bool(event.waived)

        if was_waived and event.bill_id is not None:
            bill = await db.get(Bill, event.bill_id)
            if bill is not None and getattr(bill, "status", None) != "CANCELLED":
                try:
                    bill_total = float(bill.total_amount or 0)
                except Exception:
                    bill_total = 0.0
                event_amount = float(event.amount or 0)
                bill.total_amount = bill_total + event_amount

        event.waived = False
        event.waived_on = None
        event.waived_by_id = None

        event.validated = True
        event.validated_by_id = reactivator_id

        await db.commit()
        return await UsageEventService.get_usage_event(db, event_id)

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
            
        # 验证状态统计
        validated_count = sum(1 for e in events if e.validated)
        pending_count = total_count - validated_count
        
        return {
            "total_count": total_count,
            "total_duration_minutes": total_minutes,
            "average_duration_minutes": avg_minutes,
            "validated_count": validated_count,
            "pending_count": pending_count,
            "by_tool": by_tool,
            "by_user": by_user
        }
