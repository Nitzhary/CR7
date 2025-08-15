from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.tipo_torneo_model import PyObjectId

class EquipoDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombre: str = Field(..., min_length=3, max_length=100)
    fundado_en: int
    torneo_id: PyObjectId

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EquipoCreate(BaseModel):
    nombre: str
    fundado_en: int
    torneo_id: str
