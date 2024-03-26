import asyncio
import os
from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from gridfs import GridFSBucket, NoFile
from pydantic import BaseModel
from pymongo import MongoClient

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


def upload_resume(email: str, filename: str, file_data):
    user = collection.find_one({"_id": email})
    print(user)
    if not user:
        return None

    # GridFSBucket을 사용하여 파일 업로드
    file_id = fs_bucket.upload_from_stream(filename, file_data)

    # 사용자 문서에 파일 ID 추가
    updated_info = collection.update_one(
        {"_id": email},
        {"$addToSet": {"resume_file_ids": file_id}}
    )

    # 변경 사항 확인
    if updated_info.modified_count == 1:
        print(f"Added resume file with ID: {file_id} to user {email}")
    else:
        print(f"No changes made for user {email}")

    return str(file_id)


def read_resume(email: str):
    user = collection.find_one({"_id": email})
    if not user:
        print("User not found")
        return None

    valid_file_ids = []
    files_content = []
    file_ids = user.get('resume_file_ids', [])

    for file_id_str in file_ids:
        file_id = ObjectId(file_id_str)
        try:
            grid_out = fs_bucket.open_download_stream(file_id)
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


def delete_resume(user_id: str, file_id: str):
    file_id_obj = ObjectId(file_id)

    # GridFSBucket에서 파일 삭제
    fs_bucket.delete(file_id_obj)

    # 사용자 컬렉션에서 파일 ID 제거
    collection.update_one(
        {'_id': user_id},
        {'$pull': {'resume_file_ids': file_id_obj}}
    )

    print(f"Deleted file with ID: {file_id} from user with ID: {user_id}")


if __name__ == "__main__":
    class User(BaseModel):
        email: str        # _id 필드를 email로 alias
        name: str                                   # 이름
        access_token: str = None                    # OAuth2의 access_token
        id_token: str = None                        # OAuth2의 id_token(JWT)
        expires_in: int = None  # 언제 사용할까요?   # 아직 사용하지 않음
        last_login: Optional[datetime] = None       # 마지막 로그인 시간
        joined: Optional[datetime] = None           # 가입 날짜
        available_credits: Optional[int] = 3        # 무료로 사용 가능한 크레딧
        jd: Optional[List] = None                   # 입력한 채용공고 list
        resume: Optional[List] = None               # 입력한 이력서 list
        resume_file_id: Optional[str] = None        # 추가된 필드

    
    fake_user = User(email="koo", name="희찬")

    # 파일 저장
    with open('./test.txt', 'rb') as f:
        file_id = upload_resume("koo", f.name.split('/')[-1], f)
    
    # 파일 읽기
    user_files = read_resume("koo")
    for file in user_files:
        print(file)

    # 파일 삭제
    delete_resume("koo", "6602f70ac35b92eeafa54458")