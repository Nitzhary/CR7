
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_db
from app.utils.security import validateadmin, validateuser
from app.models.jugador_model import JugadorCreate, JugadorDB

router = APIRouter(prefix="/api/jugadores", tags=["Jugadores"])

def _str_id(doc: dict):
    d = dict(doc)
    d["_id"] = str(d["_id"])
    if "equipo_id" in d and isinstance(d["equipo_id"], ObjectId):
        d["equipo_id"] = str(d["equipo_id"])
    return d

@router.get("/", summary="Listar Jugadores")
async def listar(db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    cur = db["jugadores"].find({})
    return [_str_id(x) async for x in cur]

@router.post("/", summary="Crear Jugador", response_model=JugadorDB, status_code=201)
async def crear(payload: JugadorCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    if not await db["equipos"].find_one({"_id": ObjectId(payload.equipo_id)}):
        raise HTTPException(status_code=400, detail="equipo_id no existe")
    data = payload.model_dump()
    data["equipo_id"] = ObjectId(data["equipo_id"])
    res = await db["jugadores"].insert_one(data)
    doc = await db["jugadores"].find_one({"_id": res.inserted_id})
    return _str_id(doc)

@router.get("/{id}", summary="Obtener Jugador", response_model=JugadorDB)
async def obtener(id: str, db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    doc = await db["jugadores"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.put("/{id}", summary="Actualizar Jugador", response_model=JugadorDB)
async def actualizar(id: str, payload: JugadorCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    if not await db["equipos"].find_one({"_id": ObjectId(payload.equipo_id)}):
        raise HTTPException(status_code=400, detail="equipo_id no existe")
    data = payload.model_dump()
    data["equipo_id"] = ObjectId(data["equipo_id"])
    await db["jugadores"].update_one({"_id": ObjectId(id)}, {"$set": data})
    doc = await db["jugadores"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.delete("/{id}", summary="Eliminar Jugador", status_code=204)
async def eliminar(id: str, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    res = await db["jugadores"].delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
    return
