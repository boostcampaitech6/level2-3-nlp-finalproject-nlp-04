import os
import streamlit as st
from utils.util import load_chain
from streamlit_chat import message
from back.config import DATA_DIR
from PIL import Image

st.session_state['FAV_IMAGE_PATH'] = os.path.join(DATA_DIR,'images/favicon.png')
st.set_page_config(
     page_title="Hello Jobits", # 브라우저탭에 뜰 제목
     
     page_icon=Image.open(st.session_state.FAV_IMAGE_PATH), #브라우저 탭에 뜰 아이콘,Image.open 을 이용해 특정경로 이미지 로드 
     layout="wide",
     initial_sidebar_state="collapsed"
)
st.title('모의면접 ChatGPT-3 (Demo)')
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "assistant",
                                        "content": "안녕하세요, 면접 시작하도록 하겠습니다."}]
# 질문 초기화
questions = ['Boostcamp AI Tech 6기에서 진행한 NLP 분야 대회 프로젝트에서 사용한 DPR 모델의 동작 원리와 장점에 대해 설명해주세요.', 'Boostcamp AI Tech 6기에서 진행한 NLP 분야 대회 프로젝트에서 Curriculum Learning을 적용한 이유와 어떤 방식으로 적용하였는지 설명해주세요.']
current_question_idx = 0
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
# 대화 로직
def chat(question):
    chain = load_chain(question)
    count = 0
    with st.chat_message('assistant'):
        st.session_state.messages.append({"role": "assistant", "content": question})
        st.markdown(question)
    #st.write(1)
    while True :
        user_input = st.chat_input("면접자: ", key="unique_key")
        if user_input:
            with st.chat_message('user'):
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.markdown(user_input)
            result = chain.predict(input=user_input)
            with st.chat_message('assistant'):
                st.session_state.messages.append({"role": "assistant", "content": result})
                st.markdown(result)
            count += 1
            if count > 2:
               st.write('수고하셨습니다.')
            if result == '다음 질문으로 넘어가겠습니다.':
                break
if __name__ == '__main__':
    for question in questions:
        #st.write('main')
        chat(question)
    print("수고하셨습니다. ")
