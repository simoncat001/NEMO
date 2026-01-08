from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DashboardStats(BaseModel):
    total_tools: int
    today_reservations: int
    active_tasks: int
    active_users: int


class DashboardRecentReservation(BaseModel):
    tool_name: Optional[str] = None
    start: datetime
    end: datetime


class DashboardPendingTask(BaseModel):
    tool_name: Optional[str] = None
    problem_description: Optional[str] = None
    urgency: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_reservations: List[DashboardRecentReservation]
    pending_tasks: List[DashboardPendingTask]

    model_config = ConfigDict(from_attributes=True)
