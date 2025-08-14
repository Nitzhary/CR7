from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.partido_model import PartidoCreate, PartidoDB
from bson import ObjectId

async def crear_partido(db: AsyncIOMotorDatabase, data: PartidoCreate):
    # Validar torneo
    torneo = await db["torneos"].find_one({"_id": ObjectId(data.torneo_id)})
    if not torneo:
        raise ValueError("El torneo no existe")

    # Validar equipos
    local = await db["equipos"].find_one({"_id": ObjectId(data.equipo_local_id)})
    visitante = await db["equipos"].find_one({"_id": ObjectId(data.equipo_visitante_id)})
    if not local or not visitante:
        raise ValueError("Uno o ambos equipos no existen")

    insert_data = {
        "torneo_id": ObjectId(data.torneo_id),
        "fecha": data.fecha,
        "lugar": data.lugar,
        "equipo_local_id": ObjectId(data.equipo_local_id),
        "equipo_visitante_id": ObjectId(data.equipo_visitante_id),
        "goles_local": 0,
        "goles_visitante": 0
    }

    result = await db["partidos"].insert_one(insert_data)
    created = await db["partidos"].find_one({"_id": result.inserted_id})
    return PartidoDB(**created)

async def obtener_partido(db: AsyncIOMotorDatabase, id: str):
    doc = await db["partidos"].find_one({"_id": ObjectId(id)})
    return PartidoDB(**doc) if doc else None

async def listar_partidos_por_torneo(db: AsyncIOMotorDatabase, torneo_id: str):
    cursor = db["partidos"].find({"torneo_id": ObjectId(torneo_id)})
    return [PartidoDB(**doc) async for doc in cursor]
