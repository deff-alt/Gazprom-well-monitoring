import os,sqlite3,json,logging,asyncio,uuid,hashlib
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
logger=configure_logging("telemetry")
DB=os.getenv("DB_PATH","/data/telemetry.db")
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
class Measurement(BaseModel): well_id:int=Field(gt=0);pressure:float=Field(ge=0);temperature:float;flow_rate:float=Field(ge=0);vibration:float=Field(ge=0)
@asynccontextmanager
async def lifespan(app):
 c=conn();c.execute("CREATE TABLE IF NOT EXISTS measurements(id INTEGER PRIMARY KEY AUTOINCREMENT,well_id INTEGER,pressure REAL,temperature REAL,flow_rate REAL,vibration REAL,created_at TEXT,idempotency_key TEXT UNIQUE,request_hash TEXT)")
 # Миграция существующей БД, созданной предыдущей версией сервиса.
 columns={row[1] for row in c.execute("PRAGMA table_info(measurements)").fetchall()}
 if "request_hash" not in columns:
  c.execute("ALTER TABLE measurements ADD COLUMN request_hash TEXT")
 # Заполняем хэш для записей, созданных до добавления проверки тела запроса.
 for legacy in c.execute("SELECT id,well_id,pressure,temperature,flow_rate,vibration FROM measurements WHERE request_hash IS NULL").fetchall():
  legacy_data={"well_id":legacy[1],"pressure":legacy[2],"temperature":legacy[3],"flow_rate":legacy[4],"vibration":legacy[5]}
  legacy_hash=hashlib.sha256(json.dumps(legacy_data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
  c.execute("UPDATE measurements SET request_hash=? WHERE id=?",(legacy_hash,legacy[0]))
 c.commit();c.close();logger.info("Telemetry DB ready");yield
app=FastAPI(title="Telemetry Service",version="2.0.0",lifespan=lifespan);install_request_logging(app,logger);install_problem_handlers(app,logger)
@app.get("/health")
async def health():return {"status":"ok","service":"telemetry"}
async def store(payload,key):
 async with httpx.AsyncClient(timeout=5) as client:
  r=await client.get(os.getenv("REGISTRY_URL","http://well-registry:8000")+f"/internal/v1/wells/{payload.well_id}")
  if r.status_code==404:raise HTTPException(404,detail="Скважина не найдена в реестре")
  r.raise_for_status()
 data=payload.model_dump(mode="json")
 digest=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()
 c=conn();old=c.execute("SELECT * FROM measurements WHERE idempotency_key=?",(key,)).fetchone()
 if old:
  c.close()
  if old["request_hash"] and old["request_hash"]!=digest:
   raise HTTPException(409,detail="Idempotency-Key уже использован с другим телом запроса")
  return dict(old),False
 now=datetime.now(timezone.utc).isoformat()
 try:
  cur=c.execute("INSERT INTO measurements(well_id,pressure,temperature,flow_rate,vibration,created_at,idempotency_key,request_hash) VALUES(?,?,?,?,?,?,?,?)",(payload.well_id,payload.pressure,payload.temperature,payload.flow_rate,payload.vibration,now,key,digest))
  c.commit();row=dict(c.execute("SELECT * FROM measurements WHERE id=?",(cur.lastrowid,)).fetchone())
 except sqlite3.IntegrityError:
  c.rollback();old=c.execute("SELECT * FROM measurements WHERE idempotency_key=?",(key,)).fetchone()
  if old and old["request_hash"]!=digest:
   c.close();raise HTTPException(409,detail="Idempotency-Key уже использован с другим телом запроса")
  if old:
   row=dict(old);c.close();return row,False
  c.close();raise
 c.close();return row,True
@app.post("/api/v1/telemetry",status_code=201)
async def ingest(p:Measurement,key:str=Header(...,alias="Idempotency-Key",min_length=8)):
 row,created=await store(p,key)
 if created: await publish("telemetry.received",row)
 return {**row,"replayed":not created}
@app.get("/api/v1/telemetry/{measurement_id}")
async def get_measurement(measurement_id:int):
 c=conn();r=c.execute("SELECT * FROM measurements WHERE id=?",(measurement_id,)).fetchone();c.close()
 if not r:raise HTTPException(404,detail="Измерение не найдено")
 return dict(r)
@app.delete("/internal/v1/telemetry/{measurement_id}",status_code=204)
async def compensate(measurement_id:int):
 c=conn();c.execute("DELETE FROM measurements WHERE id=?",(measurement_id,));c.commit();c.close();logger.warning("Компенсация: удалено измерение %s",measurement_id)
@app.post("/api/v1/workflows/diagnose")
async def diagnose_workflow(p:Measurement,key:str=Header(...,alias="Idempotency-Key",min_length=8)):
 row,created=await store(p,key)
 try:
  async with httpx.AsyncClient(timeout=8) as client:
   response=await client.post(os.getenv("ML_URL","http://ml-diagnostics:8000")+"/internal/v1/diagnose",json={"measurement_id":row["id"]})
   response.raise_for_status();diagnosis=response.json()
  await publish("workflow.completed",{"measurement_id":row["id"],"diagnosis":diagnosis})
  return {"status":"completed","measurement":row,"diagnosis":diagnosis}
 except Exception as exc:
  compensation_ok=True
  if created:
   try:
    async with httpx.AsyncClient(timeout=5) as client:
     rollback=await client.delete(f"http://localhost:8000/internal/v1/telemetry/{row['id']}")
     rollback.raise_for_status()
   except Exception:
    compensation_ok=False
    logger.exception("Не удалось удалить измерение при компенсации Saga: id=%s",row["id"])
  try:
   await publish("workflow.compensated",{"measurement_id":row["id"],"reason":str(exc),"compensation_succeeded":compensation_ok})
  except Exception:
   logger.exception("Не удалось опубликовать workflow.compensated для measurement_id=%s",row["id"])
  logger.exception("Saga завершилась ошибкой measurement_id=%s; compensation_ok=%s",row["id"],compensation_ok)
  if compensation_ok:
   raise HTTPException(502,detail="Диагностика не выполнена; операция компенсирована")
  raise HTTPException(502,detail="Диагностика не выполнена; автоматическая компенсация завершилась ошибкой")
