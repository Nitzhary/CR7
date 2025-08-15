from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.tipo_torneo_model import PyObjectId

class PartidoDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    torneo_id: PyObjectId
    fecha: str
    lugar: str
    equipo_local_id: PyObjectId
    equipo_visitante_id: PyObjectId
    goles_local: int = 0
    goles_visitante: int = 0

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PartidoCreate(BaseModel):
    torneo_id: str
    fecha: str
    lugar: str
    equipo_local_id: str
    equipo_visitante_id: str
