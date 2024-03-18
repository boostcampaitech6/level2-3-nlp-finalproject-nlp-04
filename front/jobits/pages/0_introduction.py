from openai import OpenAI
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_chat import message
import json

import time
import traceback
import os
import re
import random

NEXT_PAGE = 'home'

st.title('헬로자비스 홈페이지')

## input_form
input_form, start_button = st.columns([1,2]) # 노션 컬럼처럼 열을 나눠서 할수있게 해주는것



## start_button
with start_button:
        start_button.markdown(f''' 
                              <div class = 'main_message'> JOBits <br></div> 
                              ''', 
                              unsafe_allow_html=True )
        #
        ### 필요사항 따라 버튼 클릭시 안내 문구 생성
        if start_button.button('예상 질문 확인하기'):
            ### 유저 고유 폴더 생성
            
            # if check_list:
            #     start_button.markdown(f'''
            #                           <p class = 'check_message'>{', '.join(check_list)}{josa[-1]} 필요해요! </p>
            #                           ''',
            #                           unsafe_allow_html=True)
            # else:
            switch_page(NEXT_PAGE)
            st.session_state.logger.info(f"check_essential | Pass")
                
                
        if start_button.button('모의면접 시작하기'):
            ### 유저 고유 폴더 생성
            # if check_list:
            #     start_button.markdown(f'''
            #                           <p class = 'check_message'>{', '.join(check_list)}{josa[-1]} 필요해요! </p>
            #                           ''',
            #                           unsafe_allow_html=True)
            # else:
            switch_page(NEXT_PAGE)
            st.session_state.logger.info(f"check_essential | Pass")
