import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    String, DateTime, Date, Enum, Boolean, ForeignKey,
    Numeric, Integer, Text, func, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


# ============ ENUMS ============

class Role(str, enum.Enum):
    ADMIN = "admin"
    ENGINEER = "engineer"
    HEAD = "head"
    OPERATOR = "operator"


class WellType(str, enum.Enum):
    PRODUCTION = "Добывающая"
    INJECTION = "Нагнетательная"
    EXPLORATION = "Разведочная"


class WellStatus(str, enum.Enum):
    ACTIVE = "active"
    IN_REPAIR = "in_repair"
    SUSPENDED = "suspended"
    PLUGGED = "plugged"


class WorkoverStatus(str, enum.Enum):
    PLANNED = "Запланирован"
    IN_PROGRESS = "В работе"
    COMPLETED = "Завершен"
    CANCELLED = "Отменен"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


# ============ ПРОМЫСЛЫ И ПОЛЬЗОВАТЕЛИ ============

class Promysel(Base):
    __tablename__ = "promysels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(32))
    region: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(255))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))

    wells: Mapped[list["Well"]] = relationship(back_populates="promysel")
    users: Mapped[list["User"]] = relationship(back_populates="promysel")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(128), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.OPERATOR)
    promysel_id: Mapped[int | None] = mapped_column(ForeignKey("promysels.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    promysel: Mapped["Promysel | None"] = relationship(back_populates="users")
    assigned_alerts: Mapped[list["Alert"]] = relationship(back_populates="assignee")


# ============ МЕСТОРОЖДЕНИЯ И СКВАЖИНЫ ============

class Locality(Base):
    __tablename__ = "localities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[str | None] = mapped_column(String(64))
    discovery_year: Mapped[int | None] = mapped_column(Integer)
    area_km2: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))

    wells: Mapped[list["Well"]] = relationship(back_populates="locality", cascade="all, delete-orphan")

class Well(Base):
    __tablename__ = "wells"

    id: Mapped[int] = mapped_column(primary_key=True)
    well_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    locality_id: Mapped[int] = mapped_column(ForeignKey("localities.id", ondelete="RESTRICT"), nullable=False)
    promysel_id: Mapped[int | None] = mapped_column(ForeignKey("promysels.id", ondelete="SET NULL"))

    type: Mapped[WellType] = mapped_column(Enum(WellType), nullable=False)
    status: Mapped[WellStatus] = mapped_column(Enum(WellStatus), default=WellStatus.ACTIVE)
    location: Mapped[str | None] = mapped_column(String(255))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))

    depth: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    hanger_diameter: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    drilling_start_date: Mapped[date | None] = mapped_column(Date)
    drilling_end_date: Mapped[date | None] = mapped_column(Date)
    commissioning_date: Mapped[date | None] = mapped_column(Date)
    inventory_number: Mapped[str | None] = mapped_column(String(100))

    reservoir_pressure: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    buffer_pressure: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    casing_pressure: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    temperature: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    choke_diameter: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    planned_lifetime: Mapped[int | None] = mapped_column(Integer)

    locality: Mapped["Locality"] = relationship(back_populates="wells")
    promysel: Mapped["Promysel | None"] = relationship(back_populates="wells")

    kg_expertises: Mapped[list["KgExpertise"]] = relationship(back_populates="well", cascade="all, delete-orphan")
    fa_expertises: Mapped[list["FaExpertise"]] = relationship(back_populates="well", cascade="all, delete-orphan")
    workovers: Mapped[list["Workover"]] = relationship(back_populates="well", cascade="all, delete-orphan")
    production_rates: Mapped[list["ProductionRate"]] = relationship(back_populates="well", cascade="all, delete-orphan")
    telemetry: Mapped[list["Telemetry"]] = relationship(back_populates="well", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="well", cascade="all, delete-orphan")


# ============ ЭКСПЕРТИЗЫ И РЕМОНТЫ (из курсовой) ============

class KgExpertise(Base):
    __tablename__ = "kg_expertises"

    id: Mapped[int] = mapped_column(primary_key=True)
    well_id: Mapped[int] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    executor_organization: Mapped[str] = mapped_column(String(255), nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    conclusion: Mapped[str | None] = mapped_column(Text)

    well: Mapped["Well"] = relationship(back_populates="kg_expertises")


class FaExpertise(Base):
    __tablename__ = "fa_expertises"

    id: Mapped[int] = mapped_column(primary_key=True)
    well_id: Mapped[int] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    executor_organization: Mapped[str] = mapped_column(String(255), nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    conclusion: Mapped[str | None] = mapped_column(Text)

    well: Mapped["Well"] = relationship(back_populates="fa_expertises")


class Workover(Base):
    __tablename__ = "workovers"

    id: Mapped[int] = mapped_column(primary_key=True)
    well_id: Mapped[int] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False)
    work_type: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date | None] = mapped_column(Date)
    actual_start_date: Mapped[date | None] = mapped_column(Date)
    actual_end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[WorkoverStatus] = mapped_column(Enum(WorkoverStatus), default=WorkoverStatus.PLANNED)

    well: Mapped["Well"] = relationship(back_populates="workovers")


# ============ ДЕБИТЫ (суточные замеры) ============

class ProductionRate(Base):
    __tablename__ = "production_rates"
    __table_args__ = (Index("ix_production_well_date", "well_id", "measure_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    well_id: Mapped[int] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False)
    measure_date: Mapped[date] = mapped_column(Date, nullable=False)
    daily_rate: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    comment: Mapped[str | None] = mapped_column(String(255))

    well: Mapped["Well"] = relationship(back_populates="production_rates")


# ============ ТЕЛЕМЕТРИЯ (высокочастотные данные) ============

class Telemetry(Base):
    __tablename__ = "telemetry"
    __table_args__ = (Index("ix_telemetry_well_time", "well_id", "ts"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    well_id: Mapped[int] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # До штуцерной камеры (устьевые параметры)
    pressure_before_choke: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    temperature_before_choke: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # После штуцерной камеры (параметры в выкидной линии)
    pressure_after_choke: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    temperature_after_choke: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Прочие параметры (для ML)
    bottomhole_pressure: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    flow_rate_gas: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    flow_rate_liquid: Mapped[Decimal | None] = mapped_column(Numeric(12, 3))
    water_cut: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    vibration: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))

    well: Mapped["Well"] = relationship(back_populates="telemetry")


# ============ АЛЕРТЫ (результаты работы ML) ============

class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (Index("ix_alerts_well_status", "well_id", "status"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    well_id: Mapped[int] = mapped_column(ForeignKey("wells.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    parameter: Mapped[str] = mapped_column(String(64), nullable=False)
    anomaly_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 4))
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity), default=AlertSeverity.WARNING)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.NEW)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    description: Mapped[str | None] = mapped_column(Text)
    resolution_comment: Mapped[str | None] = mapped_column(Text)

    well: Mapped["Well"] = relationship(back_populates="alerts")
    assignee: Mapped["User | None"] = relationship(back_populates="assigned_alerts")