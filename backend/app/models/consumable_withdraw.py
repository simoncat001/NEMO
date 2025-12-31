"""
Consumable Withdraw model - SQLAlchemy ORM
"""
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from app.db.session import Base

class ConsumableWithdraw(Base):
    """耗材领用记录"""
    __tablename__ = "consumable_withdraw"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    consumable_id = Column(Integer, ForeignKey("consumable.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False, index=True)
    
    quantity = Column(Integer, default=1, nullable=False, comment="数量")
    amount = Column(Numeric(10, 2), default=0.00, nullable=False, comment="总金额")
    date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    consumable = relationship("Consumable", foreign_keys=[consumable_id])
    project = relationship("Project", foreign_keys=[project_id])

    def __repr__(self):
        return f"<ConsumableWithdraw(id={self.id}, user={self.user_id}, consumable={self.consumable_id}, amount={self.amount})>"
