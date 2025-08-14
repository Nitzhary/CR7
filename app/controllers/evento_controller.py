from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.evento_model import EventoCreate, EventoDB
from bson import ObjectId

async def registrar_evento(db: AsyncIOMotorDatabase, data: EventoCreate):
    # Validar existencia de entidades
    if not await db["jugadores"].find_one({"_id": ObjectId(data.jugador_id)}):
        raise ValueError("Jugador no encontrado")
    if not await db["partidos"].find_one({"_id": ObjectId(data.partido_id)}):
        raise ValueError("Partido no encontrado")
    if not await db["tipos_evento"].find_one({"_id": ObjectId(data.evento_id)}):
        raise ValueError("Tipo de evento no encontrado")

    insert_data = {
        "jugador_id": ObjectId(data.jugador_id),
        "partido_id": ObjectId(data.partido_id),
        "evento_id": ObjectId(data.evento_id),
        "minuto": data.minuto
    }

    result = await db["eventos"].insert_one(insert_data)
    created = await db["eventos"].find_one({"_id": result.inserted_id})
    return EventoDB(**created)

async def eventos_por_partido(db: AsyncIOMotorDatabase, partido_id: str):
    cursor = db["eventos"].find({"partido_id": ObjectId(partido_id)})
    return [EventoDB(**doc) async for doc in cursor]

async def eventos_por_jugador(db: AsyncIOMotorDatabase, jugador_id: str):
    cursor = db["eventos"].find({"jugador_id": ObjectId(jugador_id)})
    return [EventoDB(**doc) async for doc in cursor]
