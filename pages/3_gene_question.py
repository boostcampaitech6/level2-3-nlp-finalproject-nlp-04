__import__("pysqlite3")
import sys
import threading

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import os
import re
import time
import json

import streamlit as st
from langchain.chains import LLMChain, RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from PIL import Image
from streamlit_extras.switch_page_button import switch_page

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src.generate_question import create_prompt_with_jd
from src.generate_question import (create_prompt_with_question,
                                   create_prompt_with_resume,
                                   create_resume_vectordb, load_user_JD,
                                   load_user_resume, save_user_JD,
                                   save_user_resume)
from src.rule_based import list_extend_questions_based_on_keywords
from src.util import local_css, read_prompt_from_txt
from src.semantic_search import faiss_inference, reranker
from config import OPENAI_API_KEY, DATA_DIR, IMG_PATH, CSS_PATH

st.session_state["FAV_IMAGE_PATH"] = os.path.join(IMG_PATH, "favicon.png")
st.set_page_config(
    page_title="Hello Jobits",  # 브라우저탭에 뜰 제목
    page_icon=Image.open(
        st.session_state.FAV_IMAGE_PATH
    ),  # 브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드
    layout="wide",
    initial_sidebar_state="collapsed",)

st.session_state.logger.info("start")
NEXT_PAGE = "show_questions_hint"

MY_PATH = os.path.dirname(os.path.dirname(__file__))

#### style css ####
MAIN_IMG = st.session_state.MAIN_IMG
LOGO_IMG = st.session_state.LOGO_IMG

local_css(os.path.join(CSS_PATH, "background.css"))
local_css(os.path.join(CSS_PATH, "2_generate_question.css"))
st.markdown(f"""<style>
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
#           """,
            unsafe_allow_html=True,)

## set variables
MODEL_NAME = "gpt-3.5-turbo-16k"
#MODEL_NAME = "gpt-4-0125-preview"

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
st.markdown("""
            <section class="dots-container">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            </section>
            """,
            unsafe_allow_html=True,)

## 면접&이력서 팁
## 공간이자 이미지가 들어가면 좋을 것 같은 곳
st.markdown(f"""
            <div class='loading_space'>
            <img class='tips' src="data:image/gif;base64,{st.session_state['LOADING_GIF1']}"></div>""",
            unsafe_allow_html=True,
            )
