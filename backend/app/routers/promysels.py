from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Promysel, User, Role
from app.schemas import PromyselCreate, PromyselUpdate, PromyselOut
from app.deps import get_current_user, require_roles

router = APIRouter(prefix="/promysels", tags=["promysels"])


@router.get("", response_model=list[PromyselOut])
async def list_promysels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Список промыслов. Доступно всем авторизованным."""
    result = await db.execute(select(Promysel).order_by(Promysel.id))
    return result.scalars().all()


@router.get("/{promysel_id}", response_model=PromyselOut)
async def get_promysel(
    promysel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    promysel = (await db.execute(
        select(Promysel).where(Promysel.id == promysel_id)
    )).scalar_one_or_none()
    if not promysel:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Промысел не найден")
    return promysel


@router.post("", response_model=PromyselOut, status_code=status.HTTP_201_CREATED)
async def create_promysel(
    data: PromyselCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.ENGINEER)),
):
    """Создание промысла. Только admin и engineer."""
    existing = (await db.execute(
        select(Promysel).where(Promysel.name == data.name)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Промысел с таким названием уже существует")

    promysel = Promysel(name=data.name, region=data.region)
    db.add(promysel)
    await db.commit()
    await db.refresh(promysel)
    return promysel


@router.patch("/{promysel_id}", response_model=PromyselOut)
async def update_promysel(
    promysel_id: int,
    data: PromyselUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.ENGINEER)),
):
    promysel = (await db.execute(
        select(Promysel).where(Promysel.id == promysel_id)
    )).scalar_one_or_none()
    if not promysel:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Промысел не найден")

    if data.name is not None:
        duplicate = (await db.execute(
            select(Promysel).where(Promysel.name == data.name, Promysel.id != promysel_id)
        )).scalar_one_or_none()
        if duplicate:
            raise HTTPException(status.HTTP_409_CONFLICT, "Промысел с таким названием уже существует")
        promysel.name = data.name
    if data.region is not None:
        promysel.region = data.region

    await db.commit()
    await db.refresh(promysel)
    return promysel


@router.delete("/{promysel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promysel(
    promysel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN)),
):
    """Удаление промысла. Только admin."""
    promysel = (await db.execute(
        select(Promysel).where(Promysel.id == promysel_id)
    )).scalar_one_or_none()
    if not promysel:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Промысел не найден")

    await db.delete(promysel)
    await db.commit()