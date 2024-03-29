import os
import sys
from time import sleep

import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src.util import load_chain
from config import DATA_DIR, IMG_PATH
NEXT_PAGE = "question_list"

st.session_state["FAV_IMAGE_PATH"] = os.path.join(IMG_PATH, "favicon.png")

# streamlit 처음 실행하는 코드
st.set_page_config(
    page_title="Hello Jobits", # 브라우저탭에 뜰 제목
    page_icon=Image.open(st.session_state.FAV_IMAGE_PATH), #브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드
    layout="wide",
    initial_sidebar_state="collapsed"
)

# session_state에 변수 값 기본 초기화
st.title('Hello-JobIts 모의면접 🤖 (지원자 : ' +  st.session_state['nickname']+')')

if 'cnt' not in st.session_state:  # 진행률
    st.session_state.cnt = 0
if 'current_question_idx' not in st.session_state: # 대질문 개수
    st.session_state.current_question_idx = 0
if 'count' not in st.session_state:  # 꼬리질문?
    st.session_state.count = 0
if 'plus' not in st.session_state:  # 대질문 수행 여부
    st.session_state.plus = 0
if 'tail' not in st.session_state:
    st.session_state.tail = ''
if 'chain' not in st.session_state:
    st.session_state.chain = None
if 'basic_count' not in st.session_state:  # 기술면접 질문 개수 count
    st.session_state.basic_count = 0
if 'finish' not in st.session_state: # 프로젝트 관련 질문 끝났는지 여부
    st.session_state.finish = 0
if 'messages' not in st.session_state:
        st.session_state['messages'] = [{"role": "assistant",
                                        "content": "안녕하세요, 면접 시작하도록 하겠습니다."}]
        
# 질문들 생성
questions = st.session_state.main_question # 프로젝트 질문
basic_questions = st.session_state.basic_question # 기초 지식 질문

len_questions = len(questions) + len(basic_questions)
st.session_state.cnt += 1
if st.session_state.cnt >= len_questions:
    st.session_state.cnt = len_questions
st.progress(st.session_state.cnt/len_questions, '모의면접 진행률')

# 이전 대화 목록 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.session_state.questions_interview = st.session_state.main_question

##################################### 여기서부터 모의 면접 시작 ############################################
# 프로젝트 관련 질문 -> 대분류 질문 (일반 질문, plus == 0)
if st.session_state.plus == 0:
    # 조건 1 : 만약 대질문의 질문이 아직 남아있면 질문 실행하기
    if len(st.session_state.questions_interview) > st.session_state.current_question_idx:
        with st.chat_message('assistant'):
            st.markdown(st.session_state.questions_interview[st.session_state.current_question_idx]) # 질문하기

    # 사용자 답변 입력 받기
    if query := st.chat_input('답변을 입력해주세요. '):
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.questions_interview[st.session_state.current_question_idx]})
        
        # 질문이 남아 있다면 입력 받기
        if len(st.session_state.questions_interview) > st.session_state.current_question_idx:
            st.session_state.messages.append({"role": "user", "content": query})
            
            # 사용자 입력 채팅으로 출력하기
            with st.chat_message('user'):
                st.markdown(query)

            # 다음 질문 기다리기
            with st.chat_message('assistant'):
                # spinner는 질문 생성 때 넣어주면 좋을 것.
                # with st.spinner("답변을 작성중입니다..."):
                #     sleep(1) # 로딩 화면 보여주기
                result = '답변 감사합니다'
                # st.session_state.feedback = result # 이거 삭제해도 무관
                st.markdown(result)
            st.session_state.messages.append({"role": "assistant", "content": result})
            # 프로젝트에 대한 꼬리질문 하겠다는 표시, plus == 1
            st.session_state.plus = 1
        
        # 프로젝트에 대한 꼬리질문 실행
        if st.session_state.plus == 1:
            # 꼬리질문 함수(load_chain) 실행
            st.session_state.chain = load_chain(st.session_state.questions_interview[st.session_state.current_question_idx])

            with st.chat_message('assistant'):
                st.session_state.tail = st.session_state.chain.predict(input = query)
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.tail})
                st.markdown(st.session_state.tail)
        #######################  만약 꼬리질문이 없다면? (이거 왜 있는건지 잘 모르겠습니당) -> 아마 데모 페이지의 잔재일수도?  
        elif len(st.session_state.questions_interview) > st.session_state.current_question_idx + 1:
            st.session_state.current_question_idx += 1
            with st.chat_message('assistant'):
                st.markdown(st.session_state.questions_interview[st.session_state.current_question_idx]) # 질문 뽑기

