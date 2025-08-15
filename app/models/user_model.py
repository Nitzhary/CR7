from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    firstname: str = Field(..., min_length=2)
    lastname: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserDB(BaseModel):
    id: str
    firstname: str
    lastname: str
    email: EmailStr
    active: bool = True
    admin: bool = False
