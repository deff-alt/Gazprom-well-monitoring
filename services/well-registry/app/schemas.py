from datetime import datetime
from pydantic import BaseModel
from app.models import WellType, WellStatus

class LocalityOut(BaseModel):
    id: int
    name: str
    region: str
    class Config:
        from_attributes = True

class PromyselOut(BaseModel):
    id: int
    name: str
    region: str | None = None
    class Config:
        from_attributes = True

class WellOut(BaseModel):
    id: int
    well_number: str
    locality_id: int
    locality_name: str | None = None
    promysel_id: int | None = None
    promysel_name: str | None = None
    type: WellType
    status: WellStatus
    depth: float | None = None
    reservoir_pressure: float | None = None
    temperature: float | None = None
    latitude: float | None = None
    longitude: float | None = None