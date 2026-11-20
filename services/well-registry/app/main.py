import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import select
from app.db import engine, Base, SessionLocal
from app.models import Locality, Promysel, Well, WellType, WellStatus
from app.routers import wells as wells_router

async def seed():
    """Засеваем 1 месторождение, 1 промысел, 3 скважины (по номерам из монолита)."""
    async with SessionLocal() as db:
        loc = (await db.execute(select(Locality).where(Locality.name == "Северное"))).scalar_one_or_none()
        if not loc:
            loc = Locality(name="Северное", region="Краснодарский край")
            db.add(loc)
            await db.flush()

        prom = (await db.execute(select(Promysel).where(Promysel.name == "Краснодарский промысел"))).scalar_one_or_none()
        if not prom:
            prom = Promysel(name="Краснодарский промысел", region="Краснодарский край")
            db.add(prom)
            await db.flush()

        seeds = [
            ("142", 45.234567, 38.975432, 2850.0, 18.5, 67.0),
            ("89",  45.189012, 39.034567, 2900.0, 19.2, 68.0),
            ("217", 45.345678, 38.890123, 2650.0, 20.1, 66.5),
        ]
        for num, lat, lng, depth, rp, temp in seeds:
            exists = (await db.execute(select(Well).where(Well.well_number == num))).scalar_one_or_none()
            if not exists:
                db.add(Well(
                    well_number=num,
                    locality_id=loc.id, promysel_id=prom.id,
                    type=WellType.PRODUCTION, status=WellStatus.ACTIVE,
                    depth=depth, reservoir_pressure=rp, temperature=temp,
                    latitude=lat, longitude=lng,
                ))
        await db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed()
    yield

app = FastAPI(title="well-registry-service", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "well-registry"}

app.include_router(wells_router.router)