import os
import sys
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from loguru import logger as _logger

sys.path.append("./")

from etc.utils.logger import DevConfig
from etc.utils.util import get_image_base64,read_gif,read_prompt_from_txt
from PIL import Image
import yaml

# '''
# 이 페이지를 가장 먼저 호출하여 loggger 나 이미지 패스 같은 부분들을 모두 실행합니다.
# 그 후 최하단의 switch_page(NEXT_PAGE) 를 실행하여 user 페이지로 이동합니다. 

# Loguru 라이브러리에서 로거 인스턴스는 여러 로깅 메서드를 제공하는데, 이는 로그 메시지를 다양한 수준에서 기록할 수 있게 해줍니다. 주요 로깅 메서드는 다음과 같습니다:

# .debug(): 디버그 수준의 로깅을 수행합니다. 가장 낮은 로깅 레벨로, 상세한 시스템 정보를 기록할 때 사용됩니다.
# .info(): 정보 수준의 로깅을 수행합니다. 애플리케이션이 정상적으로 작동하고 있는 상황에서 일반적인 정보를 기록할 때 사용됩니다.
# .warning(): 경고 수준의 로깅을 수행합니다. 주의가 필요한 상황이나 예상치 못한 문제를 기록할 때 사용됩니다.
# .error(): 오류 수준의 로깅을 수행합니다. 예외 처리나 중대한 문제가 발생했을 때 사용됩니다.
# .critical(): 심각한 수준의 로깅을 수행합니다. 시스템의 중대한 실패나 긴급 상황을 기록할 때 사용됩니다.


# '''
# YAML 파일 로드
with open("secret_key.yaml", "r") as yaml_file:
    config = yaml.safe_load(yaml_file)
    
#OPENAI_API_KEY = read_prompt_from_txt("/root/yehjeans/hireview/data/test/OPANAI_KEY.txt")
OPENAI_API_KEY = config['OPENAI_API_KEY']
OPENAI_API_KEY_DIR = 'api_key.txt'
NEXT_PAGE = 'user'
DATA_DIR = config['STREAMLIT']['DATA_DIR']

if "logger" not in st.session_state:
    # logru_logger(**config.config)
    config = DevConfig
    _logger.configure(**config.config)
    st.session_state["logger"] = _logger # session_state에 ["logger"] 라는 키값을 추가하여 사용
    st.session_state["save_dir"] = config.SAVE_DIR

if "openai_api_key" not in st.session_state:
    # with open(OPENAI_API_KEY_DIR) as f:
    #     OPENAI_API_KEY = f.read()
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    st.session_state.openai_api_key = OPENAI_API_KEY

if "MAIN_IMG" not in st.session_state:
    st.session_state['MAIN_IMG'] = get_image_base64( DATA_DIR + 'images/main_back.png')

if "LOGO_IMG" not in st.session_state:
    st.session_state['LOGO_IMG'] = get_image_base64( DATA_DIR + 'images/logo_square.png')
    
if "FAV_IMAGE_PATH" not in st.session_state:
    st.session_state['FAV_IMAGE_PATH'] = DATA_DIR + '/images/favicon.png'

if "LOGO_IMAGE_PATH" not in st.session_state:
    st.session_state['LOGO_IMAGE_PATH'] = DATA_DIR + '/images/logo_square.png'

if "LOADING_GIF1" not in st.session_state:
    st.session_state['LOADING_GIF1'] = read_gif( DATA_DIR + '/images/loading_interview_1.gif')
    
if "LOADING_GIF2" not in st.session_state:
    st.session_state['LOADING_GIF2'] = read_gif( DATA_DIR + '/images/loading_interview_2.gif')

if "USER_ICON" not in st.session_state:
    st.session_state['USER_ICON'] = Image.open( DATA_DIR + '/images/user_icon.png')

if "user_name" not in st.session_state:
    st.session_state['user_name'] = '아무개'
    
if "temperature" not in st.session_state:
    st.session_state['temperature'] = 0

if "INTERVIEWER_ICON" not in st.session_state:
    st.session_state['INTERVIEWER_ICON'] = '🐾'
    
switch_page(NEXT_PAGE)
