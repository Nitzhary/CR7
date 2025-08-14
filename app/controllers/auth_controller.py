from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user_model import UserCreate, UserDB
from bson import ObjectId
from app.utils.security import hash_password, verify_password, create_jwt_token

USERS_COLLECTION = "users"

async def signup(db: AsyncIOMotorDatabase, data: UserCreate) -> UserDB:
    # email unique
    existing = await db[USERS_COLLECTION].find_one({"email": data.email.lower()})
    if existing:
        raise ValueError("Email already registered")

    hashed = hash_password(data.password)
    doc = {
        "firstname": data.firstname,
        "lastname": data.lastname,
        "email": data.email.lower(),
        "password_hash": hashed,
        "active": True,
        "admin": False
    }
    result = await db[USERS_COLLECTION].insert_one(doc)
    created = await db[USERS_COLLECTION].find_one({"_id": result.inserted_id})
    return UserDB(
        id=str(created["_id"]),
        firstname=created["firstname"],
        lastname=created["lastname"],
        email=created["email"],
        active=created.get("active", True),
        admin=created.get("admin", False)
    )

async def login(db: AsyncIOMotorDatabase, email: str, password: str) -> dict:
    user = await db[USERS_COLLECTION].find_one({"email": email.lower()})
    if not user:
        raise ValueError("Invalid credentials")

    if not verify_password(password, user.get("password_hash")):
        raise ValueError("Invalid credentials")

    if not user.get("active", True):
        raise ValueError("User inactive")

    # create token
    token = create_jwt_token(
        firstname=user.get("firstname"),
        lastname=user.get("lastname"),
        email=user.get("email"),
        active=user.get("active", True),
        admin=user.get("admin", False),
        id=str(user.get("_id"))
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.get("_id")),
            "firstname": user.get("firstname"),
            "lastname": user.get("lastname"),
            "email": user.get("email"),
            "active": user.get("active", True),
            "admin": user.get("admin", False)
        }
    }
