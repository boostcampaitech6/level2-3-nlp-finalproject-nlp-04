import asyncio
from datetime import datetime

from pymongo import errors
from bson.objectid import ObjectId

from managers.mongo_config import *
from managers.account_models import Record, User
from managers.file_manager import upload_resume, read_resume, delete_resume
from managers.db_operators import find_user_by_email, append_to_field


def create_record_instance(jd: str, file_id: str, questions: str) -> Record:
    return Record(
        jd=jd,
        resume_file_id=file_id,
        questions=questions,
        timestamp=int(datetime.now().timestamp())
    )


def upload_record(email: str, jd: str, questions: str, filename: str, file_data):
    user = find_user_by_email(email)
    if not user:
        return None
    
    # 파일 업로드
    file_id = upload_resume(email, filename, file_data)
    record = create_record_instance(jd, file_id, questions)
    
    success = append_to_field(email, "records", record)
    
    # 변경사항 확인
    if success:
        print(f"Added record with ID: {file_id} to user {email}")
    else:
        print(f"No changes made for user {email}")

    return record


def main():
    fake_user = User(_id="koo", name="희찬")
    try:
        collection.insert_one(fake_user.model_dump(by_alias=True))
    except errors.DuplicateKeyError:
        print("User already exists")

    with open('./back/test.txt', 'rb') as f:
        upload_record(email="koo", jd="이력서 예시", questions="질문 예시", filename="이력서 내용", file_data=f)


if __name__ == "__main__":
    main()
