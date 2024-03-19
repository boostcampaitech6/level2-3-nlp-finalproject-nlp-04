import logging
import sys
import streamlit as st
import requests
from PIL import Image

from utils.util import get_image_base64

sys.path.append("./")
sys.path.append("./back")
from back.config import *   #IP, PORT 얻어오기 위해 import

from streamlit_extras.switch_page_button import switch_page
from share_var import set_shared_var  # 공유 변수 관련 함수 불러오기

st.session_state['FAV_IMAGE_PATH'] = os.path.join(DATA_DIR,'images/favicon.png')
st.set_page_config(
     page_title="Hello Jobits", # 브라우저탭에 뜰 제목
     
     page_icon=Image.open(st.session_state.FAV_IMAGE_PATH), #브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드 
     layout="wide",
     initial_sidebar_state="collapsed"
)

# 로거 초기화
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 로그인 페이지로 이동하는 함수(streamlit)
# 이미 로그인 되어있으면 자동으로 다음 페이지로 이동
def goto_login_page(next_path):
    
    #다음 이동 페이지 경로 저장
    set_shared_var('NEXT_PATH', next_path)
    
    url = f"http://{OUTSIDE_IP}:{PORT}/kakao"
    response = requests.get(url)
    
    
    if response.status_code == 200:
        st.markdown(f'<meta http-equiv="refresh" content="0;URL={url}">', unsafe_allow_html=True)
        st.stop()  # 현재 페이지 중지
    else:
        st.error('리디렉션 실패')


st.session_state['START_IMG'] = get_image_base64(DATA_DIR + '/images/start_page.png')
START_IMG = st.session_state.START_IMG
# 버튼들을 화면 오른쪽 아래에 배치하기 위해 CSS 스타일을 적용합니다.
st.markdown(f"""
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
    unsafe_allow_html=True
)

# 시작하기 버튼
if st.button('LOGIN(KAKAO)'):
    goto_login_page(next_path='home')
    
# 비회원 버튼
if st.button('GUEST'):
    switch_page('home')
