from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.tipo_torneo_model import PyObjectId

class EventoDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    jugador_id: PyObjectId
    partido_id: PyObjectId
    evento_id: PyObjectId
    minuto: int

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EventoCreate(BaseModel):
    jugador_id: str
    partido_id: str
    evento_id: str
    minuto: int
