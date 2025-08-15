
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.database import get_db
from app.utils.security import validateadmin

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

def _str_id(doc: dict):
    d = dict(doc)
    d["_id"] = str(d["_id"])
    return d

@router.get("/", summary="Listar usuarios (solo admin)")
async def listar_usuarios(admin: dict = Depends(validateadmin), db: AsyncIOMotorDatabase = Depends(get_db)):
    cur = db["users"].find({})
    return [_str_id(x) async for x in cur]

@router.patch("/{id}/activar", summary="Activar/Desactivar usuario (solo admin)")
async def activar_usuario(id: str, activo: bool, admin: dict = Depends(validateadmin), db: AsyncIOMotorDatabase = Depends(get_db)):
    res = await db["users"].update_one({"_id": ObjectId(id)}, {"$set": {"active": activo}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"updated": True, "active": activo}

@router.patch("/{id}/rol", summary="Cambiar rol de usuario (solo admin)")
async def cambiar_rol(id: str, admin_flag: bool, admin: dict = Depends(validateadmin), db: AsyncIOMotorDatabase = Depends(get_db)):
    res = await db["users"].update_one({"_id": ObjectId(id)}, {"$set": {"admin": admin_flag}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"updated": True, "role": "admin" if admin_flag else "user"}
