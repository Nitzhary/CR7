from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.torneo_model import TorneoCreate, TorneoDB
from bson import ObjectId

async def crear_torneo(db: AsyncIOMotorDatabase, data: TorneoCreate):
    tipo = await db["tipos_torneo"].find_one({"_id": ObjectId(data.tipo_id)})
    if not tipo:
        raise ValueError("El tipo de torneo no existe")

    insert_data = data.dict()
    insert_data["tipo_id"] = ObjectId(data.tipo_id)

    result = await db["torneos"].insert_one(insert_data)
    created = await db["torneos"].find_one({"_id": result.inserted_id})
    return TorneoDB(**created)

async def listar_torneos(db: AsyncIOMotorDatabase):
    cursor = db["torneos"].find()
    return [TorneoDB(**doc) async for doc in cursor]

async def obtener_torneo(db: AsyncIOMotorDatabase, id: str):
    doc = await db["torneos"].find_one({"_id": ObjectId(id)})
    return TorneoDB(**doc) if doc else None

async def actualizar_torneo(db: AsyncIOMotorDatabase, id: str, data: TorneoCreate):
    tipo = await db["tipos_torneo"].find_one({"_id": ObjectId(data.tipo_id)})
    if not tipo:
        raise ValueError("El tipo de torneo no existe")

    update_data = data.dict()
    update_data["tipo_id"] = ObjectId(data.tipo_id)

    await db["torneos"].update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return await obtener_torneo(db, id)

async def eliminar_torneo(db: AsyncIOMotorDatabase, id: str):
    result = await db["torneos"].delete_one({"_id": ObjectId(id)})
    return result.deleted_count == 1
