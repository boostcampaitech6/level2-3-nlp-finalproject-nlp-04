import asyncio
import os
import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from gridfs import GridFSBucket, NoFile
from pydantic import BaseModel, Field
from pymongo import MongoClient, errors

from managers.account_models import User, History
from managers.file_manager import upload_resume, read_resume, delete_resume

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    filename="mongodb.log",
                    filemode="w",)

router = APIRouter()

# 환경 변수로부터 MongoDB 설정 읽기
username = os.getenv("MONGO_USERNAME", "admin")
password = os.getenv("MONGO_PASSWORD", "password")
MONGO_URL = f"mongodb://{username}:{password}@localhost:27017/"

# MongoDB와 GridFS 설정
loop = asyncio.get_event_loop()
client = MongoClient(MONGO_URL)
db = client["database"]
collection = db["users"]
fs_bucket = GridFSBucket(db)


# 동기
# @router.post("/{user_id}", response_model=History)
# async def create_history(user_id: str, history: History):
#     try:
#         # Find the user
#         user = collection.find_one({"_id": user_id})
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         # Add the new history to the user's history list
#         user["history"].append(history.dict())

#         # Update the user in the database
#         collection.update_one({"_id": user_id}, {"$set": user})

#         return history
#     except errors.PyMongoError as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/{user_id}", response_model=List[History])
# async def get_history(user_id: str):
#     try:
#         # Find the user
#         user = collection.find_one({"_id": user_id})
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         # Get the user's history list
#         history_list = user.get("history", [])

#         return history_list
#     except errors.PyMongoError as e:
#         raise HTTPException(status_code=500 , detail=str(e))


# @router.delete("/{user_id}/{history_id}")
# async def delete_history(user_id: str, history_id: str):
#     try:
#         # Find the user
#         user = collection.find_one({"_id": user_id})
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         # Find the history in the user's history list
#         history_list = user.get("history", [])
#         history = next((h for h in history_list if str(h["_id"]) == history_id), None)
#         if not history:
#             raise HTTPException(status_code=404, detail="History not found")

#         # Remove the history from the user's history list
#         history_list.remove(history)

#         # Update the user in the database
#         collection.update_one({"_id": user_id}, {"$set": user})

#         return {"message": "History deleted successfully"}
#     except errors.PyMongoError as e:
#         raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':

    fake_user = User(_id="koo", name="희찬")
    fake_history = History(jd="채용공고", resume_file_ids="0"*24, questions="질문", timestamp=1234567890)