from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_projects(
        self,
        skip: int = 0,
        limit: int = 100,
        active: Optional[bool] = None,
        account_id: Optional[int] = None,
    ) -> List[Project]:
        query = select(Project)
        if active is not None:
            query = query.where(Project.active == active)
        if account_id is not None:
            query = query.where(Project.account_id == account_id)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_project(self, project_id: int) -> Optional[Project]:
        result = await self.db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def create_project(self, project_in: ProjectCreate) -> Project:
        project = Project(**project_in.model_dump())
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def update_project(
        self, project_id: int, project_in: ProjectUpdate
    ) -> Optional[Project]:
        project = await self.get_project(project_id)
        if not project:
            return None
        
        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
            
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete_project(self, project_id: int) -> bool:
        project = await self.get_project(project_id)
        if not project:
            return False
            
        await self.db.delete(project)
        await self.db.commit()
        return True
