from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.tipo_torneo_model import PyObjectId

class JugadorDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombre: str
    edad: int
    posicion: str
    equipo_id: PyObjectId

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class JugadorCreate(BaseModel):
    nombre: str
    edad: int
    posicion: str
    equipo_id: str
