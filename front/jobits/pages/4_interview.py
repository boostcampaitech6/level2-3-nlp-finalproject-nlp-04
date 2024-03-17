from openai import OpenAI
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_chat import message
import json
from front.jobits.src.mypath import MY_PATH
from back.config import OPENAI_API_KEY
NEXT_PAGE = 'question_list'

api_key = OPENAI_API_KEY
client = OpenAI(
    api_key=api_key,
)
system = "You are helpful AI"
user = "안녕?"

st.set_page_config(
    page_title = "generate"
)
st.title('mock-up interview')
# st.sidebar.success('select')

def run_gpt(system, user):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",  # 또는 다른 모델을 사용
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
)
    response = response.json()
    response = json.loads(response)
    return response["choices"][0]["message"]['content']


system = """당신은 사용자를 도와주는 사람입니다."""
 
 
st.header("🤖모의면접 ChatGPT-3 (Demo)")
st.markdown("[Be Original](https://yunwoong.tistory.com/)")
 
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
 
if 'past' not in st.session_state:
    st.session_state['past'] = []
 
with st.form('form', clear_on_submit=True):
    user_input = st.text_input('You: ', '', key='input')
    submitted = st.form_submit_button('Send')
 
if submitted and user_input:
    output = run_gpt(system, user_input)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)
 
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))

if st.button("다음 페이지"):
    switch_page(NEXT_PAGE)