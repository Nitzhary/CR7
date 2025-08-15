from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = None

def get_db():
    return client[settings.MONGO_DB_NAME]

async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(settings.MONGO_URI)
    print("✅ Conexión establecida a MongoDB")
