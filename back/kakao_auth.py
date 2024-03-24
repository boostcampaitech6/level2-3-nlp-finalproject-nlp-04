# kakao_auth.py
from typing import Optional

import requests
from config import REDIRECT_URI, REST_API_KEY
from fastapi import APIRouter, Cookie, Request
from share_var import set_shared_var  # 공유 변수 관련 함수 불러오기
from starlette.responses import RedirectResponse
from user_authorization import verify_token

router = APIRouter()

ID_TOKEN = None  # ID 토큰 : 로그인 여부 확인용


@router.get("/kakao")
async def kakao():
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    return RedirectResponse(url)


@router.get("/auth")
async def kakaoAuth(code: Optional[str] = "NONE"):
    _url = f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&code={code}&redirect_uri={REDIRECT_URI}"
    _res = requests.post(_url)
    _result = _res.json()  # 사용자 정보 반환

    global ACCESS_TOKEN
    ACCESS_TOKEN = str(_result["access_token"])  # ACCESS 토큰 저장

    global ID_TOKEN
    ID_TOKEN = str(_result["id_token"])  # ID 토큰 저장

    end_point = "/launch_streamlit_app"  # 이동할 페이지 지정
    response = RedirectResponse(url=f"{end_point}?access_token={ACCESS_TOKEN}")

    # 쿠키 설정하기
    response.set_cookie(key="access_token", value=ACCESS_TOKEN)

    return response


@router.get("/kakaoLogout")
def kakaoLogout():
    url = "https://kapi.kakao.com/v1/user/unlink"
    headers = dict(Authorization=f"Bearer {ACCESS_TOKEN}")
    _res = requests.post(url, headers=headers)

    global ID_TOKEN
    ID_TOKEN = None  # ID 토큰 초기화

    set_shared_var("NEXT_PATH", "")  # 다음 페이지 이동 경로 초기화

    return {"logout": _res.json()}
