
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_db
from app.utils.security import validateuser
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/pipelines", tags=["Pipelines"])

@router.get("/partidos-detallados", summary="Pipeline 1: $lookup de partidos")
async def partidos_detallados(user: dict = Depends(validateuser), db: AsyncIOMotorDatabase = Depends(get_db)):
    pipeline = [
        {"$lookup": {
            "from": "equipos",
            "localField": "equipo_local_id",
            "foreignField": "_id",
            "as": "equipo_local"
        }},
        {"$lookup": {
            "from": "equipos",
            "localField": "equipo_visitante_id",
            "foreignField": "_id",
            "as": "equipo_visitante"
        }},
        {"$unwind": "$equipo_local"},
        {"$unwind": "$equipo_visitante"},
        {"$project": {
            "_id": {"$toString": "$_id"},
            "fecha": 1,
            "equipo_local": "$equipo_local.nombre",
            "equipo_visitante": "$equipo_visitante.nombre"
        }}
    ]
    return [x async for x in db["partidos"].aggregate(pipeline)]

@router.get("/goles-por-jugador", summary="Pipeline 2: $group conteo de goles")
async def goles_por_jugador(user: dict = Depends(validateuser), db: AsyncIOMotorDatabase = Depends(get_db)):
    # asumimos tipo_evento 'Gol' en tipos_evento
    tipo_gol = await db["tipos_evento"].find_one({"nombre": {"$regex": "^gol$", "$options": "i"}})
    if not tipo_gol:
        raise HTTPException(status_code=400, detail="No existe tipo de evento 'Gol'")
    pipeline = [
        {"$match": {"evento_id": tipo_gol["_id"]}},
        {"$group": {"_id": "$jugador_id", "goles": {"$sum": 1}}},
        {"$lookup": {
            "from": "jugadores",
            "localField": "_id",
            "foreignField": "_id",
            "as": "jugador"
        }},
        {"$unwind": "$jugador"},
        {"$project": {
            "_id": 0,
            "jugador_id": {"$toString": "$_id"},
            "jugador": "$jugador.nombre",
            "goles": 1
        }},
        {"$sort": {"goles": -1}}
    ]
    return [x async for x in db["eventos"].aggregate(pipeline)]

@router.get("/eventos-por-tipo", summary="Pipeline 3: $group por tipo de evento")
async def eventos_por_tipo(user: dict = Depends(validateuser), db: AsyncIOMotorDatabase = Depends(get_db)):
    pipeline = [
        {"$group": {"_id": "$evento_id", "cantidad": {"$sum": 1}}},
        {"$lookup": {
            "from": "tipos_evento",
            "localField": "_id",
            "foreignField": "_id",
            "as": "tipo"
        }},
        {"$unwind": "$tipo"},
        {"$project": {
            "_id": 0,
            "tipo_evento_id": {"$toString": "$_id"},
            "tipo": "$tipo.nombre",
            "cantidad": 1
        }},
        {"$sort": {"cantidad": -1}}
    ]
    return [x async for x in db["eventos"].aggregate(pipeline)]

@router.get("/partidos-por-fecha", summary="QueryString: partidos por fecha (YYYY-MM-DD)")
async def partidos_por_fecha(
    fecha: str = Query(..., description="YYYY-MM-DD"),
    user: dict = Depends(validateuser),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    try:
        dt = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido")
    pipeline = [
        {"$match": {"fecha": fecha}},  # si guardas fecha como string YYYY-MM-DD
        {"$project": {"_id": {"$toString": "$_id"}, "fecha": 1, "torneo_id": {"$toString": "$torneo_id"}}}
    ]
    return [x async for x in db["partidos"].aggregate(pipeline)]
