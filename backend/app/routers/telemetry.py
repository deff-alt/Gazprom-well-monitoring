from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Telemetry, Well, User, Role
from app.schemas import TelemetryIn, TelemetryOut, TelemetryPage
from app.deps import get_current_user, require_roles

router = APIRouter(tags=["telemetry"])


WINDOWS = {
    "1h": timedelta(hours=1),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


@router.post(
    "/internal/v1/telemetry",
    status_code=status.HTTP_201_CREATED,
    summary="Приём одной точки телеметрии от шлюза",
)
async def ingest_telemetry(
    data: TelemetryIn,
    db: AsyncSession = Depends(get_db),
):
    # Проверяем, что скважина существует
    well = (await db.execute(
        select(Well).where(Well.id == data.well_id)
    )).scalar_one_or_none()
    if not well:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Скважина {data.well_id} не найдена")

    point = Telemetry(**data.model_dump())
    db.add(point)
    await db.commit()
    await db.refresh(point)
    return {"id": point.id, "status": "recorded"}


@router.get(
    "/api/v1/telemetry/{well_id}",
    response_model=TelemetryPage,
    summary="Телеметрия по скважине за период (для графиков в UI)",
)
async def list_telemetry(
    well_id: int,
    window: str = Query("24h", regex="^(1h|24h|7d|30d)$"),
    page: int = Query(0, ge=0),
    size: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - WINDOWS[window]

    base_q = select(Telemetry).where(
        Telemetry.well_id == well_id,
        Telemetry.ts >= since,
    )

    total = (await db.execute(
        select(func.count()).select_from(base_q.subquery())
    )).scalar_one()

    rows = (await db.execute(
        base_q.order_by(Telemetry.ts.desc()).offset(page * size).limit(size)
    )).scalars().all()

    return TelemetryPage(items=rows, total=total)


@router.get(
    "/internal/v1/telemetry/{well_id}",
    response_model=list[TelemetryOut],
    summary="Окно телеметрии для ML-инференса",
)
async def ml_window(
    well_id: int,
    window: str = Query(..., regex="^(1h|24h|7d)$"),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now(timezone.utc) - WINDOWS[window]
    rows = (await db.execute(
        select(Telemetry)
        .where(Telemetry.well_id == well_id, Telemetry.ts >= since)
        .order_by(Telemetry.ts.asc())
    )).scalars().all()
    return rows