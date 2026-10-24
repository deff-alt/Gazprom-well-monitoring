from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Locality, Well, User, Role
from app.schemas import LocalityCreate, LocalityUpdate, LocalityOut
from app.deps import get_current_user, require_roles

router = APIRouter(prefix="/localities", tags=["localities"])


@router.get("", response_model=list[LocalityOut])
async def list_localities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Список месторождений. Доступно всем авторизованным."""
    result = await db.execute(select(Locality).order_by(Locality.id))
    return result.scalars().all()


@router.get("/{locality_id}", response_model=LocalityOut)
async def get_locality(
    locality_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    locality = (await db.execute(
        select(Locality).where(Locality.id == locality_id)
    )).scalar_one_or_none()
    if not locality:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Месторождение не найдено")
    return locality


@router.post("", response_model=LocalityOut, status_code=status.HTTP_201_CREATED)
async def create_locality(
    data: LocalityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.ENGINEER)),
):
    """Создание месторождения. Только admin и engineer."""
    existing = (await db.execute(
        select(Locality).where(Locality.name == data.name)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Месторождение с таким названием уже существует")

    locality = Locality(name=data.name, region=data.region)
    db.add(locality)
    await db.commit()
    await db.refresh(locality)
    return locality


@router.patch("/{locality_id}", response_model=LocalityOut)
async def update_locality(
    locality_id: int,
    data: LocalityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.ENGINEER)),
):
    locality = (await db.execute(
        select(Locality).where(Locality.id == locality_id)
    )).scalar_one_or_none()
    if not locality:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Месторождение не найдено")

    if data.name is not None:
        duplicate = (await db.execute(
            select(Locality).where(Locality.name == data.name, Locality.id != locality_id)
        )).scalar_one_or_none()
        if duplicate:
            raise HTTPException(status.HTTP_409_CONFLICT, "Месторождение с таким названием уже существует")
        locality.name = data.name
    if data.region is not None:
        locality.region = data.region

    await db.commit()
    await db.refresh(locality)
    return locality


@router.delete("/{locality_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_locality(
    locality_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN)),
):
    """
    Удаление месторождения. Только admin.
    Запрещено, если внутри есть скважины (RESTRICT).
    """
    locality = (await db.execute(
        select(Locality).where(Locality.id == locality_id)
    )).scalar_one_or_none()
    if not locality:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Месторождение не найдено")

    # Проверяем, есть ли скважины внутри
    wells_count = (await db.execute(
        select(func.count(Well.id)).where(Well.locality_id == locality_id)
    )).scalar_one()

    if wells_count > 0:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Нельзя удалить месторождение: в нём {wells_count} скважин(а). "
            f"Сначала удалите или перенесите их.",
        )

    try:
        await db.delete(locality)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Нельзя удалить месторождение: есть связанные записи",
        )