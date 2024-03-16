# back/file_manager.py
# from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from gridfs import GridFSBucket
from bson import ObjectId
from typing import Optional

client = MongoClient('mongodb://localhost:27017/')
db = client['mydatabase']
bucket = GridFSBucket(db)

def upload_file(email: str, file):
    file_id = bucket.upload_from_stream(file.filename, file.file.read())
    db.users.update_one({"email": email}, {"$set": {"file_id": file_id}}, upsert=True)
    return str(file_id)

def download_file(email: str):
    user = db.users.find_one({"email": email})
    if not user or "file_id" not in user:
        return None
    file_id = user["file_id"]
    file = bucket.open_download_stream(file_id)
    return file.read()