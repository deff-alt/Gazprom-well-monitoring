from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Well, Locality, Promysel
from app.schemas import WellOut, LocalityOut, PromyselOut

router = APIRouter(tags=["wells"])

def _to_out(w: Well) -> WellOut:
    return WellOut(
        id=w.id, well_number=w.well_number,
        locality_id=w.locality_id,
        locality_name=w.locality.name if w.locality else None,
        promysel_id=w.promysel_id,
        promysel_name=w.promysel.name if w.promysel else None,
        type=w.type, status=w.status,
        depth=w.depth, reservoir_pressure=w.reservoir_pressure,
        temperature=w.temperature,
        latitude=w.latitude, longitude=w.longitude,
    )

@router.get("/api/v1/wells", response_model=list[WellOut])
async def list_wells(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(Well).options(selectinload(Well.locality), selectinload(Well.promysel))
    )).scalars().all()
    return [_to_out(w) for w in rows]

@router.get("/api/v1/localities", response_model=list[LocalityOut])
async def list_localities(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Locality))).scalars().all()
    return rows

@router.get("/api/v1/promysels", response_model=list[PromyselOut])
async def list_promysels(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Promysel))).scalars().all()
    return rows

@router.get("/internal/v1/wells/{well_id}", response_model=WellOut)
async def get_well_internal(well_id: int, db: AsyncSession = Depends(get_db)):
    """Внутренний эндпоинт для других сервисов (alert, telemetry)."""
    w = (await db.execute(
        select(Well)
        .options(selectinload(Well.locality), selectinload(Well.promysel))
        .where(Well.id == well_id)
    )).scalar_one_or_none()
    if not w:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Well not found")
    return _to_out(w)