import asyncio
import os
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from gridfs import NoFile
from pymongo import errors
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket


# 환경 변수로부터 MongoDB 설정 읽기
username = os.getenv("MONGO_USERNAME", "admin")
password = os.getenv("MONGO_PASSWORD", "password")
MONGO_URL = f"mongodb://{username}:{password}@localhost:27017/"

# MongoDB와 GridFS 설정
# loop = asyncio.get_event_loop()

# async 설정
client = AsyncIOMotorClient(MONGO_URL)
db = client["database"]
collection = db["users"]
fs_bucket = AsyncIOMotorGridFSBucket(db)


async def upload_resume(email: str, filename: str, file_data):
    user = await collection.find_one({"_id": email})
    print(user)
    if not user:
        return None

    # GridFSBucket을 사용하여 파일 업로드
    file_id = await fs_bucket.upload_from_stream(filename, file_data)

    # 사용자 문서에 파일 ID 추가
    updated_info = await collection.update_one(
        {"_id": email},
        {"$addToSet": {"resume_file_ids": file_id}}
    )

    # 변경 사항 확인
    if updated_info.modified_count == 1:
        print(f"Added resume file with ID: {file_id} to user {email}")
    else:
        print(f"No changes made for user {email}")

    return str(file_id)


async def read_resume(email: str):
    user = await collection.find_one({"_id": email})
    if not user:
        print("User not found")
        return None

    valid_file_ids = []
    files_content = []
    file_ids = user.get('resume_file_ids', [])

    for file_id_str in file_ids:
        file_id = ObjectId(file_id_str)
        try:
            grid_out = await fs_bucket.open_download_stream(file_id)
            content = grid_out.read()
            upload_date = grid_out.upload_date.strftime("%Y-%m-%d, %H:%M:%S")
            files_content.append({
                'filename': grid_out.filename,
                'file_id': str(file_id),
                "upload_date": upload_date,
                "content": content
            })
            valid_file_ids.append(file_id_str)
        except NoFile:
            print(f"No file found in GridFS with _id: {file_id_str}")

    # 사용자 문서에서 유효하지 않은 file_id 제거
    if len(file_ids) != len(valid_file_ids):
        collection.update_one(
            {"_id": email},
            {"$set": {"resume_file_ids": valid_file_ids}}
        )
        print(f"Updated user {email} with valid file IDs.")

    return files_content


async def delete_resume(user_id: str, file_id: str):
    try:
        file_id_obj = ObjectId(file_id)

        # 파일 삭제
        await fs_bucket.delete(file_id_obj)

        # 사용자 컬렉션에서 파일 ID 제거
        await collection.update_one(
            {'_id': user_id},
            {'$pull': {'resume_file_ids': file_id_obj}}
        )

        print(f"Deleted file with ID: {file_id} from user with ID: {user_id}")
    except NoFile:
        print(f"No file found with ID: {file_id}")


async def main():
    try:
        await collection.insert_one(fake_user.model_dump(by_alias=True))
    except errors.DuplicateKeyError:
        print("User already exists")

    # 파일 저장
    with open('./back/test.txt', 'rb') as f:
        file_id = await upload_resume("koo", f.name.split('/')[-1], f)
        print(file_id)
    
    # 파일 읽기
    user_files = await read_resume("koo")
    # for file in user_files:
    #     print(file)

    # 파일 삭제
    await delete_resume("koo", "0"*24)

if __name__ == "__main__":
    from account_models import User, History

    fake_history = History(
        jd="이력서 예시",
        resume_file_ids="0"*24,
        questions="질문 예시",
        timestamp=int(datetime.now().timestamp())
    )

    fake_user = User(_id="koo", name="희찬")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()