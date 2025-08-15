from fastapi import APIRouter, HTTPException, Depends
from app.firebase import verify_firebase_token
from app.utils.security import create_jwt_token
from app.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase

router = APIRouter()

@router.post("/login")
async def login(data: dict, db: AsyncIOMotorDatabase = Depends(get_db)):
    firebase_token = data.get("firebase_token")
    if not firebase_token:
        raise HTTPException(status_code=400, detail="Se requiere firebase_token")

    try:
        firebase_user = verify_firebase_token(firebase_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # Buscar o crear el usuario en MongoDB
    user_collection = db["usuarios"]
    user_data = await user_collection.find_one({"uid": firebase_user["uid"]})
    if not user_data:
        user_data = {
            "uid": firebase_user["uid"],
            "email": firebase_user.get("email"),
            "name": firebase_user.get("name", ""),
            "role": "user",
            "active": True
        }
        await user_collection.insert_one(user_data)

    # Generar JWT local
    token = create_jwt_token(
        firstname=user_data.get("name", ""),
        lastname="",
        email=user_data.get("email", ""),
        active=user_data.get("active", True),
        admin=user_data.get("role") == "admin",
        id=str(user_data["_id"])
    )

    return {"access_token": token, "token_type": "bearer"}
