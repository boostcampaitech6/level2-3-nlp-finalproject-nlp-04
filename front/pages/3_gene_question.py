__import__("pysqlite3")
import sys
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import os
import re
import time

import streamlit as st
from langchain.chains import LLMChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from PIL import Image
from src.generate_question import create_prompt_with_jd  # 추가
from src.generate_question import (create_prompt_with_resume,
                                   create_resume_vectordb, load_user_JD,
                                   load_user_resume, save_user_JD,
                                   save_user_resume,create_prompt_with_question)
from streamlit_extras.switch_page_button import switch_page
from utils.util import local_css, read_prompt_from_txt
from src.rule_based_algorithm import generate_rule_based_questions
from back.config import OPENAI_API_KEY  # OPENAI_API_KEY 불러오기




DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
st.session_state["FAV_IMAGE_PATH"] = os.path.join(DATA_DIR, "images/favicon.png")
st.set_page_config(
    page_title="Hello Jobits",  # 브라우저탭에 뜰 제목
    page_icon=Image.open(
        st.session_state.FAV_IMAGE_PATH
    ),  # 브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.session_state.logger.info("start")
NEXT_PAGE = "show_questions_hint"

MY_PATH = os.path.dirname(os.path.dirname(__file__))

#### style css ####
MAIN_IMG = st.session_state.MAIN_IMG
LOGO_IMG = st.session_state.LOGO_IMG

local_css(MY_PATH + "/css/background.css")
local_css(MY_PATH + "/css/2_generate_question.css")
st.markdown(
    f"""<style>
                         /* 로딩이미지 */
                         .loading_space {{
                            display : flex;
                            justify-content : center;
                            margin-top : -3rem;
                        }}
                        .loading_space img{{
                            max-width : 70%;
                        }}
                        .loading_text {{
                            /* 광고 들어오면 공간 확보 */
                            padding-top : 4rem;
                            z-index : 99;
                        }}
                        .loading_text p{{
                            font-family : 'Nanumsquare';
                            color:#4C4F6D;
                            font-size:28px ;
                            line-height:1.5;
                            word-break:keep-all;
                            font-weight:700;
                            text-align:center;
                            z-index : 99;
                        }}
                        .dots-container {{
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            height: 100%;
                            width: 100%;
                            padding-top : 2rem;
                            padding-bottom : 5rem;
                            z-index : 99;
                        }}

                        .dot {{
                            z-index : 99;
                            height: 20px;
                            width: 20px;
                            margin-right: 10px;
                            border-radius: 10px;
                            background-color: #b3d4fc;
                            animation: pulse 1.5s infinite ease-in-out;
                        }}
                        .dot:last-child {{
                            margin-right: 0;
                        }}

                        .dot:nth-child(1) {{
                            animation-delay: -0.3s;
                        }}

                        .dot:nth-child(2) {{
                            animation-delay: -0.1s;
                        }}

                        .dot:nth-child(3) {{
                            animation-delay: 0.1s;
                        }}
                        </style>
#             """,
    unsafe_allow_html=True,
)
## set variables
MODEL_NAME = "gpt-3.5-turbo-16k"

## set save dir
USER_RESUME_SAVE_DIR = os.path.join(st.session_state["save_dir"], "2_generate_question_user_resume.pdf")
### 추가
USER_JD_SAVE_DIR = os.path.join(st.session_state["save_dir"], "2_generate_question_user_JD.txt")

BIG_QUESTION_SAVE_DIR = os.path.join(st.session_state["save_dir"], "2_generate_question_generated_big_question.txt")


# 진행률
progress_holder = st.empty()  # 작업에 따라 문구 바뀌는 곳
loading_message = [
    f" JOBits 가 '{st.session_state.user_name}'님의 이력서를 꼼꼼하게 읽고 있습니다. <br> 최대 3분까지 소요될 수 있습니다.",
    f" JOBits 가 '{st.session_state.user_name}'님과의 면접을 준비하고 있습니다",
]

# 로딩 그림(progress bar)
st.markdown(
    """<section class="dots-container">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </section>
            """,
    unsafe_allow_html=True,
)

## 면접&이력서 팁
## 공간이자 이미지가 들어가면 좋을 것 같은 곳
st.markdown(
    f"""<div class='loading_space'>
                    <img class='tips' src="data:image/gif;base64,{st.session_state['LOADING_GIF1']}"></div>""",
    unsafe_allow_html=True,
)
with progress_holder:
    for i in range(2):
        ### step1 : 대질문 생성 및 추출, step2 : 전처리(time.sleep(3))
        progress_holder.markdown(
            f"""<div class="loading_text">
                                        <p>{loading_message[i]}</p></div>""",
            unsafe_allow_html=True,
        )
        if st.session_state.big_q_progress:
            ### 이력서 Pre-process
            st.session_state.logger.info("resume process ")
            ### uploaded_file는 streamlit의 file_uploader에서 반환된 객체
            user_resume = st.session_state['user_email'] + 'uploaded_resume'
            uploaded_file = st.session_state[user_resume]
            ### 저장
            save_user_resume(USER_RESUME_SAVE_DIR, uploaded_file)
            st.session_state.logger.info("save resume")
            ### 불러오기
            user_resume = load_user_resume(USER_RESUME_SAVE_DIR)
            st.session_state.logger.info("user total resume import")

            ### JD Pre-process @@@@@@@@@@@@@@@@@@@@@@@@@@
            st.session_state.logger.info("JD precess")
            ### uploaded_txt 로 uploaded_JD 에서 JD 를 받아옵니다
            user_jd = st.session_state['user_email'] + 'uploaded_JD'
            uploaded_file = st.session_state[user_jd]
            ### 저장 USER_JD_SAVE_DIR 경로에 uploaded_file 내용을 적어 저장합니다.
            save_user_JD(USER_JD_SAVE_DIR, uploaded_file)
            st.session_state.logger.info("save JD")
            ### 불러오기
            user_JD = load_user_JD(USER_JD_SAVE_DIR)
            st.session_state.logger.info("user total JD import")

            ### JD 사용하여 JD 추출용 프롬프트 만들기
            st.session_state.logger.info("prompt JD start")

            prompt_template = read_prompt_from_txt(MY_PATH + "/data/test/prompt_JD_template.txt")

            prompt_JD = create_prompt_with_jd(prompt_template)
            # prompt_JD 생성완료
            st.session_state.logger.info("create prompt JD object")

            ### 모델 세팅 그대로
            llm = ChatOpenAI(
                temperature=st.session_state.temperature, model_name=MODEL_NAME, openai_api_key=OPENAI_API_KEY
            )

            st.session_state.logger.info("create llm object")

            ######## 이제 태연스의  데모를 체인으로 바꿔 실행하겠습니다.
            # STEP 1. 사용자가 입력한 JD 를 GPT 를 이용해 job_description 을 뽑습니다.

            # 사용 시간 출력용
            start = time.time()
            ###################
            chain_JD_1 = LLMChain(llm=llm, prompt=prompt_JD)

            st.session_state.logger.info("create chain_JD_1 object")

            job_description = chain_JD_1.run(user_JD)

            st.session_state.logger.info("chain_JD_1 complit")

            # STEP 2. step 1 에서 생성된 job_description 를 qa prompt template 에 넣고, GPT 에 질의하여 예상 질문을 뽑습니다.
            # prompt_qa_template #######################################
     
            st.session_state.logger.info("prompt resume start")
            prompt_template = read_prompt_from_txt(MY_PATH + "/data/test/prompt_resume_template.txt")
            
            st.session_state.logger.info("create prompt resume template")
            prompt_resume = create_prompt_with_resume(prompt_template)
            
            st.session_state.logger.info("create prompt_resume")
            
            vector_index = create_resume_vectordb(USER_RESUME_SAVE_DIR) # 이력서 vectordb를 생성해줍니다.

            st.session_state.logger.info("user_resume chunk OpenAIEmbeddings ")

            ### STEP 2 를 위한 새 모델 호출


            llm2 = ChatOpenAI(temperature=0.0,
                              model_name=MODEL_NAME,
                              openai_api_key=OPENAI_API_KEY
                             )
            
            chain_type_kwargs = {"prompt": prompt_resume}
            

            qa_chain = RetrievalQA.from_chain_type(
                llm=llm2,
                chain_type="stuff",
                retriever=vector_index.as_retriever(),
                chain_type_kwargs=chain_type_kwargs, 
                verbose = True
            )
            
            resume = qa_chain.run("기술면접에 나올만한 프로젝트 내용은?")
            print("prompt_resume @@@@@@@@",prompt_resume)
            st.session_state.logger.info(" prompt_resume running complit")         
            print(resume)
            
            ## step3 : 
            st.session_state.logger.info("prompt question start")
            prompt_template = read_prompt_from_txt(MY_PATH + "/data/test/prompt_question_template.txt")
            
            st.session_state.logger.info("create prompt question template")
            prompt_question = create_prompt_with_question(prompt_template)

            llm3= ChatOpenAI(temperature=0,
                             model_name=MODEL_NAME,
                             openai_api_key=OPENAI_API_KEY)
            
            chain = LLMChain(llm=llm3, prompt=prompt_question)
            
            main_question = chain.run({'jd': job_description,'resume': resume})
            #################
            end = time.time()
            st.session_state.logger.info(f"generate big question run time is ... {(end-start)/60:.3f} 분 ({(end-start):0.1f}초)")
            st.session_state.logger.info(" prompt_quest running complete")
            
            print(main_question)
            
            ### STEP 3. 결과물 및 Token 사용량 저장
            ### 결과 텍스트 저장
            # '\n\n'을 사용하여 질문 분리 후 바로 unpacking

            # 각 항목을 분리하여 리스트에 저장
            questions = re.split(r"\n\d+\.\s*", main_question.strip())
            #    첫 번째 빈 항목 제거
            questions = [question for question in questions if question]

            st.session_state.logger.info(f"save question result")

            ### User pdf파일 삭제
            try:
                os.remove(USER_RESUME_SAVE_DIR)
            except Exception as e:
                st.session_state.logger.info(f"User resume delete Error: \n{e}")
                print(">>> User resume delete Error: \n{e}")

            st.session_state.big_q_progress = False ### 대질문 생성 끝
           
        else :
            selected_job = st.session_state.selected_job
            
            rule_questions = generate_rule_based_questions(selected_job,user_JD,user_resume)
            print()
            
            ### 다음 세션으로 값 넘기기
            st.session_state.main_question = questions + rule_questions
            st.session_state.logger.info("end gene_question")
            time.sleep(3)
            ####

            if st.session_state.cur_task == "gene_question":
                switch_page("show_questions_hint")
            elif st.session_state.cur_task == "interview":
                switch_page("interview")
