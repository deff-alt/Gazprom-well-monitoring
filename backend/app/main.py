from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import User, Role
from app.security import hash_password
from app.routers import auth, promysels, localities, wells, users
from sqlalchemy import select

async def seed_admin():
    async with SessionLocal() as db:
        exists = (await db.execute(select(User).where(User.username == "admin"))).scalar_one_or_none()
        if not exists:
            db.add(User(
                username="admin",
                full_name="Администратор",
                hashed_password=hash_password("admin123"),
                role=Role.ADMIN,
            ))
            await db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_admin()
    yield

app = FastAPI(title="Well Monitor API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(promysels.router)
app.include_router(localities.router)
app.include_router(users.router)
app.include_router(wells.router)

@app.get("/health")
async def health():
    return {"status": "ok"}