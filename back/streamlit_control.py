# streamlit 관련 함수 모음
import socket
import subprocess
import threading
from time import sleep
import requests
import streamlit as st
from back.config import *
from back.share_var import get_shared_var, set_shared_var

MY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "front")   # 필요한 값에 접근하기 위해 경로 설정

#시작 페이지 띄우기
def run_streamlit_app():
    if check_port(STREAMLIT_PORT):  # 포트 개방 여부 확인
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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   
    result = sock.connect_ex(('localhost', port))
    
    if result != 0:
        return True
    else:
        return False    
      
# 클라이언트 측에서 쿠키를 읽어오는 코드(streamlit에서 작동)
def read_cookie_from_client():
    # JavaScript 코드를 포함하는 HTML 문자열
    # Python 변수에서 JavaScript 코드로 URL 값 전달
    url = f"http://{OUTSIDE_IP}:{PORT}/items"
    
    
    javascript_code = f"""
        <script>
            // 기능 : /items에 cookie와 함께 POST 요청을 보내는 코드
         
            // 클라이언트 측의 쿠키를 읽어오는 함수
            function getCookie(name) {{
                const value = `; ${{document.cookie}}`;
                const parts = value.split(`; ${{name}}=`);
                if (parts.length === 2) return parts.pop().split(';').shift();
            }}

            // 쿠키 읽기 예시
            const accessToken = getCookie('access_token');
            console.log('안녕 자바스크립트, Access Token:', accessToken);
            
            
            // POST 요청 보내기
            const url = "{url}";  // Python 변수를 JavaScript 변수로 설정
            // 서버에 HTTP 요청 보내기
            fetch(url, {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{ access_token: accessToken }}),
            }})
            .then(response => {{
                if (!response.ok) {{
                    throw new Error('네트워크 오류 발생');
                }}
                return response.json();
            }})
            .then(data => {{
                console.log('서버에서 받은 데이터:', data);
            }})
            .catch(error => {{
                console.error('요청 실패:', error);
            }});
            
        </script>
    """

    # HTML 컴포넌트를 사용하여 JavaScript 코드를 포함
    st.components.v1.html(javascript_code) 


def get_info_from_kakao(access_token):
    # 카카오 사용자 정보 가져오기
    headers = { "Authorization": f"Bearer {access_token}" }

    response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)
    user_info = response.json()
    return user_info

# 락 객체 생성
lock = threading.Lock()

def get_user_info():

    # 락 획득
    lock.acquire()
        
    try:
        # 임계 영역에 대한 코드 실행
        read_cookie_from_client() # user -> fastAPI한테 쿠키 전달

        sleep(2)    # read_cookie_from_client()가 실행되는 동안 대기

        access_token = get_shared_var('access_token')  # fastAPI에서 받은 access_token

        set_shared_var('NEXT_PATH', 'home')  # 바로 공유변수 원래대로 되돌리기

        user_info = get_info_from_kakao(access_token)    # kakao API로 사용자 정보 가져오기

    finally:
        # 락 해제
        lock.release()
        
    return user_info