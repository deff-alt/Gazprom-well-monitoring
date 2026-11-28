import os,sqlite3,json,logging,asyncio,uuid
from contextlib import asynccontextmanager
from datetime import datetime,timezone
from fastapi import FastAPI,HTTPException,Header,Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from app.logging_config import configure_logging
from app.request_logging import install_request_logging
from app.errors import install_problem_handlers
try: import aio_pika
except ImportError: aio_pika=None
logger=configure_logging("ml-diagnostics")
DB=os.getenv("DB_PATH","/data/ml-diagnostics.db")
RABBIT=os.getenv("RABBITMQ_URL","amqp://guest:guest@rabbitmq:5672/")
def conn():
 os.makedirs(os.path.dirname(DB) or ".",exist_ok=True);c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
async def publish(routing,payload):
 if not aio_pika: logger.warning("aio-pika недоступен; событие не опубликовано");return
 try:
  connection=await aio_pika.connect_robust(RABBIT)
  async with connection:
   channel=await connection.channel();exchange=await channel.declare_exchange("well_monitor.events",aio_pika.ExchangeType.TOPIC,durable=True)
   await exchange.publish(aio_pika.Message(json.dumps(payload,ensure_ascii=False).encode(),delivery_mode=aio_pika.DeliveryMode.PERSISTENT,content_type="application/json"),routing_key=routing)
  logger.info("Опубликовано событие %s",routing)
 except Exception: logger.exception("Ошибка публикации %s",routing);raise
async def consume(binding,callback):
 if not aio_pika:return
 while True:
  try:
   connection=await aio_pika.connect_robust(RABBIT)
   async with connection:
    channel=await connection.channel();await channel.set_qos(prefetch_count=10)
    ex=await channel.declare_exchange("well_monitor.events",aio_pika.ExchangeType.TOPIC,durable=True)
    q=await channel.declare_queue(binding.replace(".","_"),durable=True);await q.bind(ex,routing_key=binding)
    async with q.iterator() as it:
     async for msg in it:
      async with msg.process(): await callback(json.loads(msg.body))
  except asyncio.CancelledError: raise
  except Exception: logger.exception("Consumer %s перезапускается",binding);await asyncio.sleep(3)

import httpx
class Analyze(BaseModel):measurement_id:int=Field(gt=0)
async def handle_telemetry_event(event):
 result=await calculate(int(event["id"]))
 await publish("diagnostics.completed",result)
 logger.info("Асинхронно обработано измерение id=%s",event["id"])
@asynccontextmanager
async def lifespan(app):
 c=conn();c.execute("CREATE TABLE IF NOT EXISTS diagnoses(id INTEGER PRIMARY KEY AUTOINCREMENT,measurement_id INTEGER UNIQUE,score REAL,severity TEXT,result TEXT,created_at TEXT)");c.commit();c.close();task=asyncio.create_task(consume("telemetry.received",handle_telemetry_event));logger.info("Diagnostics DB ready; telemetry consumer started");yield;task.cancel();await asyncio.gather(task,return_exceptions=True)
app=FastAPI(title="ML Diagnostics Service",version="2.0.0",lifespan=lifespan);install_request_logging(app,logger);install_problem_handlers(app,logger)
@app.get("/health")
async def health():return {"status":"ok","service":"ml-diagnostics"}
async def calculate(mid):
 async with httpx.AsyncClient(timeout=5) as client:
  r=await client.get(os.getenv("TELEMETRY_URL","http://telemetry:8000")+f"/api/v1/telemetry/{mid}");r.raise_for_status();m=r.json()
 score=0.0
 if m["pressure"]<12:score+=0.45
 if m["temperature"]>85:score+=0.3
 if m["vibration"]>7:score+=0.35
 if m["flow_rate"]<10:score+=0.2
 score=min(score,1.0);severity="critical" if score>=0.7 else "warning" if score>=0.35 else "info"
 result={"measurement_id":mid,"well_id":m["well_id"],"anomaly_score":round(score,3),"severity":severity,"anomaly":score>=0.35,"recommendation":"Проверить режим работы скважины" if score>=0.35 else "Параметры в пределах контрольных значений"}
 c=conn();c.execute("INSERT OR IGNORE INTO diagnoses(measurement_id,score,severity,result,created_at) VALUES(?,?,?,?,?)",(mid,score,severity,json.dumps(result,ensure_ascii=False),datetime.now(timezone.utc).isoformat()));c.commit();c.close();return result
@app.post("/api/v1/predict")
@app.post("/internal/v1/diagnose")
async def predict(p:Analyze):
 result=await calculate(p.measurement_id);await publish("diagnostics.completed",result);return result
@app.get("/api/v1/diagnoses")
async def diagnoses():
 c=conn();rows=c.execute("SELECT result FROM diagnoses ORDER BY id DESC").fetchall();c.close();return [json.loads(x[0]) for x in rows]
