from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.tipo_evento_model import TipoEventoCreate, TipoEventoDB
from bson import ObjectId

async def crear_tipo_evento(db: AsyncIOMotorDatabase, data: TipoEventoCreate):
    result = await db["tipos_evento"].insert_one(data.dict())
    created = await db["tipos_evento"].find_one({"_id": result.inserted_id})
    return TipoEventoDB(**created)

async def listar_tipos_evento(db: AsyncIOMotorDatabase):
    cursor = db["tipos_evento"].find()
    return [TipoEventoDB(**doc) async for doc in cursor]

async def obtener_tipo_evento(db: AsyncIOMotorDatabase, id: str):
    doc = await db["tipos_evento"].find_one({"_id": ObjectId(id)})
    return TipoEventoDB(**doc) if doc else None

async def actualizar_tipo_evento(db: AsyncIOMotorDatabase, id: str, data: TipoEventoCreate):
    await db["tipos_evento"].update_one({"_id": ObjectId(id)}, {"$set": data.dict()})
    return await obtener_tipo_evento(db, id)

async def eliminar_tipo_evento(db: AsyncIOMotorDatabase, id: str):
    # Validar que no haya eventos asociados a este tipo
    eventos = await db["eventos"].count_documents({"evento_id": ObjectId(id)})
    if eventos > 0:
        raise ValueError("No se puede eliminar: hay eventos asociados a este tipo")

    result = await db["tipos_evento"].delete_one({"_id": ObjectId(id)})
    return result.deleted_count == 1
