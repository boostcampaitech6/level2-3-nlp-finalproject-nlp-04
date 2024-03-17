# 인터뷰 진행이 아닌 예상 질문을 모아보기 위한 임시 페이지 입니다.
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import time
import traceback
import os
import re
import random
from streamlit_chat import message
from front.jobits.src.generate_question import (
                                   # 추가
                                   load_user_JD, 
                                   save_user_JD,
                                   create_prompt_with_jd,
                                   create_prompt_feedback

                                   )
from front.jobits.utils.util import (
                        read_user_job_info,
                        read_prompt_from_txt,
                        local_css,
                        load_css_as_string)
import base64 # gif 이미지 불러오기
from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback

from langchain.prompts import (PromptTemplate,
                               ChatPromptTemplate,
                               SystemMessagePromptTemplate,
                               HumanMessagePromptTemplate)
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import LLMChain

# import tiktoken
# import chromadb

from front.jobits.src.mypath import MY_PATH


OPENAI_API_KEY = read_prompt_from_txt(MY_PATH+'/data/test/OPANAI_KEY.txt')

MODEL_NAME = 'gpt-3.5-turbo-16k'

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
    unsafe_allow_html=True
)

# questions 
questions = st.session_state.main_question
# 사용자 인터페이스 생성

st.title(f'{st.session_state.user_name}님의 이력서 예상 질문입니다.')

prompt_template = read_prompt_from_txt(MY_PATH + "/data/test/prompt_feedback.txt")
            

# 각 질문에 대해 번호를 매기고 토글 위젯 생성
for i, question in enumerate(questions, start=1):
    
    # 질문이 비어있거나 개행 문자만 포함된 경우 토글을 생성하지 않음
    if question.strip():
        
        # 토글 위젯 생성
        with st.expander(f"{question}", expanded=False):
            st.caption("질문에 대한 답변을 500자 이내로 작성해 주세요")
            
            # 텍스트 입력 박스
            user_answer = st.text_area("답변:", key=f"input_{i}", max_chars=500)
            
            # 답변하기 버튼
            if st.button("답변하기", key=f"button_{i}"):
            
                if not user_answer.strip():
                        st.error("답변을 입력해 주세요.")
                else:
                    # 버튼 클릭 시 안내 텍스트 출력
                    st.text("답변이 제출되었습니다. 피드백을 생성중입니다.")
            
                    ### FeedBack Pre-process @@@@@@@@@@@@@@@@@@@@@@@@@@
                    st.session_state.logger.info("Start feedback precess")
            
                    
                    prompt_Feedback = create_prompt_feedback(prompt_template)
                    # proprompt_Feedbackmpt_ 생성완료
            
                    st.session_state.logger.info("create prompt_Feedback object")
            
                    ### 모델 세팅 그대로
                    llm = ChatOpenAI(temperature=0.0
                                , model_name=MODEL_NAME
                                , openai_api_key=OPENAI_API_KEY
                                )
            
                    st.session_state.logger.info("create llm object")
            
            
                    # 피드백 시작
                    
                    chain_feedback_1 = LLMChain(llm=llm, prompt=prompt_Feedback)  
            
            
                    st.session_state.logger.info("create chain_feedback_1 object")
                    
                    
                    answer_feedback = chain_feedback_1.run({"question" : question , "answer" : user_answer})
            
                    st.session_state.logger.info("answer_feedback complit")

                    st.text(answer_feedback)

## input_form
input_form, start_button = st.columns([1,2]) # 노션 컬럼처럼 열을 나눠서 할수있게 해주는것

  
with start_button:
        start_button.markdown(f''' 
                              <div class = 'main_message'> JOBits <br></div> 
                              ''', 
                              unsafe_allow_html=True )

        if start_button.button('시작 화면으로 돌아가기'):
            
            switch_page(NEXT_PAGE)
            
            
