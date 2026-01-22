from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.usage_event import UsageEvent
from app.models.project import Project
from app.schemas.bill import BillResponse, BillDetailResponse, BillGenerationRequest, BillUpdate
from app.schemas.user import UserBasic
from app.schemas.usage_event import UsageEventResponse
from app.services.billing_service import BillingService

router = APIRouter()

@router.post("/generate", response_model=List[BillResponse])
async def generate_bills(
    request: BillGenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    手动触发账单生成 (需要管理员权限)

    当前规则（无周期）：
    - 合并历史所有未结算账单（按用户）
    - 把未出账但已验证的使用记录金额加进来
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can generate bills"
        )
    
    bills = await BillingService.generate_bills(db, request.account_ids)
    return bills

@router.get("/", response_model=List[BillResponse])
async def get_bills(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    account_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取账单列表"""
    # 普通用户只能查看自己相关的账单
    if not current_user.is_staff and not current_user.is_superuser:
        # TODO: Implement accurate user-account billing filtering
        # Current fallback: Return empty list to prevent data leak
        return []

    return await BillingService.get_bills(db, skip, limit, account_id)


@router.get("/{bill_id}", response_model=BillDetailResponse)
async def get_bill_detail(
    bill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取账单详情（包含关联使用记录和用户信息）"""

    bill = await BillingService.get_bill_detail(db, bill_id)
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found",
        )

    # 权限：管理员可看全部；普通用户仅可看自己的账单
    owner_user_id = None
    if bill.account is not None:
        owner_user_id = bill.account.user_id

    if not (current_user.is_staff or current_user.is_superuser):
        if owner_user_id is None or owner_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to view this bill",
            )

    # 确保关联完整：把该账号下符合出账条件但尚未出账的使用记录挂到该账单（仅未结算账单）
    if bill.status in {"DRAFT", "ISSUED"}:
        await BillingService.attach_unbilled_usage_events_to_bill(db, bill)

    user_basic = None
    if bill.account is not None and bill.account.user is not None:
        user_basic = UserBasic.model_validate(bill.account.user)

    # 关联使用记录：只返回真正挂在该账单上的记录（bill_id == 当前账单）
    usage_events = (
        await db.execute(
            select(UsageEvent)
            .options(
                selectinload(UsageEvent.tool),
                selectinload(UsageEvent.project),
                selectinload(UsageEvent.user),
                selectinload(UsageEvent.operator),
            )
            .where(UsageEvent.bill_id == bill.id)
        )
    ).scalars().all()

    usage_events = sorted(list(usage_events), key=lambda e: (e.start or datetime.min))

    return BillDetailResponse(
        **BillResponse.model_validate(bill).model_dump(),
        user=user_basic,
        usage_events=[UsageEventResponse.model_validate(e) for e in usage_events],
    )


@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: int,
    bill_in: BillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """编辑账单（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update bills",
        )

    if bill_in.status is not None:
        allowed = {"DRAFT", "ISSUED", "PAID", "CANCELLED"}
        if bill_in.status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Allowed: {sorted(allowed)}",
            )

    updated = await BillingService.update_bill(db, bill_id, bill_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found",
        )
    return updated
