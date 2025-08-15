
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_db
from app.utils.security import validateadmin, validateuser
from app.models.tipo_torneo_model import TipoTorneoCreate, TipoTorneoDB

router = APIRouter(prefix="/api/tipos-torneo", tags=["Tipos de Torneo"])

def _str_id(doc: dict):
    d = dict(doc)
    d["_id"] = str(d["_id"])
    return d

@router.get("/", summary="Listar Tipos Torneo")
async def listar(_, db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    cur = db["tipos_torneo"].find({})
    return [_str_id(x) async for x in cur]

@router.post("/", summary="Crear Tipo Torneo", response_model=TipoTorneoDB, status_code=201)
async def crear(payload: TipoTorneoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    if await db["tipos_torneo"].find_one({"nombre": payload.nombre}):
        raise HTTPException(status_code=400, detail="Nombre ya existe")
    res = await db["tipos_torneo"].insert_one(payload.model_dump())
    doc = await db["tipos_torneo"].find_one({"_id": res.inserted_id})
    return _str_id(doc)

@router.get("/{id}", summary="Obtener Tipo Torneo", response_model=TipoTorneoDB)
async def obtener(id: str, db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    doc = await db["tipos_torneo"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.put("/{id}", summary="Actualizar Tipo Torneo", response_model=TipoTorneoDB)
async def actualizar(id: str, payload: TipoTorneoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    await db["tipos_torneo"].update_one({"_id": ObjectId(id)}, {"$set": payload.model_dump()})
    doc = await db["tipos_torneo"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.delete("/{id}", summary="Eliminar Tipo Torneo", status_code=204)
async def eliminar(id: str, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    # Regla: no eliminar si hay torneos asociados
    existe = await db["torneos"].find_one({"tipo_torneo_id": ObjectId(id)})
    if existe:
        raise HTTPException(status_code=400, detail="No se puede eliminar: tiene torneos asociados")
    res = await db["tipos_torneo"].delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
    return
