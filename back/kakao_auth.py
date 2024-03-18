# kakao_auth.py
from typing import Optional

import jwt
import requests
from config import REDIRECT_URI, REST_API_KEY
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from starlette.responses import RedirectResponse

from user_authorization import verify_token

router = APIRouter()

ACCESS_TOKEN = None  # 토큰 저장
ID_TOKEN = None  # ID 토큰 : 로그인 여부 확인용


@router.get("/kakao")
async def kakao(response: Response):
    url = f"https://kauth.kakao.com/oauth/authorize?client_id={REST_API_KEY}&response_type=code&redirect_uri={REDIRECT_URI}"
    return RedirectResponse(url)


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
    headers = dict(Authorization=f"Bearer {ACCESS_TOKEN}")
    return RedirectResponse(url=f"{end_point}", headers=headers)

# # 카카오 콜백 처리 및 액세스 토큰 저장
# @router.get("/auth")
# async def kakao_auth(response: Response, code: Optional[str] = None):
#     if code is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing authorization code")
    
#     token_url = "https://kauth.kakao.com/oauth/token"
#     token_data = {
#         "grant_type": "authorization_code",
#         "client_id": REST_API_KEY,
#         "redirect_uri": REDIRECT_URI,
#         "code": code,
#     }
#     token_res = requests.post(token_url, data=token_data)
#     token_res_json = token_res.json()

#     if 'access_token' not in token_res_json:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to retrieve access token")

#     # 액세스 토큰을 안전한 쿠키에 저장
#     response.set_cookie(key="access_token", value=token_res_json["access_token"], httponly=True, secure=True, samesite='lax')
    
#     # 사용자를 안전한 페이지로 리디렉션
#     return RedirectResponse(url="/launch_streamlit_app")  # 사용자가 액세스할 수 있는 안전한 페이지

# # 보안이 적용된 페이지
# @router.get("/secure_page")
# async def secure_page(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=["RS256"])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
#     except jwt.JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
#     # 여기에서 사용자의 세션 정보를 검증하고 필요한 데이터를 반환
#     return {"message": "Welcome to the secure page!"}

@router.get("/kakaoLogout")
def kakaoLogout(request: Request, response: Response):
    url = "https://kapi.kakao.com/v1/user/unlink"
    headers = dict(Authorization=f"Bearer {ACCESS_TOKEN}")
    _res = requests.post(url, headers=headers)
    response.set_cookie(key="kakao", value=None)

    global ID_TOKEN
    ID_TOKEN = None  # ID 토큰 초기화

    return {"logout": _res.json()}

def check_login():
    """
    ID 토큰을 검증하여 로그인 여부를 확인합니다.

    Returns:
        bool: 로그인 여부를 나타내는 불리언 값입니다.

    Raises:
        HTTPException: 로그인이 안 된 경우, 카카오 페이지로 리다이렉트합니다.
    """
    res, decoded_payload = verify_token(ID_TOKEN)
    return res
    # if res == False:
        # go_kakao()
        # raise HTTPException(
        #     status_code=status.HTTP_303_SEE_OTHER,
        #     headers={"Location": "/kakao"},
        # )


def go_kakao():
    return RedirectResponse(url="/kakao")
