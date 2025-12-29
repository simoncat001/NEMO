from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.endpoints.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.staff_charge import (
    StaffChargeCreate,
    StaffChargeDetail,
    StaffChargeEnd,
    StaffChargeResponse,
    StaffChargeStats,
    StaffChargeUpdate,
)
from app.services.staff_charge_service import StaffChargeService

router = APIRouter()


@router.get("/", response_model=List[StaffChargeResponse])
async def get_staff_charges(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    staff_member_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    in_progress_only: bool = Query(False),
    validated_only: bool = Query(False),
    billable_only: bool = Query(False),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取员工收费记录列表"""
    return await StaffChargeService.get_staff_charges(
        db, skip, limit, staff_member_id, customer_id, project_id,
        in_progress_only, validated_only, billable_only, start_date, end_date
    )


@router.post("/", response_model=StaffChargeResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_charge(
    charge: StaffChargeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建员工收费记录（开始服务）
    
    - 员工可以为客户创建服务记录
    - 记录开始时间和相关信息
    """
    # 验证员工是否是 staff
    if charge.staff_member_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff members can create staff charges"
        )
    
    return await StaffChargeService.create_staff_charge(db, charge)


@router.get("/{charge_id}", response_model=StaffChargeDetail)
async def get_staff_charge(
    charge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取员工收费记录详情"""
    charge = await StaffChargeService.get_staff_charge(db, charge_id)
    if not charge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff charge not found"
        )
    
    # 添加计算属性
    response = StaffChargeDetail.model_validate(charge)
    response.duration_minutes = charge.duration_minutes()
    response.is_in_progress = charge.is_in_progress
    response.is_billable = charge.is_billable
    
    return response


@router.post("/{charge_id}/end", response_model=StaffChargeResponse)
async def end_staff_charge(
    charge_id: int,
    end_data: StaffChargeEnd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """结束员工收费记录"""
    charge = await StaffChargeService.get_staff_charge(db, charge_id)
    if not charge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff charge not found"
        )
    
    # 只有服务员工或管理员可以结束
    if charge.staff_member_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the staff member or administrator can end this charge"
        )
    
    try:
        return await StaffChargeService.end_staff_charge(db, charge_id, end_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{charge_id}", response_model=StaffChargeResponse)
async def update_staff_charge(
    charge_id: int,
    charge: StaffChargeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新员工收费记录（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can update staff charges"
        )
    
    updated = await StaffChargeService.update_staff_charge(db, charge_id, charge)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff charge not found"
        )
    return updated


@router.delete("/{charge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_charge(
    charge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除员工收费记录（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can delete staff charges"
        )
    
    deleted = await StaffChargeService.delete_staff_charge(db, charge_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff charge not found"
        )


@router.get("/staff-charges/staff/{staff_member_id}/active", response_model=List[StaffChargeResponse])
async def get_active_charges_for_staff(
    staff_member_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取员工当前的所有服务记录"""
    # 只能查看自己的或管理员可以查看所有
    if staff_member_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own active charges"
        )
    
    return await StaffChargeService.get_active_charges_for_staff(db, staff_member_id)


@router.get("/staff-charges/customer/{customer_id}/active", response_model=List[StaffChargeResponse])
async def get_active_charges_for_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取客户当前接受的所有服务记录"""
    # 只能查看自己的或管理员可以查看所有
    if customer_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own charges"
        )
    
    return await StaffChargeService.get_active_charges_for_customer(db, customer_id)


@router.post("/staff-charges/{charge_id}/validate", response_model=StaffChargeResponse)
async def validate_staff_charge(
    charge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """验证员工收费记录（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can validate staff charges"
        )
    
    charge = await StaffChargeService.validate_staff_charge(db, charge_id, current_user.id)
    if not charge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff charge not found"
        )
    return charge


@router.post("/staff-charges/{charge_id}/waive", response_model=StaffChargeResponse)
async def waive_staff_charge(
    charge_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """豁免员工收费记录（不计费，需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can waive staff charges"
        )
    
    charge = await StaffChargeService.waive_staff_charge(db, charge_id, current_user.id)
    if not charge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff charge not found"
        )
    return charge


@router.get("/staff-charges/stats", response_model=StaffChargeStats)
async def get_staff_charge_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    staff_member_id: Optional[int] = Query(None),
    customer_id: Optional[int] = Query(None),
    project_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取员工收费统计（需要管理员权限）"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can view staff charge statistics"
        )
    
    return await StaffChargeService.get_staff_charge_stats(
        db, start_date, end_date, staff_member_id, customer_id, project_id
    )
