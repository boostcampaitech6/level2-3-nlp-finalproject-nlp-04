from openai import OpenAI
import requests
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_chat import message
import json

import time
import traceback
import os
import re
import random
import sys
from start import redirect

sys.path.append("./back")
from back.config import * 

NEXT_PAGE = 'home'

st.title('헬로자비스 홈페이지')

def select_page():
    input_form, start_button = st.columns([1,2]) # 노션 컬럼처럼 열을 나눠서 할수있게 해주는것
# start_button = st.button
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

select_page()

# if 'kakao' in st.session_state and requests.get(f"http://{OUTSIDE_IP}:{PORT}/auth").status_code == 200:
#     # verify_url = f"http://{OUTSIDE_IP}:{PORT}/kakao"
#     # response = requests.get(verify_url, params={'kakao': st.session_state['kakao']})
#     # if response.status_code == 200:
#     select_page()
#     st.stop()
#     # else:
#     #     redirect(f"http://{OUTSIDE_IP}:{PORT}/kakao")
#     #     st.stop()


