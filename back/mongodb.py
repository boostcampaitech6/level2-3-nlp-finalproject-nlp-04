import logging
from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo import ReturnDocument, errors

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="mongodb.log",
    filemode="w",
)

app = FastAPI(docs_url="/", redoc_url=None)

# MongoDB connection URL
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
database = client["mydatabase"]
collection = database["users"]

try:
    collection.create_index("email", unique=True)  # 이메일 필드에 고유 인덱스 생성
except errors.DuplicateKeyError:
    print("This email already exists")  # 이미 존재하는 이메일인 경우 출력


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
async def create_user(user: User):
    result = await collection.insert_one(user.model_dump())
    user.email = str(result.inserted_id)
    return user


@app.put("/users/{email}", response_model=User)
async def update_user(email: str, user: User):
    update_fields = {k: v for k, v in user.model_dump().users() if v is not None}
    updated_user = await collection.find_one_and_update(
        {"email": email}, {"$set": update_fields}, return_document=ReturnDocument.AFTER
    )
    if updated_user:
        return User(**updated_user)
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/users/{email}", response_model=User)
async def read_user(email: str):
    user = await collection.find_one({"email": email})
    if user:
        return User(**user)  # User 모델에 맞게 딕셔너리를 언팩
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{email}", response_model=User)
async def delete_user(email: str):
    deleted_user = await collection.find_one_and_delete({"email": email})
    if deleted_user:
        return deleted_user
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/users/{email}/token")
async def get_access_token(email: str):
    user = await collection.find_one({"email": email}, {"access_token": 1})
    if user and "access_token" in user:
        return {"access_token": user["access_token"]}
    raise HTTPException(
        status_code=404, detail="User not found or access token not set"
    )


@app.put("/users/{email}/token", response_model=User)
async def update_access_token(email: str, token: str):
    updated_user = await collection.find_one_and_update(
        {"email": email},
        {"$set": {"access_token": token}},
        return_document=ReturnDocument.AFTER,
    )
    if updated_user:
        return User(**updated_user)
    raise HTTPException(status_code=404, detail="User not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
