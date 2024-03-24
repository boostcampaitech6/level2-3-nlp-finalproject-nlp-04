import os
import sys
from typing import Optional

import requests
import uvicorn
from fastapi import (BackgroundTasks, Cookie, FastAPI, Request, Response,
                     WebSocket)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from share_var import get_shared_var, set_shared_var  # 공유 변수 관련 함수 불러오기

sys.path.append("./")
sys.path.append("./front")
sys.path.append("./back")

from back.config import *
from back.kakao import router as kakao_router  # 카카오 로그인 라우터 불러오기
from back.mongodb import router as mongo_router  # MongoDB 라우터 불러오기
from back.streamlit_control import (check_port,  # streamlit 관련 함수 불러오기
                                    run_streamlit_app)

set_shared_var("NEXT_PATH", "")  # 다음 이동 페이지 초기화
MY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "front", "jobits"
)  # 필요한 값에 접근하기 위해 경로 설정
ACCESS_TOKEN = None  # 토큰 저장
ID_TOKEN = None  # ID 토큰 : 로그인 여부 확인용

# redirect URI 자동 설정
app = FastAPI(docs_url="/documentation", redoc_url=None)
app.include_router(kakao_router, prefix="/kakao")
app.include_router(mongo_router, prefix="/users")
templates = Jinja2Templates(directory="front/templates")  # 템플릿 폴더 지정(HTML 파일 저장 폴더)

origins = [
    f"http://{INSIDE_IP}:{PORT}",
    f"http://{OUTSIDE_IP}:{PORT}" f"http://{OUTSIDE_IP}:{STREAMLIT_PORT}" f"http://localhost:{PORT}",
]
app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json("FAST API")
    # return


# 미들웨어 : 모든 Path 에서 동작
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response


# 첫 시작 페이지
@app.get("/")
def read_root():
    return RedirectResponse(url=f"http://{OUTSIDE_IP}:{STREAMLIT_PORT}")


@app.get("/launch_streamlit_app")
async def launch_streamlit_app(background_tasks: BackgroundTasks):

    background_tasks.add_task(run_streamlit_app)  # 백그라운드로 streamlit 실행 (내부에서 포트 개방여부 확인)

    NEXT_PATH = get_shared_var("NEXT_PATH")  # 공유 변수에서 다음 이동 페이지 경로 가져오기

    streamlit_url = f"http://{OUTSIDE_IP}:{STREAMLIT_PORT}/{NEXT_PATH}"  # streamlit url 실행 시 띄우는 주소

    return RedirectResponse(url=streamlit_url)


@app.post("/cookie-and-object/")
def create_cookie(response: Response):
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return {"message": "Come to the dark side, we have cookies"}


@app.get("/cookie/")
def create_cookie():
    content = {"message": "Come to the dark side, we have cookies"}
    response = JSONResponse(content=content)
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response


class AccessToken(BaseModel):
    access_token: str


@app.post("/items")
async def print_access_token(token: AccessToken):
    print("아이템 : Received access token:", token.access_token)
    access_token = token.access_token  # 현재 저장된 access_token 값

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)
        user_info = response.json()
        print("items에서 user_info :; ", user_info)
        # return user_info
    except Exception as e:
        return None

    set_shared_var("access_token", access_token)  # 공유 변수에 access_token 저장

    # TO DO :
    # user_info얻어온 후, mongoDB에 접속해서 해당 유저 정보 가져오기
    # (access_token으로 비교, 없으면 이메일로 찾아서 access_token 업데이트)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)  # 8000은 모두에게 배포로 설정

    # # HTTPS 연결용 - 구현 예정
    # uvicorn.run(app, host=INSIDE_IP, port=PORT, ssl_keyfile=KEY_FILE, ssl_certfile=CERT_FILE)
