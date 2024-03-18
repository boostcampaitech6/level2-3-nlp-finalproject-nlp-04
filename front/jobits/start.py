import logging
import sys
import streamlit as st
import requests
import pickle

sys.path.append("./")
sys.path.append("./back")
from back.config import *   #IP, PORT 얻어오기 위해 import

from streamlit_extras.switch_page_button import switch_page
from share_var import get_shared_var, set_shared_var  # 공유 변수 관련 함수 불러오기

# 로거 초기화
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



# 페이지 제목 및 설명
st.title('안녕자비스 - 면접 챗봇 서비스')
st.markdown('## 언제든 면접 연습을 할 수 있는 인공지능 면접 챗봇 서비스입니다.')


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


# 시작하기 버튼
if st.button('시작하기(카카오 로그인)'):
    goto_login_page(next_path='introduction')
    
# 비회원 버튼
if st.button('GUEST'):
    switch_page('introduction')
