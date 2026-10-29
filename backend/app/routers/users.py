from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Promysel, Role
from app.schemas import UserCreate, UserUpdate, UserAdminOut
from app.deps import require_roles
from app.security import hash_password

router = APIRouter(prefix="/users", tags=["users"])


def _to_out(u: User) -> UserAdminOut:
    return UserAdminOut(
        id=u.id,
        username=u.username,
        full_name=u.full_name,
        role=u.role,
        promysel_id=u.promysel_id,
        promysel_name=u.promysel.name if u.promysel else None,
        is_active=u.is_active,
        created_at=u.created_at,
    )


@router.get("", response_model=list[UserAdminOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN)),
):
    result = await db.execute(
        select(User).options(selectinload(User.promysel)).order_by(User.id)
    )
    return [_to_out(u) for u in result.scalars().all()]


@router.post("", response_model=UserAdminOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_roles(Role.ADMIN)),
):
    existing = (await db.execute(
        select(User).where(User.username == data.username)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Пользователь с таким логином уже существует")

    if data.promysel_id is not None:
        pr = (await db.execute(
            select(Promysel).where(Promysel.id == data.promysel_id)
        )).scalar_one_or_none()
        if not pr:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Промысел не найден")

    user = User(
        username=data.username,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=data.role,
        promysel_id=data.promysel_id,
        is_active=True,
    )
    db.add(user)
    await db.commit()

    user = (await db.execute(
        select(User).options(selectinload(User.promysel)).where(User.id == user.id)
    )).scalar_one()
    return _to_out(user)


@router.patch("/{user_id}", response_model=UserAdminOut)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_roles(Role.ADMIN)),
):
    user = (await db.execute(
        select(User).where(User.id == user_id)
    )).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")

    update_data = data.model_dump(exclude_unset=True)

    if "role" in update_data and user.id == current.id and update_data["role"] != Role.ADMIN:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нельзя снять с себя роль администратора")

    if "is_active" in update_data and user.id == current.id and not update_data["is_active"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нельзя заблокировать себя")

    if "promysel_id" in update_data and update_data["promysel_id"] is not None:
        pr = (await db.execute(
            select(Promysel).where(Promysel.id == update_data["promysel_id"])
        )).scalar_one_or_none()
        if not pr:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Промысел не найден")

    if "password" in update_data and update_data["password"]:
        user.hashed_password = hash_password(update_data.pop("password"))
    else:
        update_data.pop("password", None)

    for k, v in update_data.items():
        setattr(user, k, v)

    await db.commit()

    user = (await db.execute(
        select(User).options(selectinload(User.promysel)).where(User.id == user_id)
    )).scalar_one()
    return _to_out(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_roles(Role.ADMIN)),
):
    user = (await db.execute(
        select(User).where(User.id == user_id)
    )).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Пользователь не найден")
    if user.id == current.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нельзя удалить самого себя")

    await db.delete(user)
    await db.commit()