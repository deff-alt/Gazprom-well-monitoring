from pydantic import BaseModel, ConfigDict, Field
from app.models import WellType, WellStatus
class LocalityOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; name:str; region:str
class PromyselOut(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; name:str; region:str|None=None
class WellCreate(BaseModel):
    well_number:str=Field(min_length=1,max_length=50,pattern=r"^[A-Za-zА-Яа-я0-9_-]+$")
    locality_id:int=Field(gt=0); promysel_id:int|None=None
    type:WellType=WellType.PRODUCTION; status:WellStatus=WellStatus.ACTIVE
    depth:float|None=Field(default=None,gt=0); reservoir_pressure:float|None=Field(default=None,ge=0)
    temperature:float|None=None; latitude:float|None=Field(default=None,ge=-90,le=90)
    longitude:float|None=Field(default=None,ge=-180,le=180)
class WellUpdate(BaseModel):
    well_number:str|None=Field(default=None,min_length=1,max_length=50)
    locality_id:int|None=Field(default=None,gt=0); promysel_id:int|None=None
    type:WellType|None=None; status:WellStatus|None=None
    depth:float|None=Field(default=None,gt=0); reservoir_pressure:float|None=Field(default=None,ge=0)
    temperature:float|None=None; latitude:float|None=Field(default=None,ge=-90,le=90)
    longitude:float|None=Field(default=None,ge=-180,le=180)
class WellOut(BaseModel):
    id:int; well_number:str; locality_id:int; locality_name:str|None=None
    promysel_id:int|None=None; promysel_name:str|None=None; type:WellType; status:WellStatus
    depth:float|None=None; reservoir_pressure:float|None=None; temperature:float|None=None
    latitude:float|None=None; longitude:float|None=None
