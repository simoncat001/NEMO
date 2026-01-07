from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.bill import BillResponse, BillGenerationRequest
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
    可以指定时间段和账户列表
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can generate bills"
        )
    
    bills = await BillingService.generate_bills(
        db, 
        request.start_date.replace(tzinfo=None), 
        request.end_date.replace(tzinfo=None), 
        request.account_ids
    )
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
