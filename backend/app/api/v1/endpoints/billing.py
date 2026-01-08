from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.bill import BillResponse, BillGenerationRequest, BillUpdate
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
