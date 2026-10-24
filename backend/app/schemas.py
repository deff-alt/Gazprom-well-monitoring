from datetime import date
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
    region: str | None = Field(default=None, max_length=255)


class PromyselUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    region: str | None = Field(default=None, max_length=255)


class PromyselOut(BaseModel):
    id: int
    name: str
    region: str | None = None

    class Config:
        from_attributes = True

# ============ МЕСТОРОЖДЕНИЯ ============

class LocalityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    region: str = Field(min_length=1, max_length=255)


class LocalityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    region: str | None = Field(default=None, min_length=1, max_length=255)


class LocalityOut(BaseModel):
    id: int
    name: str
    region: str

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