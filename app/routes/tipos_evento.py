
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_db
from app.utils.security import validateadmin, validateuser
from app.models.tipo_evento_model import TipoEventoCreate, TipoEventoDB

router = APIRouter(prefix="/api/tipos-evento", tags=["Tipos de Evento"])

def _str_id(doc: dict):
    d = dict(doc)
    d["_id"] = str(d["_id"])
    return d

@router.get("/", summary="Listar Tipos Evento")
async def listar(db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    cur = db["tipos_evento"].find({})
    return [_str_id(x) async for x in cur]

@router.post("/", summary="Crear Tipo Evento", response_model=TipoEventoDB, status_code=201)
async def crear(payload: TipoEventoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    if await db["tipos_evento"].find_one({"nombre": payload.nombre}):
        raise HTTPException(status_code=400, detail="Nombre ya existe")
    res = await db["tipos_evento"].insert_one(payload.model_dump())
    doc = await db["tipos_evento"].find_one({"_id": res.inserted_id})
    return _str_id(doc)

@router.get("/{id}", summary="Obtener Tipo Evento", response_model=TipoEventoDB)
async def obtener(id: str, db: AsyncIOMotorDatabase = Depends(get_db), user: dict = Depends(validateuser)):
    doc = await db["tipos_evento"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.put("/{id}", summary="Actualizar Tipo Evento", response_model=TipoEventoDB)
async def actualizar(id: str, payload: TipoEventoCreate, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    await db["tipos_evento"].update_one({"_id": ObjectId(id)}, {"$set": payload.model_dump()})
    doc = await db["tipos_evento"].find_one({"_id": ObjectId(id)})
    if not doc: raise HTTPException(status_code=404, detail="No encontrado")
    return _str_id(doc)

@router.delete("/{id}", summary="Eliminar Tipo Evento", status_code=204)
async def eliminar(id: str, db: AsyncIOMotorDatabase = Depends(get_db), admin: dict = Depends(validateadmin)):
    existe = await db["eventos"].find_one({"evento_id": ObjectId(id)})
    if existe:
        raise HTTPException(status_code=400, detail="No se puede eliminar: hay eventos asociados")
    res = await db["tipos_evento"].delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No encontrado")
    return
