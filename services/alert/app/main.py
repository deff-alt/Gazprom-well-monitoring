
import os
import sqlite3
import json
import logging
import asyncio
import uuid

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.logging_config import configure_logging
from app.request_logging import install_request_logging
from app.errors import install_problem_handlers

try:
    import aio_pika
except ImportError:
    aio_pika = None


logger = configure_logging("alert")

DB = os.getenv("DB_PATH", "/data/alert.db")
RABBIT = os.getenv(
    "RABBITMQ_URL",
    "amqp://guest:guest@rabbitmq:5672/"
)


def conn():
    os.makedirs(os.path.dirname(DB) or ".", exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


async def publish(routing, payload):
    if not aio_pika:
        logger.warning(
            "aio-pika недоступен; событие не опубликовано"
        )
        return

    try:
        connection = await aio_pika.connect_robust(RABBIT)

        async with connection:
            channel = await connection.channel()

            exchange = await channel.declare_exchange(
                "well_monitor.events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            await exchange.publish(
                aio_pika.Message(
                    json.dumps(
                        payload,
                        ensure_ascii=False
                    ).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    content_type="application/json"
                ),
                routing_key=routing
            )

        logger.info("Опубликовано событие %s", routing)

    except Exception:
        logger.exception(
            "Ошибка публикации %s",
            routing
        )
        raise


async def consume(binding, callback):
    if not aio_pika:
        return

    while True:
        try:
            connection = await aio_pika.connect_robust(RABBIT)

            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=10)

                exchange = await channel.declare_exchange(
                    "well_monitor.events",
                    aio_pika.ExchangeType.TOPIC,
                    durable=True
                )

                queue = await channel.declare_queue(
                    binding.replace(".", "_"),
                    durable=True
                )

                await queue.bind(
                    exchange,
                    routing_key=binding
                )

                async with queue.iterator() as iterator:
                    async for msg in iterator:
                        async with msg.process():
                            await callback(
                                json.loads(msg.body)
                            )

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception(
                "Consumer %s перезапускается",
                binding
            )
            await asyncio.sleep(3)


    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": title,
            "status": status,
            "detail": detail
        }
    )


import httpx


async def handle_diagnosis(event):
    if not event.get("anomaly"):
        return

    c = conn()

    try:
        cur = c.execute(
            """
            INSERT OR IGNORE INTO alerts
            (
                well_id,
                measurement_id,
                severity,
                score,
                description,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.get("well_id", 0),
                event["measurement_id"],
                event["severity"],
                event["anomaly_score"],
                event.get(
                    "recommendation",
                    "Обнаружена аномалия"
                ),
                "new",
                datetime.now(timezone.utc).isoformat()
            )
        )

        if cur.rowcount == 0:
            logger.info(
                "Повторное событие пропущено: measurement=%s",
                event["measurement_id"]
            )
            return

        alert_id = cur.lastrowid
        c.commit()

    finally:
        c.close()

    payload = {
        "alert_id": alert_id,
        **event
    }

    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.post(
            os.getenv(
                "NOTIFICATION_URL",
                "http://notification-mock:8000"
            ) + "/internal/v1/notifications",
            json=payload
        )

        response.raise_for_status()

    logger.warning(
        "Создан alert id=%s measurement=%s",
        alert_id,
        event["measurement_id"]
    )


@asynccontextmanager
async def lifespan(app):
    c = conn()

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            well_id INTEGER,
            measurement_id INTEGER UNIQUE,
            severity TEXT,
            score REAL,
            description TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )

    c.commit()
    c.close()

    task = asyncio.create_task(
        consume(
            "diagnostics.completed",
            handle_diagnosis
        )
    )

    logger.info(
        "Alert DB ready; RabbitMQ consumer started"
    )

    yield

    task.cancel()

    await asyncio.gather(
        task,
        return_exceptions=True
    )


app = FastAPI(
    title="Alert Service",
    version="2.0.0",
    lifespan=lifespan
)

install_request_logging(app, logger)
install_problem_handlers(app, logger)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "alert"
    }


@app.get("/api/v1/alerts")
async def list_alerts():
    c = conn()

    rows = c.execute(
        "SELECT * FROM alerts ORDER BY id DESC"
    ).fetchall()

    c.close()

    return [
        dict(row)
        for row in rows
    ]


@app.patch("/api/v1/alerts/{alert_id}")
async def update_alert(alert_id: int, payload: dict):
    if payload.get("status") not in {
        "new",
        "in_progress",
        "resolved",
        "dismissed"
    }:
        raise HTTPException(
            422,
            detail="Недопустимый статус"
        )

    c = conn()

    cur = c.execute(
        "UPDATE alerts SET status=? WHERE id=?",
        (
            payload["status"],
            alert_id
        )
    )

    c.commit()
    updated = cur.rowcount > 0
    c.close()

    if not updated:
        raise HTTPException(
            404,
            detail="Алерт не найден"
        )

    return {
        "id": alert_id,
        "status": payload["status"]
    }
