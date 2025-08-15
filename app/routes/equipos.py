
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_db
from app.utils.security import validateadmin, validateuser
from app.models.equipo_model import EquipoCreate, EquipoDB

router = APIRouter(prefix="/api/equipos", tags=["Equipos"])

def _str_id(doc: dict):
    d = dict(doc)
    d["_id"] = str(d["_id"])
    if "torneo_id" in d and isinstance(d["torneo_id"], ObjectId):
        d["torneo_id"] = str(d["torneo_id"])
    return d

@router.get("/", summary="Listar Equipos (QueryString público)", tags=["Equipos", "QueryString"])
async def listar_publico(
    nombre: str | None = Query(None, description="Filtra por nombre (contiene)"),
    torneo_id: str | None = Query(None, description="Filtra por torneo_id"),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    # Endpoint de QueryString accesible **sin token** (requisito)
    filtro = {}
    if nombre:
        filtro["nombre"] = {"$regex": nombre, "$options": "i"}
    if torneo_id:
        try: filtro["torneo_id"] = ObjectId(torneo_id)
        except: raise HTTPException(status_code=400, detail="torneo_id inválido")

    cur = db["equipos"].find(filtro)
    return [_str_id(x) async for x in cur]

@router.post("/", summary="Crear Equipo", response_model=EquipoDB, status_code=201)
async def crear(payload: EquipoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    if not await db["torneos"].find_one({"_id": ObjectId(payload.torneo_id)}):
        raise HTTPException(status_code=400, detail="torneo_id no existe")
    data = payload.model_dump()
    data["torneo_id"] = ObjectId(data["torneo_id"])
    res = await db["equipos"].insert_one(data)
    doc = await db["equipos"].find_one({"_id": res.inserted_id})
    return _str_id(doc)

@router.get("/{id}", summary="Obtener Equipo", response_model=EquipoDB)
async def obtener(id: str, db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    doc = await db["equipos"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.put("/{id}", summary="Actualizar Equipo", response_model=EquipoDB)
async def actualizar(id: str, payload: EquipoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    if not await db["torneos"].find_one({"_id": ObjectId(payload.torneo_id)}):
        raise HTTPException(status_code=400, detail="torneo_id no existe")
    data = payload.model_dump()
    data["torneo_id"] = ObjectId(data["torneo_id"])
    await db["equipos"].update_one({"_id": ObjectId(id)}, {"$set": data})
    doc = await db["equipos"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.delete("/{id}", summary="Eliminar Equipo", status_code=204)
async def eliminar(id: str, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    # regla: no eliminar si tiene jugadores
    if await db["jugadores"].find_one({"equipo_id": ObjectId(id)}):
        raise HTTPException(status_code=400, detail="No se puede eliminar: tiene jugadores asociados")
    res = await db["equipos"].delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
    return
