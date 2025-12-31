from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/", response_model=List[Project])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    active: Optional[bool] = None,
    account_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目列表"""
    service = ProjectService(db)
    return await service.get_projects(
        skip=skip, limit=limit, active=active, account_id=account_id
    )


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目详情"""
    service = ProjectService(db)
    project = await service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=Project)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建项目"""
    service = ProjectService(db)
    return await service.create_project(project_in)


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新项目"""
    service = ProjectService(db)
    project = await service.update_project(project_id, project_in)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除项目"""
    service = ProjectService(db)
    success = await service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"ok": True}
