import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

# 환경 변수로부터 MongoDB 설정 읽기
username = os.getenv("MONGO_USERNAME", "admin")
password = os.getenv("MONGO_PASSWORD", "password")

# MongoDB connection URL
MONGO_URL = f"mongodb://{username}:{password}@localhost:27017/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["database"]
collection = database["users"]
fs_bucket = AsyncIOMotorGridFSBucket(database)
