import motor.motor_asyncio
import os

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
database = client[MONGO_DB]
