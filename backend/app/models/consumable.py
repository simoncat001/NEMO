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
    category_id = Column(Integer, nullable=True)
    visible = Column(Boolean, default=True, nullable=False)
    quantity = Column(Integer, default=0)
    reminder_threshold = Column(Integer, nullable=True)
    reminder_email = Column(String, nullable=True)
    reminder_threshold_reached = Column(Boolean, default=False)
    reusable = Column(Boolean, default=False)
    allow_self_checkout = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Consumable(id={self.id}, name='{self.name}')>"
