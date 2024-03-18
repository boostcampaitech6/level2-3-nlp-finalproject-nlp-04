# 백엔드 -> 여기서 streamlit 띄워볼거

# pip3 install fastapi
# pip3 install uvicorn

# run (1) : uvicorn main:app --reload
# run (2) : python3 main.py
import re
import socket
import subprocess
from typing import Optional
import os
import sys
from pathlib import Path
import httpx
import pickle

sys.path.append("./")
sys.path.   append("./front")
sys.path.append("./back")

import requests
import uvicorn
import yaml
from aiohttp import request

import httpx
from fastapi import BackgroundTasks, Cookie, Depends, FastAPI, HTTPException, Request, Response, WebSocket, status, Header, Query
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.templating import Jinja2Templates
from jinja2 import Template

from front.jobits.src.mypath import MY_PATH # MY_PATH 불러오기 - ~/level2-3-nlp-finalproject-nlp-04/front/jobits
from share_var import get_shared_var, set_shared_var  # 공유 변수 관련 함수 불러오기

import sys
sys.path.append('./')
sys.path.append('./front')
sys.path.append('./back')

from back.config import *
from back.kakao_auth import check_login, router as kakao_router  # 카카오 로그인 라우터 불러오기

# 필요한 값에 접근

ACCESS_TOKEN = None  # 토큰 저장
ID_TOKEN = None  # ID 토큰 : 로그인 여부 확인용

set_shared_var('NEXT_PATH', '')  # 다음 이동 페이지 초기화

# redirect URI 자동 설정
app = FastAPI(docs_url="/documentation", redoc_url=None)
app.include_router(kakao_router)
templates = Jinja2Templates(directory="front/templates")  # 템플릿 폴더 지정(HTML 파일 저장 폴더)

# CORS
from fastapi.middleware.cors import CORSMiddleware

origins = [
    f"http://{INSIDE_IP}:{PORT}",
    f"http://localhost:{PORT}",
    f"http://127.0.01:{PORT}",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json("FAST API")
    data = await websocket.receive_text()
    return

# 미들웨어 : 모든 Path 에서 동작
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # print("전처리")
    response = await call_next(request)
    return response

# 첫 소개 페이지
@app.get("/")
def read_root():
    return RedirectResponse(url='/launch_streamlit_app')


@app.get("/launch_streamlit_app")
async def launch_streamlit_app(background_tasks: BackgroundTasks):

    # FastAPI의 백그라운드 작업을 사용하여 Streamlit 애플리케이션을 실행합니다.
    if check_port(STREAMLIT_PORT):
        background_tasks.add_task(run_streamlit_app)
    

    NEXT_PATH = get_shared_var('NEXT_PATH')
    

    
    streamlit_url = f"http://{OUTSIDE_IP}:{STREAMLIT_PORT}/{NEXT_PATH}"  # streamlit url 실행 시 띄우는 주소
    print(streamlit_url)
    
    return RedirectResponse(url=streamlit_url)


#introduction 페이지
def run_streamlit_app():
    # 여기에 Streamlit 애플리케이션 실행 코드를 작성합니다.
    # 예를 들어, subprocess 모듈을 사용하여 Streamlit 앱을 실행할 수 있습니다.
    subprocess.run(
        [
            "streamlit",
            "run",
            MY_PATH + "/start.py",
            "--server.port",
            str(STREAMLIT_PORT)
        ]
    )


# 포트 상태 확인 - True : 열린 상태, False : 닫힌 상태
def check_port(port):
     # 소켓 생성
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 주어진 호스트와 포트에 연결 시도
        result = sock.connect_ex(('localhost', port))
        # 연결 시도 결과를 확인하여 포트 상태 반환
        if result != 0:
            return True
        else:
            return False    
      


if __name__ == "__main__":
    uvicorn.run(app, host=INSIDE_IP, port=PORT)  # 8000은 모두에게 배포로 설정

    # # HTTPS 연결용 - 구현 예정
    #uvicorn.run(app, host=INSIDE_IP, port=PORT, ssl_keyfile=KEY_FILE, ssl_certfile=CERT_FILE)
