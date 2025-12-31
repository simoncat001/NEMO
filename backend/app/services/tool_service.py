"""
Tool service layer
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tool import Tool
from app.models.usage_event import UsageEvent
from app.schemas.tool import ToolCreate, ToolUpdate, ToolEnable, ToolDisable


class ToolService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_tools(
        self,
        skip: int = 0,
        limit: int = 100,
        visible_only: bool = False,
        operational_only: bool = False
    ) -> List[Tool]:
        """获取工具列表"""
        query = select(Tool)
        
        if visible_only:
            query = query.where(Tool.visible == True)
        if operational_only:
            query = query.where(Tool.operational == True)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_tool(self, tool_id: int) -> Optional[Tool]:
        """获取单个工具"""
        result = await self.db.execute(
            select(Tool).where(Tool.id == tool_id)
        )
        return result.scalar_one_or_none()
    
    async def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """通过名称获取工具"""
        result = await self.db.execute(
            select(Tool).where(Tool.name == name)
        )
        return result.scalar_one_or_none()
    
    async def create_tool(self, tool_in: ToolCreate) -> Tool:
        """创建工具"""
        tool = Tool(
            name=tool_in.name,
            visible=tool_in.visible,
            operational=tool_in.operational,
            description=tool_in.description,
            _location=tool_in.location,
            _phone_number=tool_in.phone_number,
            _primary_owner_id=tool_in.primary_owner_id,
        )
        self.db.add(tool)
        await self.db.commit()
        await self.db.refresh(tool)
        return tool
    
    async def update_tool(self, tool_id: int, tool_in: ToolUpdate) -> Optional[Tool]:
        """更新工具"""
        tool = await self.get_tool(tool_id)
        if not tool:
            return None
        
        update_data = tool_in.model_dump(exclude_unset=True)
        
        # 处理特殊字段映射
        if "location" in update_data:
            tool._location = update_data.pop("location")
        if "phone_number" in update_data:
            tool._phone_number = update_data.pop("phone_number")
        
        for field, value in update_data.items():
            setattr(tool, field, value)
        
        await self.db.commit()
        await self.db.refresh(tool)
        return tool
    
    async def delete_tool(self, tool_id: int) -> bool:
        """删除工具"""
        tool = await self.get_tool(tool_id)
        if not tool:
            return False
        
        await self.db.delete(tool)
        await self.db.commit()
        return True

    async def get_current_usage(self, tool_id: int) -> Optional[UsageEvent]:
        """获取工具当前的使用记录"""
        query = select(UsageEvent).where(
            and_(
                UsageEvent.tool_id == tool_id,
                UsageEvent.end == None
            )
        ).order_by(desc(UsageEvent.start))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def enable_tool(self, tool_id: int, enable_data: ToolEnable, operator_id: int) -> UsageEvent:
        """启用工具"""
        # 1. 检查工具是否存在
        tool = await self.get_tool(tool_id)
        if not tool:
            raise ValueError("Tool not found")

        # 2. 检查工具是否正在使用
        current_usage = await self.get_current_usage(tool_id)
        if current_usage:
            raise ValueError("Tool is already in use")

        # 3. 创建使用记录
        usage_event = UsageEvent(
            tool_id=tool_id,
            user_id=enable_data.user_id,
            project_id=enable_data.project_id,
            operator_id=operator_id,
            start=datetime.utcnow(),
            note=enable_data.note,
            has_ended=0
        )
        
        self.db.add(usage_event)
        await self.db.commit()
        await self.db.refresh(usage_event)
        return usage_event

    async def disable_tool(self, tool_id: int, disable_data: ToolDisable) -> UsageEvent:
        """禁用工具"""
        # 1. 获取当前使用记录
        current_usage = await self.get_current_usage(tool_id)
        if not current_usage:
            raise ValueError("Tool is not in use")

        # 2. 更新结束时间
        current_usage.end = datetime.utcnow()
        
        # 计算 has_ended: max(has_ended) + 1
        query = select(func.max(UsageEvent.has_ended)).where(UsageEvent.tool_id == tool_id)
        result = await self.db.execute(query)
        max_has_ended = result.scalar() or 0
        current_usage.has_ended = max_has_ended + 1
        
        if disable_data.note:
            current_usage.note = disable_data.note
        if disable_data.run_data:
            current_usage.run_data = disable_data.run_data

        await self.db.commit()
        await self.db.refresh(current_usage)
        return current_usage
