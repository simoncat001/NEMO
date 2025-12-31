"""
Tool model - SQLAlchemy ORM
"""
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.configuration import Configuration


class Tool(Base):
    """工具模型"""
    __tablename__ = "tool"

    # Allow legacy (pre-SQLAlchemy 2.0) type annotations during migration.
    __allow_unmapped__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    visible = Column(Boolean, default=True, nullable=False)
    operational = Column(Boolean, default=False, nullable=False)
    
    _primary_owner_id = Column("primary_owner_id", Integer, ForeignKey("user.id"))
    _location = Column("location", String(100), nullable=True)
    _phone_number = Column("phone_number", String(40), nullable=True)
    
    # 预留和使用设置
    _requires_area_access_id = Column("requires_area_access_id", Integer, nullable=True)
    grant_physical_access_level_upon_qualification_id = Column(Integer, nullable=True)
    grant_badge_reader_access_upon_qualification = Column(String(100), nullable=True)
    
    # 工具配置
    reservation_horizon = Column(Integer, default=14, nullable=True)
    minimum_usage_block_time = Column(Integer, nullable=True)
    maximum_usage_block_time = Column(Integer, nullable=True)
    maximum_reservations_per_day = Column(Integer, nullable=True)
    minimum_time_between_reservations = Column(Integer, nullable=True)
    maximum_future_reservation_time = Column(Integer, nullable=True)
    missed_reservation_threshold = Column(Integer, nullable=True)
    
    # 工具描述
    description = Column(Text, default="")
    serial = Column(String(100), nullable=True)
    
    # 策略设置
    policy_off_between_times = Column(Boolean, default=False, nullable=False)
    policy_off_weekend = Column(Boolean, default=False, nullable=False)
    image = Column(String(200), default="", nullable=False)
    tool_calendar_color = Column(String(50), default="#3788d8", nullable=False)
    qualifications_never_expire = Column(Boolean, default=False, nullable=False)
    ask_to_leave_area_when_done_using = Column(Boolean, default=False, nullable=False)
    _operation_mode = Column("_operation_mode", Integer, default=0, nullable=False)
    abuse_weight = Column(Integer, default=1, nullable=False)
    problem_shutdown_enabled = Column(Boolean, default=False, nullable=False)
    
    # 互锁信息
    interlock_id = Column(Integer, nullable=True)
    
    # 收费配置
    # 0: 按次收费 (Per Use), 1: 按时收费 (Per Hour/Time)
    price_type = Column(Integer, default=1, nullable=False, comment="收费类型: 0=按次, 1=按时")
    price_per_use = Column(Numeric(10, 2), default=0.00, nullable=False, comment="每次使用价格")
    price_per_hour = Column(Numeric(10, 2), default=0.00, nullable=False, comment="每小时价格")

    # 分类
    _category_id = Column("category", Integer, ForeignKey("task_category.id"), nullable=True)
    
    # 关系 - Configuration
    configurations: List["Configuration"] = relationship(
        "Configuration",
        back_populates="tool",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Tool(id={self.id}, name='{self.name}')>"


"""NOTE:

This backend maps task categories in `app.models.task.TaskCategory`.
An older `ToolCategory` model previously mapped to the same underlying table
(`task_category`), which causes SQLAlchemy to raise:

    InvalidRequestError: Table 'task_category' is already defined

To keep the preview environment working, we intentionally do not map `ToolCategory`
as a separate ORM class.
"""
