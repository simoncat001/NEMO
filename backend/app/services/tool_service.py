"""
Tool service layer
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tool import Tool
from app.schemas.tool import ToolCreate, ToolUpdate


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
