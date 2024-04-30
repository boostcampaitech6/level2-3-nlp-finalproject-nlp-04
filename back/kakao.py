import secrets
from typing import Optional

from config import CLIENT_ID, CLIENT_SECRET, OUTSIDE_IP, PORT, STREAMLIT_PORT
from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi_oauth_client import OAuthClient
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from user_authorization import verify_token

router = APIRouter()

templates = Jinja2Templates(directory="templates")

REDIRCTION_URI = f"http://{OUTSIDE_IP}:{PORT}/kakao/callback"

naver_client = OAuthClient(
    client_id="your_client_id",
    client_secret_id="your_client_secret_id",
    redirect_uri="your_callback_uri",
    authentication_uri="https://nid.naver.com/oauth2.0",
    resource_uri="https://openapi.naver.com/v1/nid/me",
    verify_uri="https://openapi.naver.com/v1/nid/verify",
)

kakao_client = OAuthClient(
    client_id=CLIENT_ID,
    client_secret_id=CLIENT_SECRET,
    redirect_uri=REDIRCTION_URI,
    authentication_uri="https://kauth.kakao.com/oauth",
    resource_uri="https://kapi.kakao.com/v2/user/me",
    verify_uri="https://kapi.kakao.com/v1/user/access_token_info",
)


def get_oauth_client():  # provider: str = Query(..., regex="naver|kakao") = "kakao"):
    # if provider == "naver":
    #     return naver_client
    # elif provider == "kakao":
    #     return kakao_client
    return kakao_client


def get_authorization_token(authorization: str = Header(...)) -> str:
    scheme, _, param = authorization.partition(" ")
    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return param


async def authenticate_user(
    oauth_client: OAuthClient = Depends(get_oauth_client),
    access_token: str = Depends(get_authorization_token),
):
    if not await oauth_client.is_authenticated(access_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/login")
async def login(oauth_client=Depends(get_oauth_client)):
    state = secrets.token_urlsafe(32)
    login_url = oauth_client.get_oauth_login_url(state=state)
    # return {"login_url": login_url}
    return RedirectResponse(url=login_url)


@router.get("/callback")
async def callback(code: str, state: Optional[str] = None, oauth_client=Depends(get_oauth_client)):
    token_response = await oauth_client.get_tokens(code, state)
    jwt = token_response["id_token"]

    return RedirectResponse(
        url=f"https://hello-jobits.com/home/?user_id={jwt}&access_token={token_response['access_token']}"    # 도메인 이름으로 접속
    )


@router.get("/refresh")
async def callback(
    oauth_client=Depends(get_oauth_client),
    refresh_token: str = Depends(get_authorization_token),
):
    token_response = await oauth_client.refresh_access_token(refresh_token=refresh_token)

    return {"response": token_response}


# @router.get("/logout")
# def logout():
#     url = "https://kapi.kakao.com/v1/user/unlink"
#     headers = dict(Authorization=f"Bearer {ACCESS_TOKEN}")
#     _res = requests.post(url, headers=headers)

#     global ID_TOKEN
#     ID_TOKEN = None  # ID 토큰 초기화

#     set_shared_var('NEXT_PATH', '') # 다음 페이지 이동 경로 초기화

#     return {"logout": _res.json()}


@router.get("/user", dependencies=[Depends(authenticate_user)])
async def get_user(
    oauth_client=Depends(get_oauth_client),
    access_token: str = Depends(get_authorization_token),
):
    user_info = await oauth_client.get_user_info(access_token=access_token)
    return {"user": user_info}
