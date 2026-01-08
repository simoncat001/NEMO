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
from app.schemas.bill import BillCreate, BillResponse, BillUpdate
from app.services.account_service import AccountService
from app.models.user import User

class BillingService:
    @staticmethod
    async def get_bill_by_id(db: AsyncSession, bill_id: int) -> Optional[Bill]:
        result = await db.execute(
            select(Bill)
            .options(selectinload(Bill.account).selectinload(Account.user))
            .where(Bill.id == bill_id)
        )
        return result.scalars().first()

    @staticmethod
    async def generate_bills(
        db: AsyncSession,
        account_ids: Optional[List[int]] = None
    ) -> List[Bill]:
        """合并生成账单（无周期）：

        - 把历史所有未结算账单按用户合并（金额相加）
        - 把未生成账单的、且已管理员确认（validated）的使用记录金额加进来
        """
        return await BillingService.consolidate_unpaid_bills(db, account_ids)

    @staticmethod
    async def consolidate_unpaid_bills(
        db: AsyncSession,
        account_ids: Optional[List[int]] = None,
    ) -> List[Bill]:
        unpaid_statuses = {"DRAFT", "ISSUED"}

        if account_ids:
            accounts = (
                await db.execute(
                    select(Account).where(
                        Account.active == True,
                        Account.user_id.is_not(None),
                        Account.id.in_(account_ids),
                    )
                )
            ).scalars().all()
        else:
            users = (await db.execute(select(User))).scalars().all()
            accounts = []
            for user in users:
                acc = await AccountService.get_or_create_user_account(db, user)
                if acc.active and acc.user_id is not None:
                    accounts.append(acc)

        consolidated: List[Bill] = []

        for account in accounts:
            if account.user_id is None:
                continue

            unpaid_bills = (
                await db.execute(
                    select(Bill)
                    .where(
                        Bill.account_id == account.id,
                        Bill.status.in_(unpaid_statuses),
                    )
                    .order_by(Bill.issued_date.desc())
                )
            ).scalars().all()

            # Choose a target unpaid bill to merge into (if any).
            target_bill: Optional[Bill] = unpaid_bills[0] if unpaid_bills else None
            other_bills = unpaid_bills[1:] if len(unpaid_bills) > 1 else []

            existing_unpaid_total = Decimal("0")
            for b in unpaid_bills:
                if b.total_amount is not None:
                    existing_unpaid_total += Decimal(str(b.total_amount))

            # Add unbilled, validated usage events (admin-confirmed)
            usage_events = (
                await db.execute(
                    select(UsageEvent).where(
                        and_(
                            UsageEvent.user_id == account.user_id,
                            UsageEvent.bill_id == None,
                            UsageEvent.validated == True,
                            UsageEvent.waived == False,
                        )
                    )
                )
            ).scalars().all()

            # Keep existing behavior for other unbilled items
            withdraws = (
                await db.execute(
                    select(ConsumableWithdraw).where(
                        and_(
                            ConsumableWithdraw.user_id == account.user_id,
                            ConsumableWithdraw.bill_id == None,
                        )
                    )
                )
            ).scalars().all()

            staff_charges = (
                await db.execute(
                    select(StaffCharge).where(
                        and_(
                            StaffCharge.customer_id == account.user_id,
                            StaffCharge.bill_id == None,
                            StaffCharge.waived == False,
                            StaffCharge.validated == True,
                        )
                    )
                )
            ).scalars().all()

            usage_total = sum(float(e.amount or 0) for e in usage_events)
            consumable_total = sum(float(w.amount or 0) for w in withdraws)
            staff_total = sum(float(s.amount or 0) for s in staff_charges)

            add_total = Decimal(str(usage_total + consumable_total + staff_total))
            total_amount = existing_unpaid_total + add_total

            if total_amount == 0 and not unpaid_bills and not usage_events and not withdraws and not staff_charges:
                continue

            now = datetime.utcnow()

            # If no unpaid bill exists yet, create one; otherwise merge into existing.
            if target_bill is None:
                ref_number = f"BILL-{account.id}-{now.strftime('%Y%m%d%H%M%S')}"
                target_bill = Bill(
                    account_id=account.id,
                    reference_number=ref_number,
                    period_start=now,
                    period_end=now,
                    total_amount=Decimal("0"),
                    status="ISSUED",
                )
                db.add(target_bill)
                await db.flush()

            # Move already-billed items from other unpaid bills onto the target bill
            other_bill_ids = [b.id for b in other_bills]
            if other_bill_ids:
                await db.execute(
                    update(UsageEvent)
                    .where(UsageEvent.bill_id.in_(other_bill_ids))
                    .values(bill_id=target_bill.id)
                )
                await db.execute(
                    update(ConsumableWithdraw)
                    .where(ConsumableWithdraw.bill_id.in_(other_bill_ids))
                    .values(bill_id=target_bill.id)
                )
                await db.execute(
                    update(StaffCharge)
                    .where(StaffCharge.bill_id.in_(other_bill_ids))
                    .values(bill_id=target_bill.id)
                )
                for old in other_bills:
                    old.status = "CANCELLED"

            # Assign newly billable items to the target bill
            for e in usage_events:
                e.bill_id = target_bill.id
            for w in withdraws:
                w.bill_id = target_bill.id
            for s in staff_charges:
                s.bill_id = target_bill.id

            target_bill.total_amount = total_amount

            await db.commit()
            consolidated.append((await BillingService.get_bill_by_id(db, target_bill.id)) or target_bill)

        return consolidated

    @staticmethod
    async def _generate_bill_for_account(
        db: AsyncSession,
        account: Account,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Bill]:
        # Deprecated: period-based billing is no longer used.
        # 查找该账户（用户）下未结算的收费项。
        # New rule: treat user as account, so billing is based on the user bound to the account.
        if account.user_id is None:
            return None
        
        # Unbilled Usage Events
        usage_query = (
            select(UsageEvent)
            .where(
                and_(
                    UsageEvent.user_id == account.user_id,
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
            .where(
                and_(
                    ConsumableWithdraw.user_id == account.user_id,
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
                    StaffCharge.customer_id == account.user_id,
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
        loaded = await BillingService.get_bill_by_id(db, bill.id)
        return loaded or bill

    @staticmethod
    async def get_bills(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        account_id: Optional[int] = None
    ) -> List[Bill]:
        query = select(Bill).options(selectinload(Bill.account).selectinload(Account.user))
        if account_id:
            query = query.where(Bill.account_id == account_id)
        
        query = query.order_by(Bill.issued_date.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_bill(db: AsyncSession, bill_id: int, bill_in: BillUpdate) -> Optional[Bill]:
        bill = await db.get(Bill, bill_id)
        if not bill:
            return None

        update_data = bill_in.model_dump(exclude_unset=True)

        if "due_date" in update_data and update_data["due_date"] is not None:
            update_data["due_date"] = update_data["due_date"].replace(tzinfo=None)

        for field, value in update_data.items():
            setattr(bill, field, value)

        await db.commit()
        loaded = await BillingService.get_bill_by_id(db, bill_id)
        return loaded or bill
