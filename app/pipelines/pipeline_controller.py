from motor.motor_asyncio import AsyncIOMotorDatabase

async def partidos_detallados(db: AsyncIOMotorDatabase):
    pipeline = [
        {
            "$lookup": {
                "from": "equipos",
                "localField": "equipo_local_id",
                "foreignField": "_id",
                "as": "equipo_local"
            }
        },
        {
            "$lookup": {
                "from": "equipos",
                "localField": "equipo_visitante_id",
                "foreignField": "_id",
                "as": "equipo_visitante"
            }
        },
        {
            "$unwind": "$equipo_local"
        },
        {
            "$unwind": "$equipo_visitante"
        },
        {
            "$project": {
                "_id": 1,
                "fecha": 1,
                "lugar": 1,
                "goles_local": 1,
                "goles_visitante": 1,
                "equipo_local": "$equipo_local.nombre",
                "equipo_visitante": "$equipo_visitante.nombre"
            }
        }
    ]
    return [doc async for doc in db["partidos"].aggregate(pipeline)]

async def goles_por_jugador(db: AsyncIOMotorDatabase):
    pipeline = [
        {
            "$lookup": {
                "from": "tipos_evento",
                "localField": "evento_id",
                "foreignField": "_id",
                "as": "tipo"
            }
        },
        { "$unwind": "$tipo" },
        {
            "$match": {
                "tipo.nombre": "gol"
            }
        },
        {
            "$group": {
                "_id": "$jugador_id",
                "goles": { "$sum": 1 }
            }
        },
        {
            "$lookup": {
                "from": "jugadores",
                "localField": "_id",
                "foreignField": "_id",
                "as": "jugador"
            }
        },
        { "$unwind": "$jugador" },
        {
            "$project": {
                "jugador": "$jugador.nombre",
                "goles": 1
            }
        }
    ]
    return [doc async for doc in db["eventos"].aggregate(pipeline)]


from app.models.partido_model import PartidoCreate, PartidoDB
from bson import ObjectId

async def crear_partido_validado(db: AsyncIOMotorDatabase, data: PartidoCreate):
    # Contar partidos en la misma fecha
    cantidad = await db["partidos"].count_documents({"fecha": data.fecha})
    if cantidad >= 2:
        raise ValueError("Ya existen 2 partidos registrados en esta fecha")

    # Reutilizar lógica del partido normal
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

async def eventos_por_tipo(db: AsyncIOMotorDatabase):
    pipeline = [
        {
            "$lookup": {
                "from": "tipos_evento",
                "localField": "evento_id",
                "foreignField": "_id",
                "as": "tipo"
            }
        },
        { "$unwind": "$tipo" },
        {
            "$group": {
                "_id": "$tipo.nombre",
                "cantidad": { "$sum": 1 }
            }
        },
        {
            "$project": {
                "tipo_evento": "$_id",
                "cantidad": 1,
                "_id": 0
            }
        }
    ]
    return [doc async for doc in db["eventos"].aggregate(pipeline)]

#endpoint query string
async def partidos_por_fecha(db: AsyncIOMotorDatabase, fecha: str):
    partidos = db["partidos"].find({"fecha": fecha})
    return [doc async for doc in partidos]
