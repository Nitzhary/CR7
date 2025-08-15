from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.tipo_torneo_model import PyObjectId

class TorneoDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombre: str = Field(..., min_length=3, max_length=100)
    fecha_inicio: str
    fecha_fin: str
    tipo_id: PyObjectId

    class Config:
        populate_by_name = True  # en Pydantic v2 se usa esto en vez de allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TorneoCreate(BaseModel):
    nombre: str
    fecha_inicio: str
    fecha_fin: str
    tipo_id: str  # ID como string recibido del frontend
