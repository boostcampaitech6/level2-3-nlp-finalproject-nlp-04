# streamlit 관련 함수 모음
import socket
import subprocess
import threading
from time import sleep

import requests
import streamlit as st

from config import *


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


lock = threading.Lock()


def get_info_from_kakao(access_token):
    # 카카오 사용자 정보 가져오기

    lock.acquire()  # 락 획득

    try:
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get("https://kapi.kakao.com/v2/user/me", headers=headers)
        user_info = response.json()
    finally:
        lock.release()  # 락 해제

    return user_info


# 로그인 페이지로 이동하는 함수(streamlit)
# 이미 로그인 되어있으면 자동으로 다음 페이지로 이동
def goto_login_page():

    url = f"http://{OUTSIDE_IP}:{PORT}/kakao/login"
    res_kakaologin = requests.get(url)
    url = res_kakaologin.url
    st.markdown(f'<meta http-equiv="refresh" content="0;URL={url}">', unsafe_allow_html=True)
