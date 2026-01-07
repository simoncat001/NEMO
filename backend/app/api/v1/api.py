"""
API v1 router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    users, tools, reservations, auth, accounts, usage_events, tasks, staff_charges, configurations, projects, consumables, billing
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(consumables.router, prefix="/consumables", tags=["consumables"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(usage_events.router, prefix="/usage-events", tags=["usage-events"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(staff_charges.router, prefix="/staff-charges", tags=["staff-charges"])
api_router.include_router(configurations.router, prefix="/configurations", tags=["configurations"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])

