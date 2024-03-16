# kakao_auth.py
from typing import Optional

import requests
from config import REDIRECT_URI, REST_API_KEY
from fastapi import APIRouter, Request, Response
from starlette.responses import RedirectResponse

router = APIRouter()


@router.get("/kakao")
def kakao():
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    response = RedirectResponse(url)
    return response


@router.get("/auth")
async def kakaoAuth(response: Response, code: Optional[str] = "NONE"):
    _url = f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={REST_API_KEY}&code={code}&redirect_uri={REDIRECT_URI}"
    _res = requests.post(_url)
    _result = _res.json()
    response.set_cookie(key="kakao", value=str(_result["access_token"]))

    global ACCESS_TOKEN
    ACCESS_TOKEN = str(_result["access_token"])  # ACCESS 토큰 저장

    global ID_TOKEN
    ID_TOKEN = str(_result["id_token"])  # ID 토큰 저장

    end_point = "/launch_streamlit_app"  # 이동할 페이지 지정 > mainpage
    return RedirectResponse(url=f"{end_point}?access_token={ACCESS_TOKEN}")
    # return {"code":_result}


@router.get("/kakaoLogout")
def kakaoLogout(request: Request, response: Response):
    url = "https://kapi.kakao.com/v1/user/unlink"
    headers = dict(Authorization=f"Bearer {ACCESS_TOKEN}")
    _res = requests.post(url, headers=headers)
    response.set_cookie(key="kakao", value=None)

    global ID_TOKEN
    ID_TOKEN = None  # ID 토큰 초기화

    return {"logout": _res.json()}
