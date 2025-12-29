"""Common FastAPI dependencies.

This repo's backend is currently in an early stage and doesn't yet include the
full auth/session stack. Several endpoints import `app.core.deps` for database
sessions and current-user resolution.

For preview and local development, we provide minimal implementations:
- `get_db`: yields a SQLAlchemy Session from `app.db.session.SessionLocal`
- `get_current_user`: returns the first user (or creates one if none exist)
- `get_current_staff_user`: same as current user, but forces `is_staff=True`

These stubs are intentionally lightweight so the API can boot and Swagger can be
used. Replace with real authentication/authorization for production.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_password_hash


async def _get_or_create_preview_user(db: AsyncSession, *, staff: bool = False) -> User:
    result = await db.execute(select(User).order_by(User.id.asc()).limit(1))
    user = result.scalar_one_or_none()
    if user is not None:
        if staff and not user.is_staff:
            user.is_staff = True
            db.add(user)
            await db.commit()
            await db.refresh(user)
        return user

    user = User(
        username="admin",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        # Preview default credential: admin / admin
        hashed_password=get_password_hash("admin"),
        is_active=True,
        is_staff=staff or True,
        is_superuser=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_current_user(db: AsyncSession = Depends(get_db)) -> User:
    return await _get_or_create_preview_user(db, staff=False)


async def get_current_staff_user(db: AsyncSession = Depends(get_db)) -> User:
    user = await _get_or_create_preview_user(db, staff=True)
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required",
        )
    return user
