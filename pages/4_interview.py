import os
import sys
from time import sleep

import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src.util import load_chain
from config import IMG_PATH

# session_state에 변수 값 기본 초기화
session_state_defaults = {
    "FAV_IMAGE_PATH": os.path.join(IMG_PATH, "favicon.png"),
    "progress": 0,       # 진행률
    "current_question_idx": 0, # 대질문 개수
    "tail_question_count": 0, # 꼬리질문 개수
    "is_tail_question": False, # 현재 질문이 꼬리질문인지 여부
    "is_main_question_completed": 0,  # 대질문 수행 여부
    "tail_question": '', # 꼬리질문
    "chain": None, # 체인 모델
    "is_project_question_completed": False, # 프로젝트 관련 질문 끝났는지 여부
    "messages": [{"role": "assistant", 
    "content": "안녕하세요, 면접 시작하도록 하겠습니다."}],
    "interview_script": []
}

for key, value in session_state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# streamlit 처음 실행하는 코드
st.set_page_config(
    page_title="Hello Jobits", # 브라우저탭에 뜰 제목
    page_icon=Image.open(st.session_state.FAV_IMAGE_PATH), #브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드
    layout="wide",
    initial_sidebar_state="collapsed"
)

# session_state에 변수 값 기본 초기화
st.title('Hello-JobIts 모의면접 🤖 (지원자 : ' +  st.session_state['nickname']+')')
        
# 질문이 너무 많은 경우 최대 3개만 질문하기
st.session_state.interview_questions = st.session_state.main_question[:max(3, len(st.session_state.main_question))]
st.session_state.len_questions = len(st.session_state.interview_questions)

# 상태 바
st.session_state.progress += 1
if st.session_state.progress >= st.session_state.len_questions:
    st.session_state.progress = st.session_state.len_questions
st.progress(st.session_state.progress/st.session_state.len_questions, '모의면접 진행률')

def ask_question(question):
    with st.chat_message('assistant'):
        st.write(question) # write인지 markdown인지 확인하기

def user_input(response):
    with st.chat_message('user'):
        st.write(response)

def append_message(role: str, content: str):
    st.session_state.messages.append({"role": role, "content": content})

def next_question():
    st.session_state.current_question_idx += 1

def next_tail_question():
    st.session_state.tail_question_count += 1

# 이전 대화 목록 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

    if msg['role'] == 'user':
        role_name = 'You'
    elif msg['role'] == 'assistant':
        role_name = '자비스'
    string = role_name + ' : ' + msg['content']
    st.session_state.interview_script.append(string)
    

# 대화내역 파일로 저장
st.session_state.interview_script_download = "\n\n".join(st.session_state.interview_script)
with open(os.path.join(st.session_state['save_dir'], "interview_history.txt"), "w") as file:
    file.write(st.session_state.interview_script_download)   

##################################### 여기서부터 모의 면접 시작 ############################################
# 프로젝트 관련 질문 -> 대분류 질문 (일반 질문, plus == 0)
if st.session_state.is_tail_question == False:
    # 조건 1 : 만약 대질문의 질문이 아직 남아있면 질문 실행하기
    if len(st.session_state.interview_questions) > st.session_state.current_question_idx:
        ask_question(st.session_state.interview_questions[st.session_state.current_question_idx])

    # 사용자 답변 입력 받기
    if query := st.chat_input('답변을 입력해주세요. '):
        append_message("assistant", st.session_state.interview_questions[st.session_state.current_question_idx])
        
        # 질문이 남아 있다면 입력 받기
        if len(st.session_state.interview_questions) > st.session_state.current_question_idx:
            append_message("user", query) # 대화 내용 추가
            user_input(query)   # 사용자 입력 채팅으로 출력하기

            # 다음 질문 기다리기
            thanks = "답변 감사합니다"
            ask_question(thanks)
            append_message("assistant", thanks)

            # 프로젝트에 대한 꼬리질문 하겠다는 표시, plus == 1
            st.session_state.is_tail_question = True
        
        # 프로젝트에 대한 꼬리질문 실행
        if st.session_state.is_tail_question == True:
            st.session_state.chain = load_chain(st.session_state.interview_questions[st.session_state.current_question_idx])
            st.session_state.tail = st.session_state.chain.predict(input = query)
            append_message("assistant", st.session_state.tail)
            ask_question(st.session_state.tail)

# 프로젝트 질문 -> 소분류 질문 (꼬리질문, plus ==1)
elif st.session_state.is_tail_question == True:

    # 꼬리질문 개수 카운트(2개 초과로 넘어가지 않도록)
    next_tail_question() # 처음에 꼬리질문 출력했으므로 바로 카운트 +1
    st.session_state.progress -= 1

    # 꼬리질문에 대한 사용자 답변 입력
    if query := st.chat_input('답변을 입력해주세요. '):
        user_input(query) 
        append_message("user", query)
    
    # 조건 1 : 꼬리질문이 2번 나오지 않았다면 다음 꼬리질문 실행
    if st.session_state.tail_question_count < 2:
        thanks_tail = "꼬리질문 답변 감사합니다."
        ask_question(thanks_tail)
        append_message("assistant", thanks_tail)

        st.session_state.tail = st.session_state.chain.predict(input = query)
        ask_question(st.session_state.tail)
        append_message("assistant", st.session_state.tail)
    
    # 조건 2 : 꼬리질문 2번 했으면 다음 대분류 질문 실행
    if st.session_state.tail_question_count == 2:
        st.session_state.tail_question_count = 0 # 꼬리질문 카운트 초기화
        st.session_state.is_tail_question = False # 꼬리질문 끝
        st.success(":짠: 모든 꼬리질문에 대한 답변을 완료했습니다.")

        # 조건 3 : 만약 꼬리 질문이 끝나고 다음 대분류 질문이 있다면? -> 다음 대분류 질문 출력
        if len(st.session_state.interview_questions) > st.session_state.current_question_idx + 1:
            next_question()

            # 이 부분이 필요한가?
            ask_question(st.session_state.interview_questions[st.session_state.current_question_idx])
            
        else:   # 다음 대분류 질문이 없다면? -> 프로젝트 질문이 끝나고 기초 질문 출력
            st.session_state.is_project_question_completed = True
            st.success(":짠: 모든 질문에 대한 답변을 완료했습니다. 고생 많으셨습니다.")
            st.session_state.is_tail_question = 2

# 프로젝트 관련 질문이 끝나면 끝내기
elif st.session_state.is_project_question_completed:
    st.success(":짠: 모든 질문에 대한 답변을 완료했습니다. 고생 많으셨습니다.")
        
    # 다운로드 버튼 생성
    st.download_button(
        label="모의 면접 대화내역 다운로드",  # 버튼에 표시될 텍스트
        data=st.session_state.interview_script_download,  # 다운로드할 데이터
        file_name="interview_history.txt",  # 생성될 파일의 이름
        mime="text/plain",  # MIME 타입 지정
    )

    # 페이지 이동
    if st.button("처음으로 가기"):
        switch_page('user')