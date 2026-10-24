import enum
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Role(str, enum.Enum):
    ADMIN = "admin"
    ENGINEER = "engineer"
    HEAD = "head"          # начальник промысла
    OPERATOR = "operator"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(128), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.OPERATOR)
    promysel_id: Mapped[int | None] = mapped_column(nullable=True)  # для head
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())