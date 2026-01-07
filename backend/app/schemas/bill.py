from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal

# Shared properties
class BillBase(BaseModel):
    period_start: datetime
    period_end: datetime
    due_date: Optional[datetime] = None
    status: Optional[str] = "DRAFT"

# Properties to receive on creation
class BillCreate(BillBase):
    account_id: int
    force_regenerate: bool = False # If true, cancels existing bills for period

# Properties to return to client
class BillResponse(BillBase):
    id: int
    account_id: int
    reference_number: str
    issued_date: datetime
    total_amount: Decimal
    
    class Config:
        from_attributes = True

class BillDetail(BillResponse):
    # Potential lines could happen here
    pass

class BillGenerationRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    account_ids: Optional[List[int]] = None # If None, all accounts
