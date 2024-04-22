import asyncio
import os
from datetime import datetime
from typing import List, Optional

from bson.objectid import ObjectId
from gridfs import NoFile
from pymongo import errors

from managers.db_operators import find_user_by_email
from managers.mongo_config import *


def upload_resume(email: str, filename: str, file_data):
    user = find_user_by_email(email)

    if not user:
        return None

    # GridFSBucket을 사용하여 파일 업로드
    file_id = fs_bucket.upload_from_stream(filename, file_data)

    return str(file_id)


def read_resume(email: str):
    user = find_user_by_email(email)
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
                'file_id': file_id,
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
        fs_bucket.delete(file_id_obj)

        # 사용자 컬렉션에서 파일 ID 제거
        collection.update_one(
            {'_id': user_id},
            {'$pull': {'resume_file_ids': file_id_obj}}
        )

        print(f"Deleted file with ID: {file_id} from user with ID: {user_id}")
    except NoFile:
        print(f"No file found with ID: {file_id}")


def main():
    try:
        collection.insert_one(fake_user.model_dump(by_alias=True))
    except errors.DuplicateKeyError:
        print("User already exists")

    # 파일 저장
    with open('./back/test.txt', 'rb') as f:
        file_id = upload_resume("koo", f.name.split('/')[-1], f)
        print(file_id)
    
    # 파일 읽기
    user_files = read_resume("koo")
    for file in user_files:
        print(file)

    # 파일 삭제
    delete_resume("koo", "0"*24)

if __name__ == "__main__":
    from account_models import User, History

    fake_history = History(
        jd="이력서 예시",
        resume_file_ids="0"*24,
        questions="질문 예시",
        timestamp=int(datetime.now().timestamp())
    )

    fake_user = User(_id="koo", name="희찬")
    main()