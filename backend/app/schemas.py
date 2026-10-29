from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models import Role, WellType, WellStatus

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: Role
    promysel_id: int | None = None

    class Config:
        from_attributes = True
# ============ ПРОМЫСЛЫ ============

class PromyselCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str | None = Field(default=None, max_length=32)
    region: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)


class PromyselUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = None
    region: str | None = None
    address: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class PromyselOut(BaseModel):
    id: int
    name: str
    code: str | None = None
    region: str | None = None
    address: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    class Config:
        from_attributes = True
# ============ МЕСТОРОЖДЕНИЯ ============

class LocalityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    region: str = Field(min_length=1, max_length=255)
    field_type: str | None = Field(default=None, max_length=64)
    discovery_year: int | None = Field(default=None, ge=1800, le=2100)
    area_km2: Decimal | None = None
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)


class LocalityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    region: str | None = Field(default=None, min_length=1, max_length=255)
    field_type: str | None = None
    discovery_year: int | None = None
    area_km2: Decimal | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


class LocalityOut(BaseModel):
    id: int
    name: str
    region: str
    field_type: str | None = None
    discovery_year: int | None = None
    area_km2: Decimal | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    class Config:
        from_attributes = True

# ============ СКВАЖИНЫ ============


class WellCreate(BaseModel):
    well_number: str = Field(min_length=1, max_length=50)
    locality_id: int
    promysel_id: int | None = None
    type: WellType
    status: WellStatus = WellStatus.ACTIVE
    location: str | None = Field(default=None, max_length=255)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    depth: Decimal | None = None
    hanger_diameter: Decimal | None = None
    drilling_start_date: date | None = None
    drilling_end_date: date | None = None
    commissioning_date: date | None = None
    inventory_number: str | None = Field(default=None, max_length=100)
    reservoir_pressure: Decimal | None = None
    buffer_pressure: Decimal | None = None
    casing_pressure: Decimal | None = None
    temperature: Decimal | None = None
    choke_diameter: Decimal | None = None
    planned_lifetime: int | None = None


class WellUpdate(BaseModel):
    locality_id: int | None = None
    promysel_id: int | None = None
    type: WellType | None = None
    status: WellStatus | None = None
    location: str | None = Field(default=None, max_length=255)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    depth: Decimal | None = None
    hanger_diameter: Decimal | None = None
    drilling_start_date: date | None = None
    drilling_end_date: date | None = None
    commissioning_date: date | None = None
    inventory_number: str | None = Field(default=None, max_length=100)
    reservoir_pressure: Decimal | None = None
    buffer_pressure: Decimal | None = None
    casing_pressure: Decimal | None = None
    temperature: Decimal | None = None
    choke_diameter: Decimal | None = None
    planned_lifetime: int | None = None


class WellOut(BaseModel):
    id: int
    well_number: str
    locality_id: int
    locality_name: str
    promysel_id: int | None = None
    promysel_name: str | None = None
    type: WellType
    status: WellStatus
    location: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    depth: Decimal | None = None
    hanger_diameter: Decimal | None = None
    drilling_start_date: date | None = None
    drilling_end_date: date | None = None
    commissioning_date: date | None = None
    inventory_number: str | None = None
    reservoir_pressure: Decimal | None = None
    buffer_pressure: Decimal | None = None
    casing_pressure: Decimal | None = None
    temperature: Decimal | None = None
    choke_diameter: Decimal | None = None
    planned_lifetime: int | None = None

    class Config:
        from_attributes = True

# ============ ПОЛЬЗОВАТЕЛИ (админ-панель) ============

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    full_name: str = Field(default='', max_length=128)
    password: str = Field(min_length=6, max_length=128)
    role: Role
    promysel_id: int | None = None


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=128)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    role: Role | None = None
    promysel_id: int | None = None
    is_active: bool | None = None


class UserAdminOut(BaseModel):
    id: int
    username: str
    full_name: str
    role: Role
    promysel_id: int | None = None
    promysel_name: str | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True