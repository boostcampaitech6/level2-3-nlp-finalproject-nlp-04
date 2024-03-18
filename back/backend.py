import os
import uvicorn
from fastapi import BackgroundTasks, FastAPI, Request, WebSocket
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from share_var import get_shared_var, set_shared_var  # 공유 변수 관련 함수 불러오기

import sys
sys.path.append('./')
sys.path.append('./front')
sys.path.append('./back')

from back.config import *
from back.kakao_auth import router as kakao_router  # 카카오 로그인 라우터 불러오기
from back.streamlit_control import run_streamlit_app, check_port  # streamlit 관련 함수 불러오기

set_shared_var('NEXT_PATH', '')  # 다음 이동 페이지 초기화
MY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "front", "jobits")   # 필요한 값에 접근하기 위해 경로 설정
ACCESS_TOKEN = None  # 토큰 저장
ID_TOKEN = None  # ID 토큰 : 로그인 여부 확인용

# redirect URI 자동 설정
app = FastAPI(docs_url="/documentation", redoc_url=None)
app.include_router(kakao_router)
templates = Jinja2Templates(directory="front/templates")  # 템플릿 폴더 지정(HTML 파일 저장 폴더)

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
    # data = await websocket.receive_text()
    return

# 미들웨어 : 모든 Path 에서 동작
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response

# 첫 소개 페이지
@app.get("/")
def read_root():
    return RedirectResponse(url='/launch_streamlit_app')


@app.get("/launch_streamlit_app")
async def launch_streamlit_app(background_tasks: BackgroundTasks):
    if check_port(STREAMLIT_PORT):  # 포트 개방 여부 확인
        background_tasks.add_task(run_streamlit_app)

    NEXT_PATH = get_shared_var('NEXT_PATH')

    streamlit_url = f"http://{OUTSIDE_IP}:{STREAMLIT_PORT}/{NEXT_PATH}"  # streamlit url 실행 시 띄우는 주소
    print(streamlit_url)
    
    return RedirectResponse(url=streamlit_url)


if __name__ == "__main__":
    uvicorn.run(app, host=INSIDE_IP, port=PORT)  # 8000은 모두에게 배포로 설정

    # # HTTPS 연결용 - 구현 예정
    #uvicorn.run(app, host=INSIDE_IP, port=PORT, ssl_keyfile=KEY_FILE, ssl_certfile=CERT_FILE)
