import logging
import streamlit as st
import webbrowser

# 로거 초기화
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# 페이지 제목 및 설명
st.title('안녕자비스 - 면접 챗봇 서비스')
st.markdown('## 언제든 면접 연습을 할 수 있는 인공지능 면접 챗봇 서비스입니다.')

# 시작하기 버튼
if st.button('시작하기'):
    url = 'http://223.130.163.221:8001/launch_streamlit_app'
    webbrowser.open_new_tab(url)  # url로 이동