with progress_holder:
    for i in range(2):
        ### step1 : 대질문 생성 및 추출, step2 : 전처리(time.sleep(3))
        progress_holder.markdown(f"""
                                 <div class="loading_text">
                                 <p>{loading_message[i]}</p></div>""",
                                 unsafe_allow_html=True,
                                 )
        if st.session_state.big_q_progress:
            ### 이력서 Pre-process
            st.session_state.logger.info("resume process ")
            ### uploaded_file는 streamlit의 file_uploader에서 반환된 객체
            user_resume = st.session_state['user_email'] + 'uploaded_resume'
            st.session_state.uploaded_file_resume = st.session_state[user_resume]
            ### 저장
            save_user_resume(USER_RESUME_SAVE_DIR, st.session_state.uploaded_file_resume)
            st.session_state.logger.info("save resume")
            ### 불러오기
            user_resume = load_user_resume(USER_RESUME_SAVE_DIR)
            st.session_state.logger.info("user total resume import")

            ### JD Pre-process ########################################
            st.session_state.logger.info("JD precess")
            ### uploaded_txt 로 uploaded_JD 에서 JD 를 받아옵니다
            user_jd = st.session_state['user_email'] + 'uploaded_JD'
            st.session_state.uploaded_file_jd = st.session_state[user_jd]
            ### 저장 USER_JD_SAVE_DIR 경로에 uploaded_file 내용을 적어 저장합니다.
            save_user_JD(USER_JD_SAVE_DIR, st.session_state.uploaded_file_jd)
            st.session_state.logger.info("save JD")
            ### 불러오기
            st.session_state.user_JD = load_user_JD(USER_JD_SAVE_DIR)
            st.session_state.logger.info("user total JD import")

            ### JD 사용하여 JD 추출용 프롬프트 만들기
            st.session_state.logger.info("prompt JD start")

            prompt_template_jd = read_prompt_from_txt(os.path.join(DATA_DIR, "test/prompt_JD_template.txt"))

            st.session_state.prompt_JD = create_prompt_with_jd(prompt_template_jd)
            # prompt_JD 생성완료
            st.session_state.logger.info("create prompt JD object")

            ### 모델 세팅 그대로
            llm = ChatOpenAI(temperature=st.session_state.temperature,
                             model_name=MODEL_NAME,
                             openai_api_key=OPENAI_API_KEY)

            st.session_state.logger.info("create llm object")

            ######## 이제 태연스의  데모를 체인으로 바꿔 실행하겠습니다.
            # STEP 1. 사용자가 입력한 JD 를 GPT 를 이용해 job_description 을 뽑습니다.

            # 사용 시간 출력용
            start = time.time()
            ###################
            st.session_state.chain_JD_1 = LLMChain(llm=llm, prompt=st.session_state.prompt_JD)

            st.session_state.logger.info("create chain_JD_1 object")

            st.session_state.job_description = st.session_state.chain_JD_1.run(st.session_state.user_JD)

            st.session_state.logger.info("chain_JD_1 complit")

            # STEP 2. step 1 에서 생성된 job_description 를 qa prompt template 에 넣고, GPT 에 질의하여 예상 질문을 뽑습니다.
            # prompt_qa_template #######################################
            lock = threading.Lock()
            lock.acquire()

            st.session_state.logger.info("prompt resume start")
            prompt_template_resume = read_prompt_from_txt(os.path.join(DATA_DIR, "test/prompt_resume_template.txt"))

            st.session_state.logger.info("create prompt resume template")
            st.session_state.prompt_resume = create_prompt_with_resume(prompt_template_resume)

            st.session_state.logger.info("create prompt_resume")
            st.session_state.vector_index = create_resume_vectordb(USER_RESUME_SAVE_DIR)  # 이력서 vectordb를 생성해줍니다.

            st.session_state.logger.info("user_resume chunk OpenAIEmbeddings ")

            ### STEP 2 를 위한 새 모델 호출
            llm2 = ChatOpenAI(temperature=0.0, 
                              model_name=MODEL_NAME, 
                              openai_api_key=OPENAI_API_KEY)

            st.session_state.chain_type_kwargs = {"prompt": st.session_state.prompt_resume}

            st.session_state.qa_chain = RetrievalQA.from_chain_type(llm=llm2,
                                                   chain_type="stuff",
                                                   retriever=st.session_state.vector_index.as_retriever(),
                                                   chain_type_kwargs=st.session_state.chain_type_kwargs,
                                                   verbose=True,)

            st.session_state.resume = st.session_state.qa_chain.run("기술면접에 나올만한 프로젝트 내용은?")
            print("prompt_resume @@@@@@@@", st.session_state.prompt_resume)
            st.session_state.logger.info(" prompt_resume running complit")
            print("사용자", st.session_state.user_email, "의 resume : \n", st.session_state.resume)

            # ChromaDB 비워주기
            for collection in st.session_state.vector_index._client.list_collections():
                ids = collection.get()['ids']
                print('REMOVE %s document(s) from %s collection' % (str(len(ids)), collection.name))
                if len(ids): collection.delete(ids)

            lock.release()

            ## step3 :
            st.session_state.logger.info("prompt question start")
            prompt_template_question = read_prompt_from_txt(os.path.join(DATA_DIR, "test/prompt_question_template.txt"))

            st.session_state.logger.info("create prompt question template")
            st.session_state.prompt_question = create_prompt_with_question(prompt_template_question)

            llm3 = ChatOpenAI(temperature=0, model_name=MODEL_NAME, openai_api_key=OPENAI_API_KEY)

            st.session_state.chain = LLMChain(llm=llm3, prompt=st.session_state.prompt_question)

            st.session_state.main_question = st.session_state.chain.run({"jd": st.session_state.job_description, "resume": st.session_state.resume})
            #################
            end = time.time()
            st.session_state.logger.info(
                f"generate big question run time is ... {(end-start)/60:.3f} 분 ({(end-start):0.1f}초)"
            )
            st.session_state.logger.info(" prompt_quest running complete")
            print(st.session_state.main_question)

            ### STEP 3. 결과물 및 Token 사용량 저장
            ### 결과 텍스트 저장
            # '\n\n'을 사용하여 질문 분리 후 바로 unpacking

            lock.acquire()
            
            # 각 항목을 분리하여 리스트에 저장
            st.session_state.questions = re.split(r"\n\d+\.\s*", st.session_state.main_question.strip())
            # 첫 번째 빈 항목 제거
            st.session_state.questions = [question for question in st.session_state.questions if question]

            st.session_state.logger.info(f"save question result")

            lock.release()

            ### User pdf파일 삭제
            try:
                os.remove(USER_RESUME_SAVE_DIR)
            except Exception as e:
                st.session_state.logger.info(f"User resume delete Error: \n{e}")
                print(">>> User resume delete Error: \n{e}")

            st.session_state.big_q_progress = False  ### 대질문 생성 끝

        else:
            selected_job = st.session_state.selected_job
            # rule-based question
            with open(os.path.join(DATA_DIR, "rulebased_data.json"), "r", encoding="utf-8") as f:
                data_dict = json.load(f)
            
            #########################################
            ### position 하드코딩되어있음 수정 요망 ###
            #########################################
            st.session_state.rule_questions = list_extend_questions_based_on_keywords(data_dict, st.session_state.user_JD, "AI")
            print("### rule_questions ###")
            print(*(st.session_state.rule_questions), sep='/n')
            
            # semantic search question generation
            st.session_state.faiss_result = faiss_inference(st.session_state.job_description)
            st.session_state.faiss_question = reranker(st.session_state.job_description, st.session_state.faiss_result)
            st.session_state.logger.info(f"save faiss question")
            print("### faiss_question ###")
            print(*(st.session_state.faiss_question), sep='/n')
            ### 다음 세션으로 값 넘기기
            st.session_state.main_question = st.session_state.questions + st.session_state.rule_questions + st.session_state.faiss_question
            st.session_state.logger.info("end gene_question")
            time.sleep(3)
            ####
            
            if st.session_state.cur_task == 'gene_question':
                switch_page('show_questions_hint')
            elif st.session_state.cur_task == 'interview':
                switch_page('interview')
