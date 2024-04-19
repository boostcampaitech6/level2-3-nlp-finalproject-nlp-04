from typing import Any, List, Optional
from pydantic import BaseModel, Field


class History(BaseModel):
    jd: str = ''                                # 입력한 채용공고
    resume_file_ids: Optional[Any] = None  # 입력한 이력서
    questions: str = None                       # 생성된 질문
    timestamp: int = None                       # Unix time으로 저장


class User(BaseModel):
    email: str = Field(..., alias="_id")        # _id 필드를 email로 alias
    name: str                                   # 이름
    access_token: str = None                    # OAuth2의 access_token
    id_token: str = None                        # OAuth2의 id_token(JWT)
    expires_at: Optional[int] = None # 언제 사용할까요? # 아직 사용하지 않음
    joined_at: Optional[int] = None             # 가입 날짜
    last_login: Optional[int] = None            # 마지막 로그인 시간
    history: Optional[List[History]] = []       # 사용자의 이력
    available_credits: Optional[int] = 3        # 무료로 사용 가능한 크레딧 # 사용하지 않음