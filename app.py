import logging
import os

import streamlit as st
from PIL import Image
from streamlit_extras.switch_page_button import switch_page


from back.streamlit_control import goto_login_page
from config import IMG_PATH
from src.util import get_image_base64


st.session_state["FAV_IMAGE_PATH"] = os.path.join(IMG_PATH, "favicon.png")

st.set_page_config(page_title="Hello Jobits",  # 브라우저탭에 뜰 제목
                   page_icon=Image.open(st.session_state.FAV_IMAGE_PATH),  # 브라우저 탭에 뜰 아이콘
                   layout="wide",
                   initial_sidebar_state="collapsed",)

# 로거 초기화
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

check_result = []
st.session_state["START_IMG"] = get_image_base64(os.path.join(IMG_PATH, "start_jobits.png"))
START_IMG = st.session_state.START_IMG

#image = Image.open(os.path.join(IMG_PATH, "start.png"))

st.markdown('<div class="center" ><img src="data:image/png;base64,'+ get_image_base64(os.path.join(IMG_PATH, "start_jobits.png"))+'" style="width: 100%; height: auto;"/></div>', unsafe_allow_html=True)

#st.markdown('<div class="center"><img src="data:image2/png;base64,'+ get_image_base64(os.path.join(IMG_PATH, "intro_message.png"))+'" style="width: 90%; height: auto;"/></div>', unsafe_allow_html=True)

# 버튼들을 화면 오른쪽 아래에 배치하기 위해 CSS 스타일을 적용합니다.
st.markdown(f"""
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
                    background-color: #FFFFFF; /* 배경색 */
                    padding: 10px;
                    background-attachment: fixed;
                    display: flex;
                    align-items: center; /* 세로 방향으로 중앙 정렬 */
                    height: 100vh; /* 화면 전체 높이만큼 설정 */
                }}
                .button-container {{
                    position: fixed; /* 화면에 고정시킴 */
                    display: flex;
                    align-items: center; /* 세로 방향으로 중앙 정렬 */
                    width : 100%
                    height: 0;
                }}
                [class="row-widget stButton"] button {{
                    border : none;
                    margin-left : 50%;
                    background-color: transparent;
                    animation: fadeInDown 1s;
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
                    color: #FFFFFF;
                    text-align: center;
                    margin : auto;
                }}
                [class="row-widget stButton"] button:first-child {{
                    top : 50em; /* 시작하기 버튼을 현재 위치에서 위로 20만큼 이동 */
                }}
            </style>
            """,
            unsafe_allow_html=True,
            )

# 개인정보 처리방침 내용
privacy_policy = """
「개인정보 보호법」 제15조 및 제22조에 따라 아래와 같은 내용으로 본인의 개인정보를 수집‧이용하는데 동의합니다.



• 수집∙이용 목적

: 개발자 모의면접 서비스 제공을 위한 유저 식별, 예상 질문 생성, 모의면접 진행 등의 서비스에 이용

• 수집ㆍ이용할 개인정보의 내용

: 이름, 이메일, 이력서

• 보유 및 이용 기간

: 수집‧이용 동의일로부터 6개월 이내

※ 귀하는 이에 동의를 거부할 수 있습니다.

다만 동의가 없을 경우 본 서비스 사용이 불가합니다."""

# 스트림릿으로 개인정보 처리방침 내용을 보여줌
st.text_area("개인정보 처리방침", privacy_policy, height=300)

# 동의 여부를 라디오 버튼으로 선택
consent = st.radio("위 개인정보 처리방침에 동의하십니까?", ('동의', '동의하지 않음'))
st.session_state.agreement = consent




# # 사용자가 선택한 값에 따라 다르게 행동
# if st.button("제출"):
#     if consent == '동의':
#         st.success("이용 약관에 동의하셨습니다. 감사합니다!")
#     else:
#         st.error("이용 약관에 동의하지 않으셨습니다. 동의가 필요합니다.")
        
check_list = st.session_state.agreement

if st.button("LOGIN(KAKAO)"):
    if check_list != '동의':
        st.error("동의하지 않으셨습니다. 동의가 필요합니다.")
    else:
        st.session_state["cur_user"] = "kakao"  # 사용자 상태 설정
        goto_login_page()
        
    

# 비회원 버튼
if st.button("GUEST"):
    if check_list != '동의':
        st.error("동의하지 않으셨습니다. 동의가 필요합니다.")
    else:
        st.session_state["cur_user"] = "guest"  # 사용자 상태 설정
        switch_page("home")

