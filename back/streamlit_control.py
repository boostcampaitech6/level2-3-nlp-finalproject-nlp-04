# streamlit 관련 함수 모음
import socket
import subprocess
from back.config import *

MY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "front", "jobits")   # 필요한 값에 접근하기 위해 경로 설정

#시작 페이지 띄우기
def run_streamlit_app():   
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
      