"""
Эндпоинты для дашборда: KPI, карта скважин, последние алерты.

Пока нет ML и алертов, эндпоинт alerts-last возвращает пустой список —
после ML-модуля начнёт возвращать реальные данные.
"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.database import get_db
from app.models import Well, User, Promysel, Locality, Role, Telemetry
from app.deps import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/kpi")
async def get_kpi(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """KPI для верхней панели дашборда."""
    # Базовая фильтрация по промыслу для head
    base_filter = []
    if current_user.role == Role.HEAD and current_user.promysel_id is not None:
        base_filter.append(Well.promysel_id == current_user.promysel_id)

    total = (await db.execute(
        select(func.count(Well.id)).where(*base_filter)
    )).scalar_one()

    by_status_rows = (await db.execute(
        select(Well.status, func.count(Well.id)).where(*base_filter).group_by(Well.status)
    )).all()
    by_status = {str(s.value if hasattr(s, "value") else s): c for s, c in by_status_rows}

    # Средний дебит газа за последние 24 часа (из телеметрии)
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    avg_gas = (await db.execute(
        select(func.avg(Telemetry.flow_rate_gas))
        .join(Well, Well.id == Telemetry.well_id)
        .where(Telemetry.ts >= since, *base_filter)
    )).scalar()

    return {
        "total_wells": total,
        "active": by_status.get("active", 0),
        "in_repair": by_status.get("in_repair", 0),
        "suspended": by_status.get("suspended", 0),
        "plugged": by_status.get("plugged", 0),
        "active_alerts": 0,  # появится после ML
        "avg_gas_last_24h": float(avg_gas) if avg_gas else None,
    }


@router.get("/wells-map")
async def get_wells_map(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Все скважины с координатами для отображения на карте."""
    query = (
        select(Well)
        .options(
            selectinload(Well.locality),
            selectinload(Well.promysel),
        )
        .where(Well.latitude.is_not(None), Well.longitude.is_not(None))
    )
    if current_user.role == Role.HEAD and current_user.promysel_id is not None:
        query = query.where(Well.promysel_id == current_user.promysel_id)

    wells = (await db.execute(query)).scalars().all()

    # Получаем начальников промыслов (для каждой скважины показываем её head)
    promysel_ids = list({w.promysel_id for w in wells if w.promysel_id})
    heads_by_promysel = {}
    if promysel_ids:
        heads = (await db.execute(
            select(User).where(User.role == Role.HEAD, User.promysel_id.in_(promysel_ids))
        )).scalars().all()
        heads_by_promysel = {h.promysel_id: h.full_name or h.username for h in heads}

    result = []
    for w in wells:
        result.append({
            "id": w.id,
            "well_number": w.well_number,
            "status": w.status.value if hasattr(w.status, "value") else str(w.status),
            "type": w.type.value if hasattr(w.type, "value") else str(w.type),
            "latitude": float(w.latitude) if w.latitude else None,
            "longitude": float(w.longitude) if w.longitude else None,
            "locality_name": w.locality.name if w.locality else None,
            "promysel_id": w.promysel_id,
            "promysel_name": w.promysel.name if w.promysel else None,
            "head_name": heads_by_promysel.get(w.promysel_id),
            "depth": float(w.depth) if w.depth else None,
            "reservoir_pressure": float(w.reservoir_pressure) if w.reservoir_pressure else None,
            "temperature": float(w.temperature) if w.temperature else None,
            "commissioning_date": w.commissioning_date.isoformat() if w.commissioning_date else None,
        })

    return result


@router.get("/alerts-last")
async def get_alerts_last(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Последние алерты.
    Пока ML не работает — пустой список.
    Когда появится таблица alerts — вернём данные из неё.
    """
    return {
        "items": [],
        "note": "Алерты появятся после запуска ML-модуля",
    }