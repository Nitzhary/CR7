
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_db
from app.utils.security import validateadmin, validateuser
from app.models.torneo_model import TorneoCreate, TorneoDB

router = APIRouter(prefix="/api/torneos", tags=["Torneos"])

def _str_id(doc: dict):
    d = dict(doc)
    d["_id"] = str(d["_id"])
    d["tipo_torneo_id"] = str(d["tipo_torneo_id"]) if "tipo_torneo_id" in d else None
    return d

@router.get("/", summary="Listar Torneos")
async def listar(db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    cur = db["torneos"].find({})
    out = []
    async for x in cur:
        out.append(_str_id(x))
    return out

@router.post("/", summary="Crear Torneo", response_model=TorneoDB, status_code=201)
async def crear(payload: TorneoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    # validar referencia
    if not await db["tipos_torneo"].find_one({"_id": ObjectId(payload.tipo_torneo_id)}):
        raise HTTPException(status_code=400, detail="tipo_torneo_id no existe")
    data = payload.model_dump()
    data["tipo_torneo_id"] = ObjectId(data["tipo_torneo_id"])
    res = await db["torneos"].insert_one(data)
    doc = await db["torneos"].find_one({"_id": res.inserted_id})
    return _str_id(doc)

@router.get("/{id}", summary="Obtener Torneo", response_model=TorneoDB)
async def obtener(id: str, db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    doc = await db["torneos"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.put("/{id}", summary="Actualizar Torneo", response_model=TorneoDB)
async def actualizar(id: str, payload: TorneoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    if not await db["tipos_torneo"].find_one({"_id": ObjectId(payload.tipo_torneo_id)}):
        raise HTTPException(status_code=400, detail="tipo_torneo_id no existe")
    data = payload.model_dump()
    data["tipo_torneo_id"] = ObjectId(data["tipo_torneo_id"])
    await db["torneos"].update_one({"_id": ObjectId(id)}, {"$set": data})
    doc = await db["torneos"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.delete("/{id}", summary="Eliminar Torneo", status_code=204)
async def eliminar(id: str, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    # Regla opcional: no eliminar si hay equipos/partidos asociados
    if await db["equipos"].find_one({"torneo_id": ObjectId(id)}) or await db["partidos"].find_one({"torneo_id": ObjectId(id)}):
        raise HTTPException(status_code=400, detail="No se puede eliminar: tiene registros asociados")
    res = await db["torneos"].delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
    return
