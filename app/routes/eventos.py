
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_db
from app.utils.security import validateadmin, validateuser
from app.models.evento_model import EventoCreate, EventoDB

router = APIRouter(prefix="/api/eventos", tags=["Eventos"])

def _str_id(doc: dict):
    d = dict(doc)
    d["_id"] = str(d["_id"])
    for k in ("jugador_id", "partido_id", "evento_id"):
        if k in d and isinstance(d[k], ObjectId):
            d[k] = str(d[k])
    return d

@router.get("/", summary="Listar Eventos")
async def listar(db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    cur = db["eventos"].find({})
    return [_str_id(x) async for x in cur]

@router.post("/", summary="Crear Evento", response_model=EventoDB, status_code=201)
async def crear(payload: EventoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    # validar referencias
    refs = {
        "jugador_id": ("jugadores", payload.jugador_id),
        "partido_id": ("partidos", payload.partido_id),
        "evento_id": ("tipos_evento", payload.evento_id),
    }
    for campo, (coll, value) in refs.items():
        if not await db[coll].find_one({"_id": ObjectId(value)}):
            raise HTTPException(status_code=400, detail=f"{campo} no existe")
    data = payload.model_dump()
    for k in ("jugador_id", "partido_id", "evento_id"):
        data[k] = ObjectId(data[k])
    res = await db["eventos"].insert_one(data)
    doc = await db["eventos"].find_one({"_id": res.inserted_id})
    return _str_id(doc)

@router.get("/{id}", summary="Obtener Evento", response_model=EventoDB)
async def obtener(id: str, db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    doc = await db["eventos"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.put("/{id}", summary="Actualizar Evento", response_model=EventoDB)
async def actualizar(id: str, payload: EventoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    refs = {
        "jugador_id": ("jugadores", payload.jugador_id),
        "partido_id": ("partidos", payload.partido_id),
        "evento_id": ("tipos_evento", payload.evento_id),
    }
    for campo, (coll, value) in refs.items():
        if not await db[coll].find_one({"_id": ObjectId(value)}):
            raise HTTPException(status_code=400, detail=f"{campo} no existe")
    data = payload.model_dump()
    for k in ("jugador_id", "partido_id", "evento_id"):
        data[k] = ObjectId(data[k])
    await db["eventos"].update_one({"_id": ObjectId(id)}, {"$set": data})
    doc = await db["eventos"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.delete("/{id}", summary="Eliminar Evento", status_code=204)
async def eliminar(id: str, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    res = await db["eventos"].delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
    return
