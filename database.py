from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb+srv://cattus-web:ZycXOL2qALXurYW0@cattus-api.sgnegkc.mongodb.net/?retryWrites=true&w=majority&appName=cattus-api")
db = client["test"]
collection = db["notifications"]
