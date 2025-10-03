import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

client = AsyncIOMotorClient(os.getenv("DATABASE_URL"))
db = client[os.getenv("DATABASE_NAME")]

notifications_collection = db["notifications"]
activities_collection = db["activities"]
