import os
from pymongo import MongoClient
from gridfs import GridFSBucket
from dotenv import load_env

load_env(overide=True)

# 환경 변수로부터 MongoDB 설정 읽기
username = os.getenv("MONGO_USERNAME", "admin")
password = os.getenv("MONGO_PASSWORD", "password")

# MongoDB connection URL
MONGO_URL = f"mongodb://{username}:{password}@localhost:27017/"
client = MongoClient(MONGO_URL)
database = client["database"]
collection = database["users"]
fs_bucket = GridFSBucket(database)
