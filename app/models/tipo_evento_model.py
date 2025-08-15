from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.tipo_torneo_model import PyObjectId

class TipoEventoDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombre: str = Field(..., min_length=3, max_length=50)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TipoEventoCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50)
