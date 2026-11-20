from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models import Telemetry, Well, Alert, AlertSeverity, AlertStatus, User, Role
from app.permissions import can_train_model, can_predict
from app.ml_service import train, predict

router = APIRouter(prefix="/api/v1/ml", tags=["machine-learning"])


@router.get("/status")
async def model_status(user: User = Depends(get_current_user)):
    from app.ml_service import MODEL_PATH
    if not MODEL_PATH.exists(): return {"trained": False, "model": "Isolation Forest"}
    import joblib
    bundle = joblib.load(MODEL_PATH)
    return {"trained": True, "model": "Isolation Forest", "trained_at": bundle["trained_at"], "training_samples": bundle["samples"]}


@router.post("/train")
async def train_model(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if not can_train_model(user): raise HTTPException(403, "Обучение модели доступно только администратору")
    rows = (await db.execute(select(Telemetry).order_by(Telemetry.ts.asc()))).scalars().all()
    try: return train(rows)
    except ValueError as exc: raise HTTPException(422, str(exc))


@router.post("/predict/{well_id}")
async def predict_well(well_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    if not can_predict(user): raise HTTPException(403, "Недостаточно прав для запуска диагностики")
    well = (await db.execute(select(Well).where(Well.id == well_id))).scalar_one_or_none()
    if not well: raise HTTPException(404, "Скважина не найдена")
    if user.role == Role.HEAD and well.promysel_id != user.promysel_id: raise HTTPException(403, "Нет доступа к скважине")
    row = (await db.execute(select(Telemetry).where(Telemetry.well_id == well_id).order_by(Telemetry.ts.desc()).limit(1))).scalar_one_or_none()
    if not row: raise HTTPException(422, "Нет телеметрии для диагностики")
    try: result = predict(row)
    except FileNotFoundError as exc: raise HTTPException(409, str(exc))
    if result["is_anomaly"]:
        recent_since = datetime.now(timezone.utc) - timedelta(hours=2)
        existing = (await db.execute(select(Alert).where(
            Alert.well_id == well_id,
            Alert.parameter == result["parameter"],
            Alert.status.in_([AlertStatus.NEW, AlertStatus.IN_PROGRESS]),
            Alert.created_at >= recent_since,
        ).limit(1))).scalar_one_or_none()
        if existing:
            result["alert_created"] = False
            result["existing_alert_id"] = existing.id
        else:
            severity = AlertSeverity.CRITICAL if result["anomaly_score"] >= 0.8 else AlertSeverity.WARNING
            alert = Alert(well_id=well_id, parameter=result["parameter"], anomaly_score=result["anomaly_score"], severity=severity, status=AlertStatus.NEW, description=f"Isolation Forest выявил нетипичное сочетание параметров. Оценка аномальности: {result['anomaly_score']:.2f}.")
            db.add(alert); await db.commit()
            result["alert_created"] = True
    else: result["alert_created"] = False
    result["well_id"] = well_id
    result["well_number"] = well.well_number
    return result
