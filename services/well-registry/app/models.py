import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Float, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
class WellType(str, enum.Enum):
    PRODUCTION = "Добывающая"
    INJECTION = "Нагнетательная"
    EXPLORATION = "Разведочная"
class WellStatus(str, enum.Enum):
    ACTIVE="active"; IN_REPAIR="in_repair"; SUSPENDED="suspended"; PLUGGED="plugged"
class Locality(Base):
    __tablename__="localities"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(255),unique=True)
    region: Mapped[str]=mapped_column(String(255))
    wells: Mapped[list["Well"]]=relationship(back_populates="locality")
class Promysel(Base):
    __tablename__="promysels"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(255),unique=True)
    region: Mapped[str|None]=mapped_column(String(255))
    wells: Mapped[list["Well"]]=relationship(back_populates="promysel")
class Well(Base):
    __tablename__="wells"
    id: Mapped[int]=mapped_column(primary_key=True)
    well_number: Mapped[str]=mapped_column(String(50),unique=True,index=True)
    locality_id: Mapped[int]=mapped_column(ForeignKey("localities.id"))
    promysel_id: Mapped[int|None]=mapped_column(ForeignKey("promysels.id"),nullable=True)
    type: Mapped[WellType]=mapped_column(default=WellType.PRODUCTION)
    status: Mapped[WellStatus]=mapped_column(default=WellStatus.ACTIVE)
    depth: Mapped[float|None]=mapped_column(Float,nullable=True)
    reservoir_pressure: Mapped[float|None]=mapped_column(Float,nullable=True)
    temperature: Mapped[float|None]=mapped_column(Float,nullable=True)
    latitude: Mapped[float|None]=mapped_column(Float,nullable=True)
    longitude: Mapped[float|None]=mapped_column(Float,nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    locality: Mapped["Locality"]=relationship(back_populates="wells")
    promysel: Mapped["Promysel|None"]=relationship(back_populates="wells")
class IdempotencyRecord(Base):
    __tablename__="idempotency_records"
    key: Mapped[str]=mapped_column(String(128),primary_key=True)
    request_hash: Mapped[str]=mapped_column(String(64))
    response_json: Mapped[str]=mapped_column(Text)
    status_code: Mapped[int]=mapped_column(default=201)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
