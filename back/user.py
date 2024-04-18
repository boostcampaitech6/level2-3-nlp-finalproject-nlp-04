import logging
import os
from typing import List, Optional

import streamlit as st
from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument, errors

from managers.account_models import User, History

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    filename="mongodb.log",
                    filemode="w",)

router = APIRouter()
username = os.getenv("MONGO_USERNAME", "admin")
password = os.getenv("MONGO_PASSWORD", "password")

# MongoDB connection URL
MONGO_URL = f"mongodb://{username}:{password}@localhost:27017/"
client = AsyncIOMotorClient(MONGO_URL)
database = client["database"]
collection = database["users"]

# try:
#     collection.create_index("email", unique=True)  # 이메일 필드에 고유 인덱스 생성
# except errors.DuplicateKeyError:
#     print("This email already exists")  # 이미 존재하는 이메일인 경우 출력

# await collection.create_index([("email", ASCENDING)], unique=True)
 

@router.get("/{email}/exists")
async def check_email_exists(email: str):
    """
    이 함수는 주어진 이메일이 데이터베이스에 존재하는지 확인합니다.

    Parameters:
        email (str): 확인할 이메일 주소

    Returns:
        bool: 이메일이 데이터베이스에 존재하는 경우 True를 반환하고, 그렇지 않은 경우 False를 반환합니다.
    """
    user = await collection.find_one({"_id": email})
    return user is not None


@router.post("/", response_model=User)
async def create_user(user: User):
    """
    사용자를 생성하는 함수입니다.

    Parameters:
        user (User): 생성할 사용자 정보를 담고 있는 User 객체

    Returns:
        User: 생성된 사용자 정보를 담고 있는 User 객체
    """
    # user.emial = email
    try:
        await collection.insert_one(user.model_dump(by_alias=True))
        # user._id = str(result.inserted_id)
    except errors.DuplicateKeyError:
        raise HTTPException(status_code=409, detail="User already exists")
    return user


@router.put("/{email}", response_model=User)
async def update_user(email: str, user: User):
    """
    사용자 정보를 업데이트하는 함수입니다.

    Parameters:
        email (str): 사용자 이메일
        user (User): 업데이트할 사용자 정보

    Returns:
        User: 업데이트된 사용자 정보

    Raises:
        HTTPException: 사용자를 찾을 수 없을 때 발생하는 예외
    """
    update_fields = {k: v for k, v in user.model_dump(by_alias=True).items() if v is not None}
    updated_user = await collection.find_one_and_update({"_id": email},
                                                        {"$set": update_fields},
                                                        return_document=ReturnDocument.AFTER,)
    
    if updated_user:
        return User(**updated_user)
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/{email}", response_model=User)
async def read_user(email: str):
    """
    사용자 이메일을 받아와서 해당 이메일을 가진 사용자를 조회합니다.

    Parameters:
        email (str): 조회할 사용자의 이메일

    Returns:
        User: 조회된 사용자 정보

    Raises:
        HTTPException: 조회된 사용자가 없을 경우 404 에러를 발생시킵니다.
    """
    user = await collection.find_one({"_id": email})
    if user:
        return User(**user)  # User 모델에 맞게 딕셔너리를 언팩
    raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{email}", response_model=User)
async def delete_user(email: str):
    """
    사용자를 삭제하는 함수입니다.

    Parameters:
        email (str): 삭제할 사용자의 이메일 주소

    Returns:
        User: 삭제된 사용자의 정보

    Raises:
        HTTPException: 삭제할 사용자가 없을 경우 발생합니다.
    """
    deleted_user = await collection.find_one_and_delete({"_id": email})
    if deleted_user:
        return deleted_user
    raise HTTPException(status_code=404, detail="User not found")


@router.get("/{email}/token")
async def get_access_token(email: str):
    """
    사용자의 이메일을 입력받아 해당 사용자의 액세스 토큰을 반환합니다.

    Parameters:
        email (str): 사용자의 이메일 주소

    Returns:
        dict: 액세스 토큰을 포함한 딕셔너리

    Raises:
        HTTPException: 사용자를 찾을 수 없거나 액세스 토큰이 설정되지 않은 경우 404 오류를 발생시킵니다.
    """
    user = await collection.find_one({"_id": email}, {"access_token": 1})
    if user and "access_token" in user:
        return {"access_token": user["access_token"]}
    raise HTTPException(status_code=404, detail="User not found or access token not set")


@router.put("/{email}/token", response_model=User)
async def update_access_token(email: str, token: str):
    """
    사용자의 액세스 토큰을 업데이트하는 함수입니다.

    Parameters:
        email (str): 사용자 이메일
        token (str): 업데이트할 액세스 토큰

    Returns:
        User: 업데이트된 사용자 정보

    Raises:
        HTTPException: 사용자를 찾을 수 없을 때 발생하는 예외
    """
    updated_user = await collection.find_one_and_update(
        {"_id": email},
        {"$set": {"access_token": token}},
        return_document=ReturnDocument.AFTER,
    )

    if updated_user:
        return User(**updated_user)
    
    raise HTTPException(status_code=404, detail="User not found")
