import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_chat import message

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

        if start_button.button('예상 질문 확인하기'):
            switch_page(NEXT_PAGE)
            st.session_state.logger.info(f"check_essential | Pass")
                
                
        if start_button.button('모의면접 시작하기'):
            switch_page(NEXT_PAGE)
            st.session_state.logger.info(f"check_essential | Pass")
