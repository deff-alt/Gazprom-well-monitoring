"""Мок notification-service.
Принимает уведомления и логирует их. По методичке допустимо использовать мок
для сервиса, который не входит в минимальные 4 обязательных.
"""
import logging
from datetime import datetime, timezone

from fastapi import FastAPI

from app.logging_config import configure_logging
from app.request_logging import install_request_logging

logger = configure_logging("notification-mock")
app = FastAPI(title="notification-mock")
install_request_logging(app, logger)

SENT: list[dict] = []


@app.on_event("startup")
async def startup_event():
    logger.info("Запуск notification-mock")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Остановка notification-mock")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "notification-mock", "sent": len(SENT)}


@app.post("/internal/v1/notifications", status_code=201)
async def send_notification(payload: dict):
    record = {
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    SENT.append(record)
    logger.info("Уведомление принято mock-сервисом; total_sent=%s", len(SENT))
    return record


@app.get("/internal/v1/notifications")
async def list_notifications():
    logger.info("Запрошена история уведомлений; total_sent=%s", len(SENT))
    return SENT
