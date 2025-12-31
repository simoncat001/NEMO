from typing import Optional
from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class ConsumableBase(BaseModel):
    name: str
    category_id: Optional[int] = None
    visible: bool = True
    quantity: int = 0
    reminder_threshold: Optional[int] = None
    reminder_email: Optional[str] = None
    reusable: bool = False
    allow_self_checkout: bool = False
    notes: Optional[str] = None

class ConsumableCreate(ConsumableBase):
    pass

class ConsumableUpdate(ConsumableBase):
    name: Optional[str] = None
    category_id: Optional[int] = None
    visible: Optional[bool] = None
    quantity: Optional[int] = None
    reminder_threshold: Optional[int] = None
    reminder_email: Optional[str] = None
    reusable: Optional[bool] = None
    allow_self_checkout: Optional[bool] = None
    notes: Optional[str] = None

class Consumable(ConsumableBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
