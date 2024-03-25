import logging
import os
import sys

import requests
import streamlit as st
from PIL import Image

sys.path.append("./")
from back.streamlit_control import goto_login_page
from utils.util import get_image_base64

sys.path.append("./")
sys.path.append("./back")
from streamlit_extras.switch_page_button import switch_page

from back.config import OUTSIDE_IP, PORT  # IP, PORT 얻어오기 위해 import

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
st.session_state["FAV_IMAGE_PATH"] = os.path.join(DATA_DIR, "images/favicon.png")

st.set_page_config(
    page_title="Hello Jobits",  # 브라우저탭에 뜰 제목
    page_icon=Image.open(
        st.session_state.FAV_IMAGE_PATH
    ),  # 브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 로거 초기화
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


st.session_state["START_IMG"] = get_image_base64(os.path.join(DATA_DIR, "images/start_page.png"))
START_IMG = st.session_state.START_IMG

# 버튼들을 화면 오른쪽 아래에 배치하기 위해 CSS 스타일을 적용합니다.
st.markdown(
    f"""
    <style>
        .main {{
             background-image: url("data:image/png;base64,{START_IMG}");
             background-size:100% 100%;
             padding:0px;
             background-attachment: fixed;  /* 배경화면 이미지를 화면에 고정합니다. */
        }}
        [class="row-widget stButton"] button {{
             border : none;
             padding-left : 8rem;
             background-color: transparent;
        }}
        [class="row-widget stButton"] button:hover {{
             background-color: transparent;
        }}
        [class="row-widget stButton"] button>div {{
             display : flex;
             border-radius: 50px;
             background : #D9D9D9;
             filter: drop-shadow(0px 4px 4px rgba(0, 0, 0, 0.25));
             width : 9em;
             height : 2.5em;
             font-size : 40px;
             justify-content : center;
             font-family : 'Nanumsquare';
        }}
        [class="row-widget stButton"] button>div:hover{{
             transform : scale(1.1);
             background : #2D5AF0;
             transition : .5s;
        }}
        [class="row-widget stButton"] button>div>p {{
             font-size : 40px;
             font-weight: 700;
             color: #FFFFFF;
             text-align: center;
             margin : auto;
        }}
        [class="row-widget stButton"] button:first-child {{
            bottom: 40px; /* 시작하기 버튼을 현재 위치에서 위로 20만큼 이동 */
        }}
        
    </style>
    """,
    unsafe_allow_html=True,
)

if st.button("LOGIN(KAKAO)"):
    st.session_state["cur_user"] = "kakao"  # 사용자 상태 설정
    goto_login_page()

# 비회원 버튼
if st.button("GUEST"):
    st.session_state["cur_user"] = "guest"  # 사용자 상태 설정
    switch_page("home")
