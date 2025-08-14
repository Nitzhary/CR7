from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.equipo_model import EquipoCreate, EquipoDB
from bson import ObjectId

async def crear_equipo(db: AsyncIOMotorDatabase, data: EquipoCreate):
    torneo = await db["torneos"].find_one({"_id": ObjectId(data.torneo_id)})
    if not torneo:
        raise ValueError("El torneo no existe")

    insert_data = data.dict()
    insert_data["torneo_id"] = ObjectId(data.torneo_id)

    result = await db["equipos"].insert_one(insert_data)
    created = await db["equipos"].find_one({"_id": result.inserted_id})
    return EquipoDB(**created)

async def listar_equipos_por_torneo(db: AsyncIOMotorDatabase, torneo_id: str):
    cursor = db["equipos"].find({"torneo_id": ObjectId(torneo_id)})
    return [EquipoDB(**doc) async for doc in cursor]

async def obtener_equipo(db: AsyncIOMotorDatabase, id: str):
    doc = await db["equipos"].find_one({"_id": ObjectId(id)})
    return EquipoDB(**doc) if doc else None

async def actualizar_equipo(db: AsyncIOMotorDatabase, id: str, data: EquipoCreate):
    torneo = await db["torneos"].find_one({"_id": ObjectId(data.torneo_id)})
    if not torneo:
        raise ValueError("El torneo no existe")

    update_data = data.dict()
    update_data["torneo_id"] = ObjectId(data.torneo_id)

    await db["equipos"].update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return await obtener_equipo(db, id)

async def eliminar_equipo(db: AsyncIOMotorDatabase, id: str):
    result = await db["equipos"].delete_one({"_id": ObjectId(id)})
    return result.deleted_count == 1
