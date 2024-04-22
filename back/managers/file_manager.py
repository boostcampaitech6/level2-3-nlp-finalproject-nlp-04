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

    files_content = []
    records = user.get('records', [])

    for record in records:
        file_id_str = record['resume_file_id']
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

        except NoFile:
            print(f"No file found in GridFS with _id: {file_id_str}")

    return files_content


def delete_resume(user_id: str, file_id: str):
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
    from account_models import User, Record
    
    fake_record = Record(
        jd="이력서 예시",
        resume_file_id="0"*24,
        questions="질문 예시",
        timestamp=int(datetime.now().timestamp())
    )

    fake_user = User(_id="koo", name="희찬")
    
    try:
        collection.insert_one(fake_user.model_dump(by_alias=True))
    except errors.DuplicateKeyError:
        print("User already exists")
    
    from records_manager import upload_record
    # 파일 업로드
    with open('back/test.txt', 'rb') as f:
        file = f.read()
        file_id = upload_resume("koo", "이력서 예시", file)
        fake_record.resume_file_id = file_id
        upload_record("koo", "jd", "questions", "filename", file)

    # 파일 읽기
    user_files = read_resume("koo")
    for file in user_files:
        print(file)

    # 파일 삭제
    delete_resume("koo", "0"*24)

if __name__ == "__main__":
    main()