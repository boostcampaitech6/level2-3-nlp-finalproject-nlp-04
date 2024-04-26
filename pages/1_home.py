import os
import sys
import uuid
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
from back.managers.account_models import User, Record

NEXT_PAGE = "privacy_policy"
st.session_state.is_logged_in = False

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
    st.session_state.is_logged_in, st.session_state.token_payload = verify_token(st.session_state["user_id"])

# 로그인 상태에 따라 사용자 정보 설정
if "user_id" in st.session_state and st.session_state.is_logged_in:
    user_info = get_info_from_kakao(st.session_state["access_token"])
else:
    user_info = {"properties": {"nickname": "GUEST"}, "kakao_account": {"email": "GUEST"}, "access_token": "GUEST"}
    st.session_state["save_dir"] = os.path.join(st.session_state['save_dir'], str(uuid.uuid4()))    # GUEST 사용자 폴더 분리

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

if "openai_api_key" not in st.session_state:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    st.session_state.openai_api_key = OPENAI_API_KEY

if "FAV_IMAGE_PATH" not in st.session_state:
    st.session_state["FAV_IMAGE_PATH"] = os.path.join(IMG_PATH, "favicon.png")

if "LOADING_GIF1" not in st.session_state:
    st.session_state["LOADING_GIF1"] = read_gif(os.path.join(IMG_PATH, "loading_interview_1.gif"))

if "LOADING_GIF2" not in st.session_state:
    st.session_state["LOADING_GIF2"] = read_gif(os.path.join(IMG_PATH, "loading_interview_2.gif"))

if "temperature" not in st.session_state:
    st.session_state["temperature"] = 0

if "is_privacy_policy_agreed" not in st.session_state:
    st.session_state["is_privacy_policy_agreed"] = False

if "last_login" not in st.session_state:
    st.session_state["last_login"] = None

if "expires_at" not in st.session_state:
    st.session_state["expires_at"] = None

if st.session_state.is_logged_in:
    # DB에 저장할 변수 설정
    st.session_state.last_login = st.session_state.token_payload["auth_time"]
    st.session_state.expires_at = st.session_state.token_payload["exp"]

    user = User(
        _id=st.session_state["user_email"],
        name=st.session_state["nickname"],
        access_token=st.session_state["access_token"],
        id_token=st.session_state["user_id"],
        last_login=st.session_state.last_login,
        expires_at=st.session_state.expires_at,
        is_privacy_policy_agreed=st.session_state.is_privacy_policy_agreed,
    )

if not st.session_state.is_logged_in:
    user = User(
        _id="GUEST",
        name="GUEST",
        access_token="GUEST",
        id_token="GUEST",
    )

st.session_state.is_member = requests.get(f"http://localhost:{PORT}/users/{st.session_state['user_email']}/exists").json()

if not st.session_state.is_member: # DB에 저장된 사용자가 아니라면 DB에 저장
    user.joined_at = st.session_state.last_login
    user = requests.post(f"http://localhost:{PORT}/users/",json=user.model_dump(by_alias=True)).json()

elif st.session_state.is_member: # 이미 DB에 저장된 사용자라면 개인 정보 동의 여부 확인
    st.session_state.is_privacy_policy_agreed = requests.get(f"http://localhost:{PORT}/users/{st.session_state['user_email']}/privacy_policy").json()
    user = requests.put(f"http://localhost:{PORT}/users/{st.session_state['user_email']}",json=user.model_dump(by_alias=True)).json()

if st.session_state.is_privacy_policy_agreed: # 개인 정보 동의를 했다면 다음 페이지로 넘어가기
    NEXT_PAGE = "user"

switch_page(NEXT_PAGE)
