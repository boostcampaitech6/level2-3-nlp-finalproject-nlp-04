from datetime import datetime
from typing import Optional
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

app = FastAPI(docs_url="/", redoc_url=None)

# MongoDB connection URL
MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
database = client["mydatabase"]
collection = database["items"]


class Items(BaseModel):
    email: str
    name: str
    access_token: str = None
    id_token: str = None
    # expires_in: int = None
    # available_credits: Optional[int] = 3
    # last_used: Optional[datetime] = None
    # jd: Optional[str] = None
    # resume: Optional[str] = None


@app.post("/items/", response_model=Items)
async def create_item(item: Items):
    result = await collection.insert_one(item.model_dump())
    item.id = str(result.inserted_id)
    return item


@app.get("/items/{item_id}", response_model=Items)
async def read_item(item_id: str):
    item = await collection.find_one({"_id": ObjectId(item_id)})
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.put("/items/{item_id}", response_model=Items)
async def update_item(item_id: str, item: Items):
    updated_item = await collection.find_one_and_update(
        {"_id": item_id}, {"$set": item.model_dump()}
    )
    if updated_item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}", response_model=Items)
async def delete_item(item_id: str):
    deleted_item = await collection.find_one_and_delete({"_id": item_id})
    if deleted_item:
        return deleted_item
    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)