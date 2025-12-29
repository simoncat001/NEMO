"""
Project model - SQLAlchemy ORM  
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.account import Account


class Project(Base):
    """项目模型"""
    __tablename__ = "project"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    application_identifier: Mapped[str] = mapped_column(String(200), unique=True)
    
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # 项目信息
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("account.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # 允许员工收费
    allow_staff_charges: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 关系
    account: Mapped[Optional["Account"]] = relationship("Account", back_populates="projects")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"
