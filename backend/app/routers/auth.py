from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenPair, RefreshRequest, UserOut
from app.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenPair)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.username == data.username))).scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "User is blocked")

    return TokenPair(
        access_token=create_access_token(user.username, user.role.value, user.promysel_id),
        refresh_token=create_refresh_token(user.username, user.role.value, user.promysel_id),
    )

@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(data.refresh_token)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong token type")

    user = (await db.execute(select(User).where(User.username == payload["sub"]))).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")

    return TokenPair(
        access_token=create_access_token(user.username, user.role.value, user.promysel_id),
        refresh_token=create_refresh_token(user.username, user.role.value, user.promysel_id),
    )

@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user