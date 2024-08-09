import os
import sys

import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page

sys.path.append("./")
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from config import DATA_DIR, IMG_PATH, path, CSS_PATH
from loguru import logger as _logger
from src.logger import DevConfig
from src.util import (check_essential, get_image_base64, local_css,
                        read_job_info_tb, read_prompt_from_txt,
                        read_sample_resume, save_uploaded_jd_as_filepath)

st.session_state['FAV_IMAGE_PATH'] = os.path.join(IMG_PATH, "favicon.png")

if st.session_state['user_email'] != 'GUEST':   
    config = DevConfig
    st.session_state["save_dir"] = os.path.join(config.SAVE_DIR, st.session_state['user_email'])

if not os.path.exists(st.session_state["save_dir"]):
    os.makedirs(st.session_state["save_dir"])
    
if "logger" not in st.session_state:
    # logru_logger(**config.config)
    _logger.configure(**config.config)
    st.session_state["logger"] = _logger # session_state에 ["logger"] 라는 키값을 추가하여 사용

st.set_page_config(
    page_title="Hello Jobits",  # 브라우저탭에 뜰 제목
    page_icon=Image.open(st.session_state.FAV_IMAGE_PATH),  # 브라우저 탭에 뜰 아이콘
    layout="wide",
    initial_sidebar_state="collapsed",
)

SAVE_JD_FILE_DIR = st.session_state['save_dir']
EXAMPLE_JD = read_prompt_from_txt(os.path.join(DATA_DIR, "JD_example.txt") )
# st.session_state.logger.info("start") # 이 logger 가  st.session_state["logger"] = _logger 로 home 에서 생성된 함수입니다.
# .info 는 logger 즉 logru 라이브러리의 logger의 메서드입니다.

NEXT_PAGE = "gene_question"
NEXT_PAGE_NORESUME = "gene_question_no_resume"

#### style css ####

st.title("안녕하세요, " + st.session_state.nickname + "님!")  # 사용자 이름을 받아서 화면에 출력합니다.

local_css(os.path.join(CSS_PATH, "background.css"))


# local_css("css/1_user.css")
st.markdown(
            f"""
            <style>
                @keyframes fadeInDown {{
                    0% {{
                        opacity: 0;
                        transform: translate3d(0, -10%, 0);
                        }}
                    to {{
                        opacity: 1;
                        transform: translateZ(0);
                        }}
                }}
                .main {{
                    background-color: #99A7E4; /* 배경색 */
                    background-size:cover;
                    margin:0px;
                }}
                .css-z5fcl4 {{ 
                        margin-left : 10%;
                        margin-right : 10%;
                        margin-top : 2rem;
                        display : flex;  
                }}
                div.row-widget.stRadio > div{{
                    display : flex;
                    justify-content : space-around;
                    align-items: center;
                    flex-basis : 3rem;
                }}
                [role="radiogroup"] {{
                    margin : 0 auto;
                }}
                [data-baseweb="radio"] {{
                    margin : 0;
                }}
                /*
                .st-dr, .st-dt, .st-du, .st-ed{{
                    margin : 0 auto;
                    margin-right :0;
                    margin-left:2px;
                }}
                */
                [data-baseweb="radio"] div {{
                    background-color : #2D5AF0;
                }}
                [data-baseweb="radio"] div>div {{
                    background-color : #FFFFFF;
                }}
                [data-baseweb="radio"] div:nth-child(3) {{
                    visibility:hidden;
                }}
                .st-en, .st-em, .st-el, .st-ek {{
                    border-color : #2D5AF0;
                }}
                .essential_menu{{
                    color : #5271FF;
                }}
                .menu_name {{
                    font-size : 20px;
                    padding-top : 0px;
                    font-family : 'Nanumsquare'
                }}
                .css-115gedg {{
                    display : flex;
                    align-content: stretch;
                }}
                .css-vsyxl8{{
                    display : flex;
                    flex-wrap: wrap;
                    align-content: stretch;
                }}
                .main_message {{
                    word-break: keep-all;
                    font-size : 36px;
                    text-align : left;
                    font-weight : bold;
                    margin-top : 14%;
                    font-family : 'Nanumsquare';
                    animation: fadeInDown 1s;
                    margin-left : 8rem;
                    margin-bottom : 2rem;
                    color : black;
                }}
                #real_ad {{
                    margin-left : 8rem;
                    margin-bottom : 1rem;
                    box-sizing:content-box;
                }}
                .additional_message {{
                    display : flex;
                    flex-grow : 1;
                    justify-content : start;
                    color : #1c1c1c;
                    font-family : 'Nanumsquare';
                }}
                .info_message {{
                    display : flex;
                    flex-grow : 1;
                    justify
                    -content : end;
                    color : #1c1c1c;
                    font-family : 'Nanumsquare'
                }}
                .check_message{{
                    word-break: keep-all;
                    font-size : 20px;
                    text-align : left;
                    font-weight : 700;
                    color : red;
                    font-family : 'Nanumsquare';
                    margin-left : 8rem;
                    margin-right : 8rem;
                }}
                [class="row-widget stButton"] {{
                    display : flex;
                    justify-content : start;
                    margin-left : auto;
                    margin-right : auto;

                }}
                [class="row-widget stButton"] button {{
                    border : none;
                    margin-left : 8rem;
                    background-color: transparent;
                }}
                [class="row-widget stButton"] button:hover {{
                    background-color: transparent;
                }}
                [class="row-widget stButton"] button>div {{
                    display : flex;
                    border-radius: 50px;
                    background : #D9D9D9;
                    filter: drop-shadow(0px 4px 4px rgba(0, 0, 0, 0.25));
                    width : 9em;
                    height : 2.5em;
                    font-size : 40px;
                    justify-content : center;
                    font-family : 'Nanumsquare';
                }}
                [class="row-widget stButton"] button>div:hover{{
                    transform : scale(1.1);
                    background : #5271FF;
                    transition : .5s;
                }}
                [class="row-widget stButton"] button>div>p {{
                    font-size : 40px;
                    font-weight: 700;
                    color: #1c1c1c;
                    text-align: center;
                    margin : auto;
                }}
                [data-testid="stHorizontalBlock"] {{
                    justify-content : space-around;
                    flex-direction: row;
                    flex-wrap : wrap;
                }}
                /* 결과 샘플 */
                [data-testid="stHorizontalBlock"] > div:nth-child(2) > div > div> div:nth-child(4) > div {{
                    margin-left : 8rem;
                    max-width : 80%;
                    justify-content: flex-start;
                }}
                [data-testid="stExpander"] {{
                    margin-left : 7rem;
                    max-width : 70%;
                }}
                [data-baseweb="accordion"] {{
                    border : none;
                }}
                [data-baseweb="accordion"] >li >div >svg {{
                    visibility : hidden;
                }}
                </style>""",
                unsafe_allow_html=True,)

