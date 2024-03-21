from datetime import datetime
from typing import Optional
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo import ReturnDocument, errors
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',  # 이 부분에서 파일 경로와 이름을 설정합니다.
    filemode='w'
)

app = FastAPI(docs_url="/", redoc_url=None)

# MongoDB connection URL
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
database = client["mydatabase"]
collection = database["users"]

try:
    collection.create_index("email", unique=True)
except errors.DuplicateKeyError:
    print("This email already exists")


class User(BaseModel):
    email: str            
    name: str
    access_token: str = None
    id_token: str = None
    # expires_in: int = None
    # available_credits: Optional[int] = 3
    # last_used: Optional[datetime] = None
    # jd: Optional[str] = None
    # resume: Optional[str] = None


@app.get("/users/{email}/exists")
async def check_email_exists(email: str):
    user = await collection.find_one({"email": email})
    return user is not None


@app.post("/users/", response_model=User)
async def create_item(item: User):
    result = await collection.insert_one(item.model_dump())
    item.email = str(result.inserted_id)
    return item


@app.put("/users/{email}", response_model=User)
async def update_item(email: str, item: User):
    update_fields = {k: v for k, v in item.model_dump().users() if v is not None}
    updated_item = await collection.find_one_and_update(
        {"email": email},
        {"$set": update_fields},
        return_document=ReturnDocument.AFTER
    )
    if updated_item:
        return User(**updated_item)
    raise HTTPException(status_code=404, detail="Item not found")


@app.get("/users/{email}", response_model=User)
async def read_item(email: str):
    item = await collection.find_one({"email": email})
    if item:
        return User(**item)  # User 모델에 맞게 딕셔너리를 언팩
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/users/{email}", response_model=User)
async def delete_item(email: str):
    deleted_item = await collection.find_one_and_delete({"email": email})
    if deleted_item:
        return deleted_item
    raise HTTPException(status_code=404, detail="Item not found")




@app.get("/users/{email}/token")
async def get_access_token(email: str):
    user = await collection.find_one({"email": email}, {"access_token": 1})
    if user and "access_token" in user:
        return {"access_token": user["access_token"]}
    raise HTTPException(status_code=404, detail="User not found or access token not set")


@app.put("/users/{email}/token", response_model=User)
async def update_access_token(email: str, token: str):
    updated_user = await collection.find_one_and_update(
        {"email": email},
        {"$set": {"access_token": token}},
        return_document=ReturnDocument.AFTER
    )
    if updated_user:
        return User(**updated_user)
    raise HTTPException(status_code=404, detail="User not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)