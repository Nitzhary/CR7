from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.jugador_model import JugadorCreate, JugadorDB
from bson import ObjectId

async def crear_jugador(db: AsyncIOMotorDatabase, data: JugadorCreate):
    equipo = await db["equipos"].find_one({"_id": ObjectId(data.equipo_id)})
    if not equipo:
        raise ValueError("El equipo no existe")

    insert_data = data.dict()
    insert_data["equipo_id"] = ObjectId(data.equipo_id)

    result = await db["jugadores"].insert_one(insert_data)
    created = await db["jugadores"].find_one({"_id": result.inserted_id})
    return JugadorDB(**created)

async def listar_jugadores_por_equipo(db: AsyncIOMotorDatabase, equipo_id: str):
    cursor = db["jugadores"].find({"equipo_id": ObjectId(equipo_id)})
    return [JugadorDB(**doc) async for doc in cursor]

async def obtener_jugador(db: AsyncIOMotorDatabase, id: str):
    doc = await db["jugadores"].find_one({"_id": ObjectId(id)})
    return JugadorDB(**doc) if doc else None

async def actualizar_jugador(db: AsyncIOMotorDatabase, id: str, data: JugadorCreate):
    equipo = await db["equipos"].find_one({"_id": ObjectId(data.equipo_id)})
    if not equipo:
        raise ValueError("El equipo no existe")

    update_data = data.dict()
    update_data["equipo_id"] = ObjectId(data.equipo_id)

    await db["jugadores"].update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return await obtener_jugador(db, id)

async def eliminar_jugador(db: AsyncIOMotorDatabase, id: str):
    result = await db["jugadores"].delete_one({"_id": ObjectId(id)})
    return result.deleted_count == 1
