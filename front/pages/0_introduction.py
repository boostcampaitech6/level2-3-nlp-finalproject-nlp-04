import os
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_chat import message
from PIL import Image
from back.config import DATA_DIR

NEXT_PAGE = 'home'

st.session_state['FAV_IMAGE_PATH'] = os.path.join(DATA_DIR,'images/favicon.png')
st.set_page_config(
     page_title="Hello Jobits", # 브라우저탭에 뜰 제목
     
     page_icon=Image.open(st.session_state.FAV_IMAGE_PATH), #브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드 
     layout="wide",
     initial_sidebar_state="collapsed"
)
st.title('헬로자비스 홈페이지')

## input_form
input_form, start_button = st.columns([1,2]) # 노션 컬럼처럼 열을 나눠서 할수있게 해주는것

## start_button
with start_button:
        start_button.markdown(f''' 
                              <div class = 'main_message'> JOBits <br></div> 
                              ''', 
                              unsafe_allow_html=True )

        if start_button.button('예상 질문 확인하기'):
            switch_page(NEXT_PAGE)
            st.session_state.logger.info(f"check_essential | Pass")
                
                
        if start_button.button('모의면접 시작하기'):
            switch_page(NEXT_PAGE)
            st.session_state.logger.info(f"check_essential | Pass")
