import os
import sys
from time import sleep
import requests
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from loguru import logger as _logger

sys.path.append("./")
from utils.logger import DevConfig
from utils.util import get_image_base64,read_gif
from PIL import Image

from back.config import OPENAI_API_KEY, OUTSIDE_IP, PORT     #KEY, IP, PORT 얻어오기 위해 import

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OPENAI_API_KEY_DIR = 'api_key.txt'
NEXT_PAGE = 'user'

if "logger" not in st.session_state:
    # logru_logger(**config.config)
    config = DevConfig
    _logger.configure(**config.config)
    st.session_state["logger"] = _logger # session_state에 ["logger"] 라는 키값을 추가하여 사용
    st.session_state["save_dir"] = config.SAVE_DIR

if "openai_api_key" not in st.session_state:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    st.session_state.openai_api_key = OPENAI_API_KEY

if "MAIN_IMG" not in st.session_state:
    st.session_state['MAIN_IMG'] = get_image_base64(os.path.join(DATA_DIR,'images/main_back.png'))

if "LOGO_IMG" not in st.session_state:
    st.session_state['LOGO_IMG'] = get_image_base64(os.path.join(DATA_DIR,'images/logo_square.png'))
    
if "FAV_IMAGE_PATH" not in st.session_state:
    st.session_state['FAV_IMAGE_PATH'] = os.path.join(DATA_DIR,'images/favicon.png')

if "LOGO_IMAGE_PATH" not in st.session_state:
    st.session_state['LOGO_IMAGE_PATH'] = os.path.join(DATA_DIR,'images/logo_square.png')

if "LOADING_GIF1" not in st.session_state:
    st.session_state['LOADING_GIF1'] = read_gif(os.path.join(DATA_DIR,'images/loading_interview_1.gif'))
    
if "LOADING_GIF2" not in st.session_state:
    st.session_state['LOADING_GIF2'] = read_gif(os.path.join(DATA_DIR,'images/loading_interview_2.gif'))

if "USER_ICON" not in st.session_state:
    st.session_state['USER_ICON'] = Image.open(os.path.join(DATA_DIR, 'images/user_icon.png'))

if "user_name" not in st.session_state:
    st.session_state['user_name'] = '아무개'
    
if "temperature" not in st.session_state:
    st.session_state['temperature'] = 0

   
   
# 클라이언트 측에서 쿠키를 읽어오는 코드(streamlit에서 작동)
def read_cookie_from_client():
    # JavaScript 코드를 포함하는 HTML 문자열
    # Python 변수에서 JavaScript 코드로 URL 값 전달
    url = f"http://{OUTSIDE_IP}:{PORT}/items"
    
    
    javascript_code = f"""
        <script>
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
 
print("read_cookie_from_client() 실행")  

read_cookie_from_client() # user -> fastAPI한테 쿠키 전달

sleep(3)    # read_cookie_from_client()가 실행되는 동안 대기

user_info = {
'properties': {
    'nickname': 'GUEST'
},
'kakao_account': {
    'email': 'GUEST'
},
'access_token': 'GUEST'
}



#user_info = None
#get_cookie_url = "http://" + OUTSIDE_IP + ":" + str(PORT) + "/items"

if 'properties' not in user_info: # GUEST인 경우 처리
    user_info = {
    'properties': {
        'nickname': 'GUEST'
    },
    'kakao_account': {
        'email': 'GUEST'
    },
    'access_token': 'GUEST'
}
else:   # 로그인 한 사용자 -> access토큰 설정
    # 사용자 access_token 불러오기
    # token_response = read_cookie_from_client()
    # 쿠키 가져오기
    # print("불러온 사용자 access 토큰 : ", token_response.json(), user_info['access_token'])
    
    pass


   
# import extra_streamlit_components as stx
# cookie_manager = stx.CookieManager() 
# value = cookie_manager.get(cookie='access_token')
# print("cookie value : ", value)


if "user_email" not in st.session_state:
    st.session_state['user_email'] = user_info['kakao_account']['email']

if "nickname" not in st.session_state:
    st.session_state['nickname'] = user_info['properties']['nickname']

if "access_token" not in st.session_state:  # access_token 설정
    st.session_state['access_token'] = user_info['access_token']


switch_page(NEXT_PAGE)