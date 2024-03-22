import os
import sys
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


# 사용자 정보 저장(session_state)
response = requests.get("http://" + OUTSIDE_IP + ":" + str(PORT) + "/user_info")
user_info = response.json()

get_cookie_url = "http://" + OUTSIDE_IP + ":" + str(PORT) + "/items"

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
    cookies = {"access_token": "your_access_token_here"}  # 쿠키 이름과 값을 적절히 설정하세요
    token_response = requests.get(get_cookie_url, cookies=cookies)
    user_info['access_token'] = token_response.json()['access_token']
    print("불러온 사용자 access 토큰 : ", token_response.json(), user_info['access_token']) 






# # HTML 컴포넌트에 JavaScript 코드를 삽입하여 실행
# st.write("""
#     <script>
#     // GET 요청을 보낼 URL
# var url = """+get_cookie_url+""";

# // GET 요청 보내기
# fetch(url)
#     .then(response => {
#         // 서버 응답이 성공적으로 도착한 경우
#         if (response.ok) {
#             // JSON 형식으로 응답을 파싱하여 반환
#             return response.json();
#         }
#         // 서버 응답이 에러인 경우
#         throw new Error('Network response was not ok');
#     })
#     .then(data => {
#         // JSON 데이터를 사용하여 처리
#         console.log(data);
#     })
#     .catch(error => {
#         // 오류 처리
#         console.error('There was a problem with the fetch operation:', error);
#     });

#     </script>
# """)




if "user_email" not in st.session_state:
    st.session_state['user_email'] = user_info['kakao_account']['email']

if "nickname" not in st.session_state:
    st.session_state['nickname'] = user_info['properties']['nickname']

if "access_token" not in st.session_state:  # access_token 설정
    st.session_state['access_token'] = user_info['access_token']


switch_page(NEXT_PAGE)