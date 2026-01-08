from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.bill import Bill
    from app.models.user import User


class AccountType(Base):
    """账户类型分类"""
    __tablename__ = "account_type"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    display_order: Mapped[int] = mapped_column(default=0)

    # 关系
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="type")

    def __repr__(self):
        return f"<AccountType(id={self.id}, name='{self.name}')>"


class Account(Base):
    """账户模型 - 用于项目资金管理"""
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    # One account per user (treat user as account)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=True,
        index=True,
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 外键
    type_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("account_type.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # 字段
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # 关系
    type: Mapped[Optional["AccountType"]] = relationship("AccountType", back_populates="accounts")
    user: Mapped[Optional["User"]] = relationship("User")
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="account")
    bills: Mapped[List["Bill"]] = relationship("Bill", back_populates="account")

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', active={self.active})>"

    def display_with_status(self) -> str:
        """显示带状态的账户名称"""
        prefix = "[INACTIVE] " if not self.active else ""
        return f"{prefix}{self.name}"
