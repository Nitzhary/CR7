
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_db
from app.utils.security import validateadmin, validateuser
from app.models.partido_model import PartidoCreate, PartidoDB

router = APIRouter(prefix="/api/partidos", tags=["Partidos"])

def _str_id(doc: dict):
    d = dict(doc)
    d["_id"] = str(d["_id"])
    for k in ("torneo_id", "equipo_local_id", "equipo_visitante_id"):
        if k in d and isinstance(d[k], ObjectId):
            d[k] = str(d[k])
    return d

@router.get("/", summary="Listar Partidos")
async def listar(db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    cur = db["partidos"].find({})
    return [_str_id(x) async for x in cur]

@router.post("/", summary="Crear Partido", response_model=PartidoDB, status_code=201)
async def crear(payload: PartidoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    # validar referencias
    if not await db["torneos"].find_one({"_id": ObjectId(payload.torneo_id)}):
        raise HTTPException(status_code=400, detail="torneo_id no existe")
    for k in ("equipo_local_id", "equipo_visitante_id"):
        if not await db["equipos"].find_one({"_id": ObjectId(getattr(payload, k))}):
            raise HTTPException(status_code=400, detail=f"{k} no existe")
    data = payload.model_dump()
    data["torneo_id"] = ObjectId(data["torneo_id"])
    data["equipo_local_id"] = ObjectId(data["equipo_local_id"])
    data["equipo_visitante_id"] = ObjectId(data["equipo_visitante_id"])
    res = await db["partidos"].insert_one(data)
    doc = await db["partidos"].find_one({"_id": res.inserted_id})
    return _str_id(doc)

@router.get("/{id}", summary="Obtener Partido", response_model=PartidoDB)
async def obtener(id: str, db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    doc = await db["partidos"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.put("/{id}", summary="Actualizar Partido", response_model=PartidoDB)
async def actualizar(id: str, payload: PartidoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    if not await db["torneos"].find_one({"_id": ObjectId(payload.torneo_id)}):
        raise HTTPException(status_code=400, detail="torneo_id no existe")
    for k in ("equipo_local_id", "equipo_visitante_id"):
        if not await db["equipos"].find_one({"_id": ObjectId(getattr(payload, k))}):
            raise HTTPException(status_code=400, detail=f"{k} no existe")
    data = payload.model_dump()
    data["torneo_id"] = ObjectId(data["torneo_id"])
    data["equipo_local_id"] = ObjectId(data["equipo_local_id"])
    data["equipo_visitante_id"] = ObjectId(data["equipo_visitante_id"])
    await db["partidos"].update_one({"_id": ObjectId(id)}, {"$set": data})
    doc = await db["partidos"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.delete("/{id}", summary="Eliminar Partido", status_code=204)
async def eliminar(id: str, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    # Regla opcional: no eliminar si hay eventos
    if await db["eventos"].find_one({"partido_id": ObjectId(id)}):
        raise HTTPException(status_code=400, detail="No se puede eliminar: tiene eventos asociados")
    res = await db["partidos"].delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
    return
