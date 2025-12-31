"""
Consumable model - SQLAlchemy ORM
"""
from sqlalchemy import Column, Integer, String, Boolean, Numeric
from app.db.session import Base

class Consumable(Base):
    """耗材模型"""
    __tablename__ = "consumable"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=True)
    visible = Column(Boolean, default=True, nullable=False)
    
    # 价格信息
    price = Column(Numeric(10, 2), default=0.00, nullable=False, comment="单价")
    
    def __repr__(self):
        return f"<Consumable(id={self.id}, name='{self.name}', price={self.price})>"
