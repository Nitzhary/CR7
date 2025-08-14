from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.tipo_torneo_model import TipoTorneoCreate, TipoTorneoDB
from bson import ObjectId

async def crear_tipo_torneo(db: AsyncIOMotorDatabase, data: TipoTorneoCreate):
    result = await db["tipos_torneo"].insert_one(data.dict())
    created = await db["tipos_torneo"].find_one({"_id": result.inserted_id})
    return TipoTorneoDB(**created)

async def listar_tipos_torneo(db: AsyncIOMotorDatabase):
    cursor = db["tipos_torneo"].find()
    return [TipoTorneoDB(**doc) async for doc in cursor]

async def obtener_tipo_torneo(db: AsyncIOMotorDatabase, id: str):
    doc = await db["tipos_torneo"].find_one({"_id": ObjectId(id)})
    return TipoTorneoDB(**doc) if doc else None

async def actualizar_tipo_torneo(db: AsyncIOMotorDatabase, id: str, data: TipoTorneoCreate):
    await db["tipos_torneo"].update_one({"_id": ObjectId(id)}, {"$set": data.dict()})
    return await obtener_tipo_torneo(db, id)

async def eliminar_tipo_torneo(db: AsyncIOMotorDatabase, id: str):
    result = await db["tipos_torneo"].delete_one({"_id": ObjectId(id)})
    return result.deleted_count == 1
