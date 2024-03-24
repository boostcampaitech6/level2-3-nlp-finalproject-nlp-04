import os
import sys
from time import sleep
import requests
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from loguru import logger as _logger
from back.share_var import get_shared_var, set_shared_var
from back.streamlit_control import get_info_from_kakao, get_user_info

sys.path.append("./")
from utils.logger import DevConfig
from utils.util import get_image_base64,read_gif
from PIL import Image

from back.config import OPENAI_API_KEY, OUTSIDE_IP, PORT     #KEY, IP, PORT 얻어오기 위해 import

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
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



if "cur_user" not in st.session_state: # 카카오 사용자 처리
    st.session_state['cur_user'] = 'kakao'
    user_info = get_user_info()
    
else:   # GUEST인 경우 처리
    
    user_info = {
    'properties': {
        'nickname': 'GUEST'
    },
    'kakao_account': {
        'email': 'GUEST'
    },
    'access_token': 'GUEST'
}

if "user_email" not in st.session_state:
    st.session_state['user_email'] = user_info['kakao_account']['email']

if "nickname" not in st.session_state:
    st.session_state['nickname'] = user_info['properties']['nickname']

# if "access_token" not in st.session_state:  # access_token 설정
#     st.session_state['access_token'] = user_info['access_token']


switch_page(NEXT_PAGE)