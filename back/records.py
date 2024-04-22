import logging

from fastapi import APIRouter
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from managers.account_models import User, Record
from managers.mongo_config import *

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    filename="mongodb.log",
                    filemode="w",)

router = APIRouter()

fs_bucket = AsyncIOMotorGridFSBucket(database)



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
    fake_history = Record(jd="채용공고", resume_file_ids="0"*24, questions="질문", timestamp=1234567890)