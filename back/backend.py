# 백엔드 -> 여기서 streamlit 띄워볼거

# pip3 install fastapi
# pip3 install uvicorn

# run (1) : uvicorn main:app --reload
# run (2) : python3 main.py
import re
import subprocess
from typing import Optional
import os
import sys
from pathlib import Path

sys.path.append("./")
sys.path.append("./front")

import requests
import uvicorn
import yaml
from aiohttp import request
from fastapi import BackgroundTasks, Cookie, Depends, FastAPI, HTTPException, Request, Response, WebSocket, status, UploadFile, File, HTTPException
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.templating import Jinja2Templates
from jinja2 import Template


from front.pages import question_list  # 질문 생성 페이지
from config import *
from kakao_auth import check_login, router as kakao_router  # 카카오 로그인 라우터 불러오기
from user_authorization import verify_token  # 토큰 유효성 검사 함수 불러오기
from file_manager import upload_file, download_file

# 필요한 값에 접근

ACCESS_TOKEN = None  # 토큰 저장
ID_TOKEN = None  # ID 토큰 : 로그인 여부 확인용

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

    question_list.main()  # 질문 생성 페이지

    # json 띄우기
    return RedirectResponse(url='/introduction')
    return {"안녕자비스": "소개페이지 + '시작하기' 버튼 필요"}  # content-type: application/json


# # 메인 페이지
# @app.get("/mainpage", response_class=HTMLResponse)
# def read_root(request: Request, kakao: Optional[str] = Cookie(None)):

#     check_login()  # 로그인 체크 -> 안 된 경우 로그인 페이지로 리다이렉트

#     # 로그인이 된 경우 메인 페이지를 띄웁니다. -> HTML 띄우기
#     return templates.TemplateResponse("main_page.html", {"request": request, "안녕자비스": "Main화면"})

@app.get("/introduction")
async def introduction(background_tasks: BackgroundTasks):

    #check_login()  # 로그인 체크 -> 안 된 경우 로그인 페이지로 리다이렉트

    # FastAPI의 백그라운드 작업을 사용하여 Streamlit 애플리케이션을 실행합니다.
    background_tasks.add_task(run_streamlit_app)

    streamlit_url = f"http://{OUTSIDE_IP}:{STREAMLIT_PORT}"  # streamlit url 실행 시 띄우는 주소

    return RedirectResponse(url=streamlit_url)


#introduction 페이지
def run_streamlit_app():
    # 여기에 Streamlit 애플리케이션 실행 코드를 작성합니다.
    # 예를 들어, subprocess 모듈을 사용하여 Streamlit 앱을 실행할 수 있습니다.
    subprocess.run(
        [
            "streamlit",
            "run",
            "/dev/shm/level2-3-nlp-finalproject-nlp-04/front/0_introduction.py",
            "--server.port",
            str(STREAMLIT_PORT)
        ]
    )
    
#서비스 시작 페이지
def run_streamlit_app2():
    # 여기에 Streamlit 애플리케이션 실행 코드를 작성합니다.
    # 예를 들어, subprocess 모듈을 사용하여 Streamlit 앱을 실행할 수 있습니다.
    subprocess.run(
        [
            "streamlit",
            "run",
            "/dev/shm/level2-3-nlp-finalproject-nlp-04/front/1_home.py",
            "--server.port",
            str(STREAMLIT_PORT2)
        ]
    )    

@app.get("/launch_streamlit_app")
async def launch_streamlit_app(background_tasks: BackgroundTasks):

    #check_login()  # 로그인 체크 -> 안 된 경우 로그인 페이지로 리다이렉트

    # FastAPI의 백그라운드 작업을 사용하여 Streamlit 애플리케이션을 실행합니다.
    background_tasks.add_task(run_streamlit_app2)

    streamlit_url = f"http://{OUTSIDE_IP}:{STREAMLIT_PORT2}"  # streamlit url 실행 시 띄우는 주소

    return RedirectResponse(url=streamlit_url)


# @app.post("/email")
# async def receive_email(email: str):
#     return {"email": email}


# @app.post("/uploadfile/")
# async def upload_file_endpoint(email: str, file: UploadFile = File(...)):
#     file_id = upload_file(email, file)
#     return {"file_id": file_id}


# @app.get("/downloadfile/")
# async def download_file_endpoint(email: str):
#     file_content = download_file(email)
#     if file_content is None:
#         raise HTTPException(status_code=404, detail="File not found")
#     return {"file_content": file_content}


if __name__ == "__main__":
    uvicorn.run(app, host=INSIDE_IP, port=PORT)  # 8000은 모두에게 배포로 설정

    # # HTTPS 연결용
    # uvicorn.run(app, host=INSIDE_IP, port=PORT, ssl_keyfile=KEY_FILE, ssl_certfile=CERT_FILE)
