# 인터뷰 진행이 아닌 예상 질문을 모아보기 위한 임시 페이지 입니다.
import os
import sys

import streamlit as st
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from PIL import Image
from src.generate_question import (create_prompt_feedback,  # 추가
                                   create_prompt_hint)
from streamlit_extras.switch_page_button import switch_page
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src.util import read_prompt_from_txt
from config import DATA_DIR, IMG_PATH, OPENAI_API_KEY

st.session_state["FAV_IMAGE_PATH"] = os.path.join(IMG_PATH, "favicon.png")
st.set_page_config(
    page_title="Hello Jobits",  # 브라우저탭에 뜰 제목
    page_icon=Image.open(
        st.session_state.FAV_IMAGE_PATH
    ),  # 브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드
    layout="wide",
    initial_sidebar_state="collapsed",
)
#MODEL_NAME = "gpt-4-0125-preview"
MODEL_NAME = "gpt-3.5-turbo-16k"
NEXT_PAGE = "introduction"

st.session_state.logger.info("start show_questions page")

# 사용자 정의 CSS 스타일을 추가합니다.
st.markdown(
    """
    <style>
    .stExpander > div:first-child {
        font-weight: bold;
        color: navy;
        border: 1px solid rgba(28, 131, 225, 0.1);
        border-radius: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# questions
st.session_state.questions_showhint = st.session_state.main_question
# 사용자 인터페이스 생성

st.title(f"{st.session_state.user_name}님의 기술면접 예상 질문입니다.")

prompt_template_fb = read_prompt_from_txt(os.path.join(DATA_DIR, "test/prompt_feedback.txt"))
prompt_template_ht = read_prompt_from_txt(os.path.join(DATA_DIR, "test/prompt_hint.txt"))


# 각 질문에 대해 번호를 매기고 토글 위젯 생성
for i, question in enumerate(st.session_state.questions_showhint, start=1):

    # 질문이 비어있거나 개행 문자만 포함된 경우 토글을 생성하지 않음
    if question.strip():

        # 토글 위젯 생성
        with st.expander(f"{question}", expanded=False):

            st.caption("질문에 대한 답변을 500자 이내로 작성해 주세요")
            # 텍스트 입력 박스
            user_answer = st.text_area("답변:", key=f"input_{i}", max_chars=500)

            # ###답변하기 버튼 이후 피드백 @@@@@@@@@@@@@@@@@2
            if st.button("답변하기", key=f"button_{i}"):

                if not user_answer.strip():
                    st.error("답변을 입력해 주세요.")
                else:
                    # 버튼 클릭 시 임시 메시지 객체 생성
                    temp_message = st.empty()

                    # 임시 메시지에 텍스트 표시
                    temp_message.text("답변이 생성되는 중입니다. 잠시 기다려주세요.")

                    prompt_Feedback = create_prompt_feedback(prompt_template_fb)
                    # proprompt_Feedbackmpt_ 생성완료

                    st.session_state.logger.info("create prompt_Feedback object")

                    ### 모델 세팅 그대로
                    llm = ChatOpenAI(temperature=0.0, model_name=MODEL_NAME, openai_api_key=OPENAI_API_KEY)

                    st.session_state.logger.info("create llm object")

                    # 피드백 시작

                    chain_feedback_2 = LLMChain(llm=llm, prompt=prompt_Feedback)

                    st.session_state.logger.info("create chain_feedback_2 object")

                    answer_feedback = chain_feedback_2.run({"question": question, "answer": user_answer})

                    st.session_state.logger.info("answer_feedback complit")

                    # 임시 메시지 제거 및 최종 답변 표시
                    temp_message.empty()
                    st.text(answer_feedback)

            # ###답변하기 버튼 이후 피드백 @@@@@@@@@@@@@@@@@2
            if st.button("힌트받기", key=f"button_ht_{i}"):

                ### FeedBack Pre-process @@@@@@@@@@@@@@@@@@@@@@@@@@
                st.session_state.logger.info("Start hint precess")

                prompt_Hint = create_prompt_hint(prompt_template_ht)
                # proprompt_Feedbackmpt_ 생성완료

                st.session_state.logger.info("create prompt_Hint object")

                ### 모델 세팅
                llm = ChatOpenAI(temperature=0.0, model_name=MODEL_NAME, openai_api_key=OPENAI_API_KEY)

                st.session_state.logger.info("create llm object")

                # 피드백 시작

                chain_hint_1 = LLMChain(llm=llm, prompt=prompt_Hint)

                st.session_state.logger.info("create chain_hint_1 object")

                answer_hint = chain_hint_1.run({"question": question})

                st.session_state.logger.info("chain_hint_1 complit")

                # 임시 메시지 제거 및 힌트

                st.text(answer_hint)


## input_form
input_form, start_button = st.columns([1, 2])  # 노션 컬럼처럼 열을 나눠서 할수있게 해주는것


with start_button:
    start_button.markdown(
        f""" 
                              <div class = 'main_message'> JOBits <br></div> 
                              """,
        unsafe_allow_html=True,
    )

    if start_button.button("시작 화면으로 돌아가기"):
        switch_page("user")
