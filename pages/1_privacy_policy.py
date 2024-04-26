import os
import sys
import requests

import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page

sys.path.append("./")
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from config import IMG_PATH, path, PORT
from src.util import read_prompt_from_txt, local_css
from back.managers.account_models import User, Record

st.session_state['FAV_IMAGE_PATH'] = os.path.join(IMG_PATH, "favicon.png")

st.set_page_config(
    page_title="Hello Jobits",  # 브라우저탭에 뜰 제목
    page_icon=Image.open(st.session_state.FAV_IMAGE_PATH),  # 브라우저 탭에 뜰 아이콘
    layout="wide",
    initial_sidebar_state="collapsed",
)

NEXT_PAGE = "user"

#### style css ####
MAIN_IMG = st.session_state.MAIN_IMG
LOGO_IMG = st.session_state.LOGO_IMG

st.title("안녕하세요, " + st.session_state.nickname + "님!")  # 사용자 이름을 받아서 화면에 출력합니다.

local_css(os.path.join(path, "front", "css", "background.css"))

privacy_policy = """
개인정보 보호법」제15조 및 제22조에 따라 아래와 같은 내용으로 본인의 개인정보를 수집‧이용하는데 동의합니다.

• 수집∙이용 목적
    : 개발자 모의면접 서비스 제공을 위한 유저 식별, 예상 질문 생성, 모의면접 진행 등의 서비스에 이용

• 수집ㆍ이용할 개인정보의 내용
    : 이름, 이메일, 이력서

• 보유 및 이용 기간
    : 수집‧이용 동의일로부터 6개월 이내

※ 귀하는 이에 동의를 거부할 수 있습니다.

다만 동의가 없을 경우 본 서비스 사용이 불가합니다."""

st.text_area("개인정보 처리방침", privacy_policy, height=300)

# 동의 여부를 라디오 버튼으로 선택
consent = st.radio("위 개인정보 처리방침에 동의하십니까?", ('동의', '동의하지 않음'))
st.session_state.agreement = consent

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
        is_privacy_policy_agreed=True
    )

if not st.session_state.is_logged_in:
    user = User(
        _id="GUEST",
        name="GUEST",
        access_token="GUEST",
        id_token="GUEST",
    )

if consent == '동의':
    st.session_state.is_privacy_policy_agreed = True
    
    if st.session_state.is_logged_in: # 카카오 로그인 사용자인 경우 동의 여부 저장
        user = requests.put(f"http://localhost:{PORT}/users/{st.session_state['user_email']}",json=user.model_dump(by_alias=True)).json()
    
    switch_page(NEXT_PAGE)
else:
    st.error("동의하지 않으셨습니다. 동의가 필요합니다.")