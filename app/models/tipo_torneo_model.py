from pydantic import BaseModel, Field
from bson import ObjectId
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.json_schema(
            schema=core_schema.no_info_after_validator_function(
                cls.validate,
                core_schema.str_schema()
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: str(v),
                when_used="always"
            )
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class TipoTorneoDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    nombre: str = Field(..., min_length=3, max_length=50)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TipoTorneoCreate(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50)
