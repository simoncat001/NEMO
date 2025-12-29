"""
Reservation model - SQLAlchemy ORM
"""
from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.configuration import ConfigurationOption


class Reservation(Base):
    """预约模型"""
    __tablename__ = "reservation"

    # Allow legacy (pre-SQLAlchemy 2.0) type annotations during migration.
    __allow_unmapped__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 用户和工具
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    tool_id = Column(Integer, ForeignKey("tool.id"), nullable=True, index=True)
    area_id = Column(Integer, ForeignKey("area.id"), nullable=True, index=True)
    
    # 项目
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False, index=True)
    
    # 时间
    start = Column(DateTime(timezone=True), nullable=False, index=True)
    end = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # 状态
    cancelled = Column(Boolean, default=False, nullable=False)
    cancellation_time = Column(DateTime(timezone=True), nullable=True)
    cancelled_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    
    missed = Column(Boolean, default=False, nullable=False)
    
    # 备注
    additional_information = Column(Text, default="")
    self_configuration = Column(Boolean, default=False, nullable=False)
    
    # 缩短标志
    shortened = Column(Boolean, default=False, nullable=False)
    
    # 问题回答（JSON格式）
    question_data = Column(Text, nullable=True)
    
    # 关系 - ConfigurationOption
    configuration_options: List["ConfigurationOption"] = relationship(
        "ConfigurationOption",
        back_populates="reservation",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Reservation(id={self.id}, tool_id={self.tool_id}, user_id={self.user_id})>"
