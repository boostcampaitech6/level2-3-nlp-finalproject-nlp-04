import asyncio
import os
from datetime import datetime
from typing import List, Optional
import tracemalloc

from bson.objectid import ObjectId
from gridfs import NoFile
from pymongo import errors
from mongo_config import *
from account_models import History, User
from file_manager import upload_resume, read_resume, delete_resume

async def upload_history(email: str, jd: str, questions: str, filename: str, file_data):
    user = await collection.find_one({"_id": email})
    print(user)
    if not user:
        return None
    
    # 파일 업로드
    file_id = await upload_resume(email, filename, file_data)
    
    print("file_id: ", file_id, type(file_id))
    history = History(
        jd=jd,
        resume_file_ids=file_id,
        questions=questions,
        timestamp=int(datetime.now().timestamp())
    )
    history_dict = history.to_dict()
    # 사용자 문서에 파일 ID 추가
    updated_info = await collection.update_one(
        {"_id": email},
        {"$addToSet": {"history": history_dict}}
    )
 
    # 변경 사항 확인
    if updated_info.modified_count == 1:
        print(f"Added history with ID: {file_id} to user {email}")
    else:
        print(f"No changes made for user {email}")

    return str(file_id)


async def main():
    fake_user = User(_id="koo", name="희찬")
    try:
        await collection.insert_one(fake_user.model_dump(by_alias=True))
    except errors.DuplicateKeyError:
        print("User already exists")

    with open('./back/test.txt', 'rb') as f:
        await upload_history(email="koo", jd="이력서 예시", questions="질문 예시", filename="이력서 내용", file_data=f)


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
