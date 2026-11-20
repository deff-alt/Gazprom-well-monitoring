from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Alert, AlertStatus, AlertSeverity, User, Role, Well
from app.permissions import can_work_with_alerts

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


def serialize_alert(a: Alert):
    return {
        "id": a.id, "well_id": a.well_id,
        "well_number": a.well.well_number if a.well else str(a.well_id),
        "locality_name": a.well.locality.name if a.well and a.well.locality else None,
        "promysel_id": a.well.promysel_id if a.well else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "parameter": a.parameter,
        "anomaly_score": float(a.anomaly_score) if a.anomaly_score is not None else None,
        "severity": a.severity.value if hasattr(a.severity, "value") else str(a.severity),
        "status": a.status.value if hasattr(a.status, "value") else str(a.status),
        "assigned_to": a.assigned_to,
        "assignee_name": (a.assignee.full_name or a.assignee.username) if a.assignee else None,
        "description": a.description,
        "resolution_comment": a.resolution_comment,
    }


@router.get("")
async def list_alerts(
    severity: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    well_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    filters = []
    if user.role == Role.HEAD:
        filters.append(Well.promysel_id == user.promysel_id)
    if severity:
        try: filters.append(Alert.severity == AlertSeverity(severity))
        except ValueError: raise HTTPException(400, "Неизвестный уровень критичности")
    if status_filter:
        try: filters.append(Alert.status == AlertStatus(status_filter))
        except ValueError: raise HTTPException(400, "Неизвестный статус алерта")
    if well_id is not None: filters.append(Alert.well_id == well_id)
    count_q = select(func.count(Alert.id)).join(Well, Alert.well_id == Well.id).where(*filters)
    total = (await db.execute(count_q)).scalar_one()
    q = select(Alert).options(
        selectinload(Alert.well).selectinload(Well.locality),
        selectinload(Alert.assignee),
    ).join(Well, Alert.well_id == Well.id).where(*filters)
    rows = (await db.execute(q.order_by(Alert.created_at.desc()).offset(offset).limit(limit))).scalars().all()
    return {"items": [serialize_alert(a) for a in rows], "total": total}


@router.patch("/{alert_id}")
async def update_alert(
    alert_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not can_work_with_alerts(user):
        raise HTTPException(403, "Недостаточно прав для обработки алертов")
    alert = (await db.execute(
        select(Alert).options(selectinload(Alert.well).selectinload(Well.locality), selectinload(Alert.assignee))
        .where(Alert.id == alert_id)
    )).scalar_one_or_none()
    if not alert: raise HTTPException(404, "Алерт не найден")
    if user.role == Role.HEAD and alert.well.promysel_id != user.promysel_id:
        raise HTTPException(403, "Нет доступа к алерту другого промысла")
    allowed = {"new", "in_progress", "resolved", "dismissed"}
    new_status = payload.get("status")
    if new_status not in allowed: raise HTTPException(400, "Недопустимый статус")
    alert.status = AlertStatus(new_status)
    if new_status == "in_progress": alert.assigned_to = user.id
    if new_status in ("resolved", "dismissed"):
        alert.resolution_comment = str(payload.get("resolution_comment") or "")[:2000] or None
        if alert.assigned_to is None: alert.assigned_to = user.id
    await db.commit()
    await db.refresh(alert)
    return serialize_alert(alert)