# 프로젝트 질문 -> 소분류 질문 (꼬리질문, plus ==1)
elif st.session_state.plus == 1:

    # 꼬리질문 개수 카운트(2개 초과로 넘어가지 않도록)
    st.session_state.count += 1 # 처음에 꼬리질문 출력했으므로 바로 카운트 +1
    st.session_state.cnt -= 1

    # 꼬리질문에 대한 사용자 답변 입력
    if query := st.chat_input('답변을 입력해주세요. '):
        with st.chat_message('user'):
                st.markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})
    
    # 조건 1 : 꼬리질문이 2번 나오지 않았다면 다음 꼬리질문 실행
    if st.session_state.count != 2:
        with st.chat_message('assistant'):
            plus_result = "꼬리질문 답변 감사합니다."
            st.markdown(plus_result)
        st.session_state.tail = st.session_state.chain.predict(input = query)   # 꼬리질문 query 입력
        with st.chat_message('assistant'):
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.tail})
            st.markdown(st.session_state.tail)
        st.session_state.messages.append({"role": "assistant", "content": plus_result})

    
    # 조건 2 : 꼬리질문 2번 했으면 다음 대분류 질문 실행
    if (st.session_state.count == 2):
        # 꼬리질문 관련 plus와 count 초기화
        st.session_state.count = 0
        st.session_state.plus = 0
        st.success(":짠: 모든 꼬리질문에 대한 답변을 완료했습니다.")

        # 조건 3 : 만약 꼬리 질문이 끝나고 다음 대분류 질문이 있다면? -> 다음 대분류 질문 출력
        if len(st.session_state.questions_interview) > st.session_state.current_question_idx + 1:
            with st.chat_message('assistant'):
                st.session_state.current_question_idx += 1
                st.markdown(st.session_state.questions_interview[st.session_state.current_question_idx])
        else:   # 다음 대분류 질문이 없다면? -> 프로젝트 질문이 끝나고 기초 질문 출력
            st.session_state.finish = 1
            st.success(":짠: 다음으로 기초 기술 질문으로 넘어가겠습니다.")
            st.session_state.plus = 2
            with st.chat_message('assistant'):
                st.markdown(st.session_state.basic_questions[st.session_state.basic_count]) # 질문 뽑기
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.basic_questions[st.session_state.basic_count]})

# 프로젝트 관련 질문이 끝나고 기초 질문 시작 ()
elif st.session_state.finish == 1:
    # 기초 질문에 대한 사용자의 답변 입력
    if query := st.chat_input('답변을 입력해주세요. '):
        # 기초 질문이 남아 있다면 입력 받기
        if len(st.session_state.basic_questions) > st.session_state.basic_count:
            st.session_state.messages.append({"role": "user", "content": query})
            
            # 사용자 입력을 채팅으로 출력하기
            with st.chat_message('user'):
                st.markdown(query)
            # 답변 감사합니다 출력하기
            with st.chat_message('assistant'):
                # with st.spinner("답변을 작성중입니다..."):
                #     sleep(1) # 로딩 화면 보여주기
                result = '답변 감사합니다'
                # st.session_state.feedback = result
                st.markdown(result)
            #################################### 여기 수정했습니다. -상수 -
            st.session_state.messages.append({"role": "assistant", "content": result})
            # st.session_state.current_question_idx += 1  # 이전 코드
            
        if len(st.session_state.basic_questions) > st.session_state.basic_count+1:     # basic_count == index
            st.session_state.messages.append({"role": "assistant", "content": st.session_state.basic_questions[st.session_state.basic_count+1]})  
            
    # 조건 1 : 기초 질문이 아직 남아있지 않다면 마지막 멘트 출력
    if len(st.session_state.basic_questions) <= st.session_state.basic_count+1:     # basic_count == index
        st.success(":짠: 모든 질문에 대한 답변을 완료했습니다.")
        # 결과 분석 페이지 가기
        if st.button("결과 보러 가기"):
            switch_page(NEXT_PAGE)
    else:
        st.session_state.basic_count += 1
        if st.session_state.basic_count <= len(st.session_state.basic_questions):
            with st.chat_message('assistant'):
                st.markdown(st.session_state.basic_questions[st.session_state.basic_count]) # 질문 뽑기
