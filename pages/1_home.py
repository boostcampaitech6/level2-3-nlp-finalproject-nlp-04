import os
import sys
import requests

import streamlit as st
from loguru import logger as _logger
from PIL import Image
from streamlit_extras.switch_page_button import switch_page

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from src.logger import DevConfig
from src.util import get_image_base64, read_gif
from config import OPENAI_API_KEY, IMG_PATH, PORT

from back.streamlit_control import get_info_from_kakao
from back.user_authorization import verify_token
from back.mongodb import User

NEXT_PAGE = "user"
is_logged_in = False

if "logger" not in st.session_state:
    # logru_logger(**config.config)
    config = DevConfig
    _logger.configure(**config.config)
    st.session_state["logger"] = _logger  # session_state에 ["logger"] 라는 키값을 추가하여 사용
    st.session_state["save_dir"] = config.SAVE_DIR

try:
    user_id = st.query_params["user_id"]
    token = st.query_params["access_token"]
except:
    user_id = None

# 쿼리 매개변수가 있다면, session_state에 설정
if user_id is not None:
    st.session_state["user_id"] = user_id
    st.session_state["access_token"] = token

    # 토큰 검증, 토큰 페이로드 디코딩
    is_logged_in, token_payload = verify_token(st.session_state["user_id"])

# 로그인 상태에 따라 사용자 정보 설정
if "user_id" in st.session_state and is_logged_in:
    user_info = get_info_from_kakao(st.session_state["access_token"])
else:
    user_info = {"properties": {"nickname": "GUEST"}, "kakao_account": {"email": "GUEST"}, "access_token": "GUEST"}


if "user_email" not in st.session_state:
    st.session_state["user_email"] = user_info["kakao_account"]["email"]
    print("user_email : ", st.session_state["user_email"])

if "nickname" not in st.session_state:
    st.session_state["nickname"] = user_info["properties"]["nickname"]
    print("nickname : ", st.session_state["nickname"])

if "access_token" not in st.session_state:
    st.session_state["access_token"] = user_info["access_token"]
    print("access_token : ", st.session_state["access_token"])

if "user_id" not in st.session_state:
    st.session_state["user_id"] = user_info["kakao_account"]["email"]
    print("user_id : ", st.session_state["user_id"])


if is_logged_in:
    # DB에 저장할 변수 설정
    last_login = token_payload["auth_time"]
    expires_at = token_payload["exp"]

    user = User(
        _id=st.session_state["user_email"],
        name=st.session_state["nickname"],
        access_token=st.session_state["access_token"],
        id_token=st.session_state["user_id"],
        last_login=last_login,
        expires_at=expires_at,
    )

    is_member = requests.get(f"http://localhost:{PORT}/kako/{st.session_state['user_email']}/exists")

    if is_member: # 이미 DB에 저장된 사용자라면
        user = requests.post(f"http://localhost:{PORT}/users/{user._id}",json=user.model_dump(by_alias=True),)

    elif not is_member: # DB에 저장된 사용자가 아니라면
        user.joined_at = last_login
        user = requests.post(f"http://localhost:{PORT}/users/",json=user.model_dump(by_alias=True),)


if "openai_api_key" not in st.session_state:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    st.session_state.openai_api_key = OPENAI_API_KEY

if "MAIN_IMG" not in st.session_state:
    st.session_state["MAIN_IMG"] = get_image_base64(os.path.join(IMG_PATH, "main_back.png"))

if "LOGO_IMG" not in st.session_state:
    st.session_state["LOGO_IMG"] = get_image_base64(os.path.join(IMG_PATH, "logo_square.png"))

if "FAV_IMAGE_PATH" not in st.session_state:
    st.session_state["FAV_IMAGE_PATH"] = os.path.join(IMG_PATH, "favicon.png")

if "LOGO_IMAGE_PATH" not in st.session_state:
    st.session_state["LOGO_IMAGE_PATH"] = os.path.join(IMG_PATH, "logo_square.png")

if "LOADING_GIF1" not in st.session_state:
    st.session_state["LOADING_GIF1"] = read_gif(os.path.join(IMG_PATH, "loading_interview_1.gif"))

if "LOADING_GIF2" not in st.session_state:
    st.session_state["LOADING_GIF2"] = read_gif(os.path.join(IMG_PATH, "loading_interview_2.gif"))

if "USER_ICON" not in st.session_state:
    st.session_state["USER_ICON"] = Image.open(os.path.join(IMG_PATH, "user_icon.png"))

if "user_name" not in st.session_state:
    st.session_state["user_name"] = "아무개"

if "temperature" not in st.session_state:
    st.session_state["temperature"] = 0

switch_page(NEXT_PAGE)
