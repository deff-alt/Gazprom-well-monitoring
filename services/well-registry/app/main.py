from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from app.logging_config import configure_logging
from app.request_logging import install_request_logging
from app.errors import install_problem_handlers
from app.db import engine,Base,SessionLocal
from app.models import Locality,Promysel,Well,WellType,WellStatus
from app.routers import wells as wells_router
logger=configure_logging("well-registry")
async def seed():
 async with SessionLocal() as db:
  loc=(await db.execute(select(Locality).where(Locality.name=="Северное"))).scalar_one_or_none()
  if not loc: loc=Locality(name="Северное",region="Краснодарский край");db.add(loc);await db.flush()
  prom=(await db.execute(select(Promysel).where(Promysel.name=="Краснодарский промысел"))).scalar_one_or_none()
  if not prom: prom=Promysel(name="Краснодарский промысел",region="Краснодарский край");db.add(prom);await db.flush()
  for num,lat,lng,depth,rp,temp in [("142",45.234567,38.975432,2850,18.5,67),("89",45.189012,39.034567,2900,19.2,68),("217",45.345678,38.890123,2650,20.1,66.5)]:
   exists=(await db.execute(select(Well).where(Well.well_number==num))).scalar_one_or_none()
   if not exists: db.add(Well(well_number=num,locality_id=loc.id,promysel_id=prom.id,type=WellType.PRODUCTION,status=WellStatus.ACTIVE,depth=depth,reservoir_pressure=rp,temperature=temp,latitude=lat,longitude=lng))
  await db.commit()
@asynccontextmanager
async def lifespan(app:FastAPI):
 logger.info("Запуск well-registry")
 async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
 await seed();logger.info("База и начальные данные готовы");yield;logger.info("Остановка well-registry")
app=FastAPI(title="Well Registry Service",version="2.0.0",lifespan=lifespan);install_request_logging(app,logger);install_problem_handlers(app,logger)
@app.get("/health")
async def health(): return {"status":"ok","service":"well-registry"}
app.include_router(wells_router.router)
