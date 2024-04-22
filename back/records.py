import sys
import logging
from typing import List

from pymongo import errors
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from fastapi import (APIRouter, UploadFile, status, HTTPException, 
                     Header, Depends, Form, File)

from managers.records_manager import upload_record
from managers.account_models import User, Record
from managers.mongo_config import *

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from user_authorization import verify_token

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    filename="mongodb.log",
                    filemode="w",)

router = APIRouter()


def get_authorization_token(authorization: str = Header(...)) -> str:
    scheme, _, param = authorization.partition(" ")
    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return param


def verify_user(token: str, user_id: str) -> bool:
    """
    토큰을 검증하고 요청한 user_id가 토큰에서 추출한 user_id와 일치하는지 확인합니다.

    Args:
        token (str): 검증할 JWT 토큰
        user_id (str): 요청받은 사용자 ID

    Returns:
        bool: 검증 성공 시 True, 실패 시 HTTPException 발생

    Raises:
        HTTPException: 토큰이 유효하지 않거나 user_id가 일치하지 않을 때
    """
    result, message = verify_token(token)
    
    # 토큰이 유효하지 않은 경우
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    

    email = message["email"]
    # 다른 사용자의 조회를 하는 경우
    if user_id != email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's records",
        )
    
    return True


@router.post("/{user_id}", response_model=Record)
async def create_record(
    user_id: str, 
    jd: str = Form(...), 
    questions: str = Form(...), 
    filename: str = Form(...), 
    file_data: UploadFile = File(...),) -> Record:
    # token: str = Depends(get_authorization_token)):
    
    # verify_user(token, user_id) # 인증과 인가 실패하면 이 단계에서 HTTPException 발생

    try:
        # Find the user
        user = collection.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        file_contents = await file_data.read()
        record = upload_record(user_id, jd, questions, filename, file_contents)
        await file_data.close()
        
        return record

    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=List[Record])
async def get_records(user_id: str,): # token: str = Depends(get_authorization_token)):
    
    # verify_user(token, user_id) # 인증과 인가 실패하면 이 단계에서 HTTPException 발생

    try:
        records = collection.find_one({"_id": user_id})
        return Record(**records)
    
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500 , detail=str(e))


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
    fake_record = Record(jd="채용공고", resume_file_id="0"*24, questions="질문", timestamp=1234567890)