import os
import streamlit as st
from utils.util import load_chain
from streamlit_chat import message
from time import sleep
from streamlit_extras.switch_page_button import switch_page
from PIL import Image

NEXT_PAGE = 'question_list'

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
st.session_state['FAV_IMAGE_PATH'] = os.path.join(DATA_DIR,'images/favicon.png')
st.set_page_config(
     page_title="Hello Jobits", # 브라우저탭에 뜰 제목
     
     page_icon=Image.open(st.session_state.FAV_IMAGE_PATH), #브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드 
     layout="wide",
     initial_sidebar_state="collapsed"
)

st.title('Hello-JobIts 모의면접 🤖')

if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = 0
if 'count' not in st.session_state:
    st.session_state.count = 0
if 'plus' not in st.session_state:
    st.session_state.plus = 0
if 'tail' not in st.session_state:
    st.session_state.tail = ''
if 'chain' not in st.session_state:
    st.session_state.chain = None
if 'messages' not in st.session_state:
        st.session_state['messages'] = [{"role": "assistant",
                                        "content": "안녕하세요, 면접 시작하도록 하겠습니다."}]
for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            

questions = st.session_state.main_question
            
# 사용자 입력 받기
if st.session_state.plus == 0:
    if len(questions) > st.session_state.current_question_idx:
        with st.chat_message('assistant'):
            st.markdown(questions[st.session_state.current_question_idx]) # 질문 뽑기
    if query := st.chat_input('답변을 입력해주세요. '):
        st.session_state.messages.append({"role": "assistant", "content": questions[st.session_state.current_question_idx]})
        # 질문이 남아 있다면 입력 받기
        if len(questions) > st.session_state.current_question_idx:
            st.session_state.messages.append({"role": "user", "content": query})
            # 사용자 입력 채팅으로 출력하기
            with st.chat_message('user'):
                st.markdown(query)
            # 다음 질문 기다리기
            with st.chat_message('assistant'):
                with st.spinner("답변을 작성중입니다..."):
                    sleep(1) # 로딩 화면 보여주기
                result = '답변 감사합니다'
                st.session_state.feedback = result
                st.markdown(result)
            st.session_state.messages.append({"role": "assistant", "content": result})
            # st.session_state.current_question_idx += 1
            st.session_state.plus = 1
        if st.session_state.plus == 1:
            st.session_state.chain = load_chain(questions[st.session_state.current_question_idx])
            with st.chat_message('assistant'):
                st.session_state.tail = st.session_state.chain.predict(input = query)
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.tail})
                st.markdown(st.session_state.tail)
        elif len(questions) > st.session_state.current_question_idx + 1:
            st.session_state.current_question_idx += 1
            with st.chat_message('assistant'):
                st.markdown(questions[st.session_state.current_question_idx]) # 질문 뽑기
                
elif st.session_state.plus == 1:
    st.session_state.count += 1
    # with st.chat_message('assistant'):
    #     st.markdown(lang(st.session_state.count, questions[st.session_state.current_question_idx]))
    if query := st.chat_input('답변을 입력해주세요. '):
        with st.chat_message('user'):
                st.markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})
    if st.session_state.count != 2:
        with st.chat_message('assistant'):
            plus_result = "꼬리질문 답변 감사합니다."
            st.markdown(plus_result)
        with st.chat_message('assistant'):
            st.session_state.tail = st.session_state.chain.predict(input = query)
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.tail})
            st.markdown(st.session_state.tail)
            
        st.session_state.messages.append({"role": "assistant", "content": plus_result})
    # 준비된 질문을 다 했는지 확인
    if st.session_state.count == 2:
        st.session_state.count = 0
        st.session_state.plus = 0
        st.success(":짠: 모든 꼬리질문에 대한 답변을 완료했습니다.")
        if len(questions) > st.session_state.current_question_idx + 1:
            with st.chat_message('assistant'):
                st.session_state.current_question_idx += 1
                st.markdown(questions[st.session_state.current_question_idx])
    elif st.session_state.tail == '다음 질문으로 넘어가겠습니다.':
        st.session_state.count = 0
        st.session_state.plus = 0
        st.success(":짠: 모든 꼬리질문에 대한 답변을 완료했습니다.")
        if len(questions) > st.session_state.current_question_idx + 1:
            with st.chat_message('assistant'):
                st.session_state.current_question_idx += 1
                st.markdown(questions[st.session_state.current_question_idx])
        else:
            st.success(":짠: 모든 질문에 대한 답변을 완료했습니다.")
            # 결과 분석 페이지 가기
            if st.button("결과 보러 가기"):
                switch_page(NEXT_PAGE)  