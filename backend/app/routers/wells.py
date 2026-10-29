from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Well, Locality, Promysel, User, Role
from app.schemas import WellCreate, WellUpdate, WellOut
from app.deps import get_current_user, require_roles

router = APIRouter(prefix="/wells", tags=["wells"])


def _well_to_out(well: Well) -> WellOut:
    """Преобразует Well (ORM) в WellOut с подтянутыми именами связей."""
    return WellOut(
        id=well.id,
        well_number=well.well_number,
        locality_id=well.locality_id,
        locality_name=well.locality.name if well.locality else "",
        promysel_id=well.promysel_id,
        promysel_name=well.promysel.name if well.promysel else None,
        type=well.type,
        status=well.status,
        latitude=well.latitude,
        longitude=well.longitude,
        depth=well.depth,
        hanger_diameter=well.hanger_diameter,
        drilling_start_date=well.drilling_start_date,
        drilling_end_date=well.drilling_end_date,
        commissioning_date=well.commissioning_date,
        inventory_number=well.inventory_number,
        reservoir_pressure=well.reservoir_pressure,
        buffer_pressure=well.buffer_pressure,
        casing_pressure=well.casing_pressure,
        temperature=well.temperature,
        choke_diameter=well.choke_diameter,
        planned_lifetime=well.planned_lifetime,
    )


@router.get("", response_model=list[WellOut])
async def list_wells(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Список скважин.
    - head видит только скважины своего промысла
    - остальные роли видят все
    """
    query = select(Well).options(
        selectinload(Well.locality),
        selectinload(Well.promysel),
    ).order_by(Well.id)

    if current_user.role == Role.HEAD and current_user.promysel_id is not None:
        query = query.where(Well.promysel_id == current_user.promysel_id)

    result = await db.execute(query)
    wells = result.scalars().all()
    return [_well_to_out(w) for w in wells]


@router.get("/{well_id}", response_model=WellOut)
async def get_well(
    well_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    well = (await db.execute(
        select(Well)
        .options(selectinload(Well.locality), selectinload(Well.promysel))
        .where(Well.id == well_id)
    )).scalar_one_or_none()

    if not well:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Скважина не найдена")

    if (current_user.role == Role.HEAD
            and current_user.promysel_id is not None
            and well.promysel_id != current_user.promysel_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Нет доступа к скважине другого промысла")

    return _well_to_out(well)


@router.post("", response_model=WellOut, status_code=status.HTTP_201_CREATED)
async def create_well(
    data: WellCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.ENGINEER)),
):
    """Создание скважины. Только admin и engineer."""
    # Проверка уникальности номера
    existing = (await db.execute(
        select(Well).where(Well.well_number == data.well_number)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Скважина с таким номером уже существует")

    # Проверка, что месторождение существует
    locality = (await db.execute(
        select(Locality).where(Locality.id == data.locality_id)
    )).scalar_one_or_none()
    if not locality:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Месторождение не найдено")

    # Проверка промысла (если указан)
    if data.promysel_id is not None:
        promysel = (await db.execute(
            select(Promysel).where(Promysel.id == data.promysel_id)
        )).scalar_one_or_none()
        if not promysel:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Промысел не найден")

    well = Well(**data.model_dump())
    db.add(well)
    await db.commit()

    # Перечитываем с подгруженными связями
    well = (await db.execute(
        select(Well)
        .options(selectinload(Well.locality), selectinload(Well.promysel))
        .where(Well.id == well.id)
    )).scalar_one()
    return _well_to_out(well)


@router.patch("/{well_id}", response_model=WellOut)
async def update_well(
    well_id: int,
    data: WellUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.ENGINEER)),
):
    well = (await db.execute(
        select(Well).where(Well.id == well_id)
    )).scalar_one_or_none()
    if not well:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Скважина не найдена")

    update_data = data.model_dump(exclude_unset=True)

    # Если меняют locality_id — проверяем, что новое месторождение существует
    if "locality_id" in update_data:
        loc = (await db.execute(
            select(Locality).where(Locality.id == update_data["locality_id"])
        )).scalar_one_or_none()
        if not loc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Месторождение не найдено")

    if "promysel_id" in update_data and update_data["promysel_id"] is not None:
        pr = (await db.execute(
            select(Promysel).where(Promysel.id == update_data["promysel_id"])
        )).scalar_one_or_none()
        if not pr:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Промысел не найден")

    for field, value in update_data.items():
        setattr(well, field, value)

    await db.commit()

    well = (await db.execute(
        select(Well)
        .options(selectinload(Well.locality), selectinload(Well.promysel))
        .where(Well.id == well_id)
    )).scalar_one()
    return _well_to_out(well)


@router.delete("/{well_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_well(
    well_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(Role.ADMIN, Role.ENGINEER)),
):
    """
    Удаление скважины. Каскадно удаляются экспертизы, ремонты,
    телеметрия и алерты (настройка ON DELETE CASCADE в модели).
    """
    well = (await db.execute(
        select(Well).where(Well.id == well_id)
    )).scalar_one_or_none()
    if not well:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Скважина не найдена")

    await db.delete(well)
    await db.commit()