###########여까지 마크다운으로 화면 보여줌
## emoji for interviewer icon

## custom message
info_message = ""
main_message = "당신의 면접, <br>JOBits 로 준비해 보세요."


## read job info tb
job_info, JOBS = read_job_info_tb(os.path.join(DATA_DIR,  "samples", "job_info_tb.parquet"))
st.session_state.job_info = job_info
st.session_state.logger.info("read job tb")
st.session_state.logger.info(f"job info is ... {JOBS}")
st.session_state.big_q_progress = True

## input_form
input_form, start_button = st.columns([1, 2])  # 노션 컬럼처럼 열을 나눠서 할수있게 해주는것
with input_form:
    

    st.session_state.user_name = st.session_state.nickname
    st.session_state.logger.info(f"user name : {st.session_state.user_name}")

    ### 이력서 폼

    input_form.markdown('''
                        <div class="menu_name">이력서<span style="font-size:14px; color: #5271FF;">(200MB이하 PDF파일만 지원)</span><span class="essential_menu">*</span></div>
                        ''', 
                        unsafe_allow_html=True)
    
    user_resume = st.session_state['user_email'] + "uploaded_resume"
    st.session_state[user_resume] = input_form.file_uploader("이력서", accept_multiple_files=False, type = ['pdf'], label_visibility='collapsed')
    # 이력서 없이 시작하기 옵션을 추가합니다. skip_resume: bool
    st.session_state.skip_resume = st.checkbox("이력서 없이 시작하기")

    st.session_state.logger.info(f"upload resume -> Sucess")
    

    ### JD 폼 ######################
    input_form.markdown('''
                        <div class="menu_name">채용공고<span style="font-size:14px; color: #5271FF;">(1500자 이내로 작성해주세요)</span><span class="essential_menu">*</span></div>
                        ''', 
                        unsafe_allow_html=True)
     # 사용자에게 텍스트 입력을 요청하는 텍스트 영역 생성
    st.session_state.jd_text = st.text_area("채용 공고", max_chars=1500,value=EXAMPLE_JD,height=300)
    
    user_jd = st.session_state['user_email'] + "uploaded_JD"
    st.session_state[user_jd] = save_uploaded_jd_as_filepath( # text, path, filename="uploaded_jd.txt" 형태
                                                                st.session_state.jd_text,
                                                                SAVE_JD_FILE_DIR
                                                                ) # 파일 경로에 저장됩니다.

    
    
    st.session_state.logger.info(f"upload JD -> Sucess")

    st.session_state.temperature = 0.2
    st.session_state.logger.info(f"interview style (temperature) : {st.session_state.temperature}")
    
    ## start_button
    with start_button:
        start_button.markdown(f""" <div class = 'main_message'> {main_message}<br></div> """,
                              unsafe_allow_html=True,)
        ### 필요사항체크
        check_list, josa= check_essential(st.session_state[user_resume],st.session_state.skip_resume,st.session_state.jd_text)        
        
        st.session_state.logger.info(f"check_essential")
        ### 필요사항 따라 버튼 클릭시 안내 문구 생성
        if start_button.button("예상 질문 확인하기"):
            if check_list:
                start_button.markdown(f"""<p class = 'check_message'>{', '.join(check_list)}{josa[-1]} 필요해요! </p>""",
                                      unsafe_allow_html=True,)
            
            else:
                if st.session_state.skip_resume :
                    st.session_state.cur_task = "gene_question"  # 예상 질문 생성하기 수행
                    switch_page(NEXT_PAGE_NORESUME)
                    
                else:
                    st.session_state.cur_task = "gene_question"  # 예상 질문 생성하기 수행
                    switch_page(NEXT_PAGE)
                    st.session_state.logger.info(f"check_essential | Pass")

        if start_button.button("모의면접 시작하기"):
            ### 유저 고유 폴더 생성
            if check_list:
                start_button.markdown(f"""<p class = 'check_message'>{', '.join(check_list)}{josa[-1]} 필요해요! </p>""",
                                      unsafe_allow_html=True,)
            else:
                
                if st.session_state.skip_resume :
                    st.session_state.cur_task = "interview"  # 예상 질문 생성하기 수행
                    switch_page(NEXT_PAGE_NORESUME)
                    
                else:
                    st.session_state.cur_task = "interview"  # 모의면접 수행
                    switch_page(NEXT_PAGE)
                    st.session_state.logger.info(f"check_essential | Pass")

    # 광고 공간
    start_button.markdown(f"""
                          <div class='ad_space'>
                          <div id='real_ad'> </div>
                          """,
                          unsafe_allow_html=True,)