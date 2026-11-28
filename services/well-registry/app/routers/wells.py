import hashlib,json,logging
from fastapi import APIRouter,Depends,HTTPException,Header,status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Well,Locality,Promysel,IdempotencyRecord
from app.schemas import WellOut,WellCreate,WellUpdate,LocalityOut,PromyselOut
router=APIRouter(tags=["wells"]); log=logging.getLogger("well-registry")
def out(w): return WellOut(id=w.id,well_number=w.well_number,locality_id=w.locality_id,locality_name=w.locality.name if w.locality else None,promysel_id=w.promysel_id,promysel_name=w.promysel.name if w.promysel else None,type=w.type,status=w.status,depth=w.depth,reservoir_pressure=w.reservoir_pressure,temperature=w.temperature,latitude=w.latitude,longitude=w.longitude)
async def load(db,wid):
 w=(await db.execute(select(Well).options(selectinload(Well.locality),selectinload(Well.promysel)).where(Well.id==wid))).scalar_one_or_none()
 if not w: raise HTTPException(404,detail="Скважина не найдена")
 return w
@router.get("/api/v1/wells",response_model=list[WellOut])
async def list_wells(db:AsyncSession=Depends(get_db)):
 rows=(await db.execute(select(Well).options(selectinload(Well.locality),selectinload(Well.promysel)))).scalars().all();return [out(x) for x in rows]
@router.post("/api/v1/wells",response_model=WellOut,status_code=201)
async def create_well(payload:WellCreate, idempotency_key:str=Header(...,alias="Idempotency-Key",min_length=8,max_length=128),db:AsyncSession=Depends(get_db)):
 data=payload.model_dump(mode="json"); digest=hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
 old=await db.get(IdempotencyRecord,idempotency_key)
 if old:
  if old.request_hash!=digest: raise HTTPException(409,detail="Idempotency-Key уже использован с другим телом запроса")
  return WellOut.model_validate_json(old.response_json)
 if (await db.execute(select(Well).where(Well.well_number==payload.well_number))).scalar_one_or_none(): raise HTTPException(409,detail="Скважина с таким номером уже существует")
 if not await db.get(Locality,payload.locality_id): raise HTTPException(422,detail="Указанное месторождение не найдено")
 if payload.promysel_id and not await db.get(Promysel,payload.promysel_id): raise HTTPException(422,detail="Указанный промысел не найден")
 w=Well(**payload.model_dump());db.add(w);await db.flush();w=await load(db,w.id); result=out(w);db.add(IdempotencyRecord(key=idempotency_key,request_hash=digest,response_json=result.model_dump_json(),status_code=201));await db.commit();log.info("Создана скважина id=%s number=%s",w.id,w.well_number);return result
@router.get("/api/v1/wells/{well_id}",response_model=WellOut)
async def get_well(well_id:int,db:AsyncSession=Depends(get_db)): return out(await load(db,well_id))
@router.put("/api/v1/wells/{well_id}",response_model=WellOut)
async def update_well(well_id:int,payload:WellUpdate,db:AsyncSession=Depends(get_db)):
 w=await load(db,well_id);data=payload.model_dump(exclude_unset=True)
 if "locality_id" in data and not await db.get(Locality,data["locality_id"]): raise HTTPException(422,detail="Месторождение не найдено")
 if data.get("promysel_id") and not await db.get(Promysel,data["promysel_id"]): raise HTTPException(422,detail="Промысел не найден")
 if data.get("well_number") and data["well_number"]!=w.well_number and (await db.execute(select(Well).where(Well.well_number==data["well_number"]))).scalar_one_or_none(): raise HTTPException(409,detail="Номер скважины уже занят")
 for k,v in data.items(): setattr(w,k,v)
 await db.flush();w=await load(db,w.id);result=out(w);await db.commit();log.info("Обновлена скважина id=%s",well_id);return result
@router.delete("/api/v1/wells/{well_id}",status_code=204)
async def delete_well(well_id:int,db:AsyncSession=Depends(get_db)):
 w=await load(db,well_id);await db.delete(w);await db.commit();log.info("Удалена скважина id=%s",well_id);return None
@router.get("/api/v1/localities",response_model=list[LocalityOut])
async def list_localities(db:AsyncSession=Depends(get_db)): return (await db.execute(select(Locality))).scalars().all()
@router.get("/api/v1/promysels",response_model=list[PromyselOut])
async def list_promysels(db:AsyncSession=Depends(get_db)): return (await db.execute(select(Promysel))).scalars().all()
@router.get("/internal/v1/wells/{well_id}",response_model=WellOut)
async def get_well_internal(well_id:int,db:AsyncSession=Depends(get_db)): return out(await load(db,well_id))
