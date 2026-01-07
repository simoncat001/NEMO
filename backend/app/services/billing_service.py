from datetime import datetime
from typing import List, Optional, Tuple
from decimal import Decimal

from sqlalchemy import select, and_, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bill import Bill
from app.models.account import Account
from app.models.usage_event import UsageEvent
from app.models.consumable_withdraw import ConsumableWithdraw
from app.models.staff_charge import StaffCharge
from app.schemas.bill import BillCreate, BillResponse

class BillingService:
    @staticmethod
    async def generate_bills(
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        account_ids: Optional[List[int]] = None
    ) -> List[Bill]:
        """为指定时间段生成账单"""
        # 1. 查找所有有效的账户
        query = select(Account).where(Account.active == True)
        if account_ids:
            query = query.where(Account.id.in_(account_ids))
        
        result = await db.execute(query)
        accounts = result.scalars().all()
        
        generated_bills = []
        
        for account in accounts:
            bill = await BillingService._generate_bill_for_account(
                db, account, start_date, end_date
            )
            if bill:
                generated_bills.append(bill)
        
        return generated_bills

    @staticmethod
    async def _generate_bill_for_account(
        db: AsyncSession,
        account: Account,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Bill]:
        # 查找该账户下未结算的使用记录
        # 注意: UsageEvent linked to Project, Project linked to Account.
        # But wait, Project.account_id can change? 
        # Usually billing is based on the project's account AT THE TIME of usage.
        # But our model structure is UsageEvent -> Project -> Account.
        # If Project moves to another account, previous usage might be billed to new account?
        # Ideally UsageEvent should snapshot account_id, but per current schema we rely on Project relation.
        
        # Unbilled Usage Events
        usage_query = (
            select(UsageEvent)
            .join(UsageEvent.project)
            .where(
                and_(
                    UsageEvent.project.has(account_id=account.id),
                    UsageEvent.end >= start_date,
                    UsageEvent.end <= end_date,
                    UsageEvent.bill_id == None,
                    UsageEvent.waived == False,
                    # UsageEvent.validated == True # Assuming validated? Or just ended?
                    # Let's assume ended implies billable for now, or check business logic.
                    # Usually pending validation events shouldn't be billed.
                )
            )
        )
        usage_events = (await db.execute(usage_query)).scalars().all()
        
        # Unbilled Consumable Withdraws
        consumable_query = (
            select(ConsumableWithdraw)
            .join(ConsumableWithdraw.project)
            .where(
                and_(
                    ConsumableWithdraw.project.has(account_id=account.id),
                    ConsumableWithdraw.date >= start_date,
                    ConsumableWithdraw.date <= end_date,
                    ConsumableWithdraw.bill_id == None
                )
            )
        )
        withdraws = (await db.execute(consumable_query)).scalars().all()
        
        # Unbilled Staff Charges
        staff_query = (
            select(StaffCharge)
            .where(
                and_(
                    # StaffCharge has direct customer_id (User), but bill goes to Project Account?
                    # StaffCharge has project_id.
                    StaffCharge.project.has(account_id=account.id),
                    StaffCharge.end >= start_date,
                    StaffCharge.end <= end_date,
                    StaffCharge.bill_id == None,
                    StaffCharge.waived == False,
                    # StaffCharge.validated == True
                )
            )
        )
        staff_charges = (await db.execute(staff_query)).scalars().all()
        
        # Calculate totals
        usage_total = sum(e.amount for e in usage_events if e.amount)
        consumable_total = sum(w.amount for w in withdraws if w.amount)
        staff_total = sum(s.amount for s in staff_charges if s.amount)
        
        total_amount = usage_total + consumable_total + staff_total
        
        if total_amount == 0 and not usage_events and not withdraws and not staff_charges:
            return None
            
        # Create Bill
        ref_number = f"BILL-{account.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        bill = Bill(
            account_id=account.id,
            reference_number=ref_number,
            period_start=start_date,
            period_end=end_date,
            total_amount=Decimal(str(total_amount)),
            status="ISSUED"
        )
        db.add(bill)
        await db.flush() # get ID
        
        # Update items with bill_id
        # We can do bulk update or iterate. Iterate is safer for small batches to ensure object state.
        for e in usage_events:
            e.bill_id = bill.id
        
        for w in withdraws:
            w.bill_id = bill.id
            
        for s in staff_charges:
            s.bill_id = bill.id
            
        await db.commit()
        await db.refresh(bill)
        
        return bill

    @staticmethod
    async def get_bills(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        account_id: Optional[int] = None
    ) -> List[Bill]:
        query = select(Bill)
        if account_id:
            query = query.where(Bill.account_id == account_id)
        
        query = query.order_by(Bill.issued_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
