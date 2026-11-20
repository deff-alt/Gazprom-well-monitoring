"""Мок notification-service.
Принимает уведомления и логирует их. По методичке допустимо использовать мок
для сервиса, который не входит в минимальные 4 обязательных.
"""
from datetime import datetime
from fastapi import FastAPI

app = FastAPI(title="notification-mock")

SENT: list[dict] = []

@app.get("/health")
async def health():
    return {"status": "ok", "service": "notification-mock", "sent": len(SENT)}

@app.post("/internal/v1/notifications", status_code=201)
async def send_notification(payload: dict):
    record = {"sent_at": datetime.utcnow().isoformat(), "payload": payload}
    SENT.append(record)
    print(f"[notification] {record}")
    return record

@app.get("/internal/v1/notifications")
async def list_notifications():
    return SENT