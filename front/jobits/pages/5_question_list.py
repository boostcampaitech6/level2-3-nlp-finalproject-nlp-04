from openai import OpenAI
import streamlit as st
from streamlit_chat import message
import json
from front.jobits.src.mypath import MY_PATH
from back.config import OPENAI_API_KEY

client = OpenAI(
    api_key=OPENAI_API_KEY,
)
system = "prompting"
user = "안녕?"
st.title('list')

# feedback을 기록해서 전달해주는 함수.
def feedback_gpt(string, user):
    # 페르소나 및 프로프팅
    system = f"""prompting"""

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


system = """prompting"""
 
 
st.header("🤖Yunwoong's ChatGPT-3 (Demo)")
st.markdown("[Be Original](https://yunwoong.tistory.com/)")


# Expander 1
with st.expander("Expander 1"):
    string1 = """1. 프로젝트에서 '채용공고 최신 동향 파악' 주제를 선정한 이유에 대해 설명해주세요. 해당 주제를 선택한 이유와 프로젝트를 통해 어떤 문제를 해결하고자 했는지에 대해 알려주세요."""
    st.write(string1)
    text_input1 = st.text_area(f"{string1}에 대한 답변을 입력해주세요", height=500)
    with st.form('form1', clear_on_submit=True):
        submitted = st.form_submit_button('Send')
    if submitted and text_input1:
        st.write("피드백:", feedback_gpt(string1, text_input1))

# Expander 2
with st.expander("Expander 2"):
    string2 ="""2. 프로젝트에서 사용한 기술인 selenium, konlpy, Scikit-Learn의 각각의 역할과 사용 이유에 대해 설명해주세요. 각 기술이 어떻게 프로젝트의 성과에 기여했는지에 대해 알려주세요."""
    st.write(string2)
    text_input2 = st.text_area(f"{string2}에 대한 답변을 입력해주세요", height=500)
    with st.form('form2', clear_on_submit=True):
        submitted = st.form_submit_button('Send')
    if submitted and text_input2:
        st.write("피드백:", feedback_gpt(string2, text_input2))

# Expander 3
with st.expander("Expander 3"):
    string3 = """3. 프로젝트를 진행하면서 발생한 어려움이나 아쉬운 점에 대해 이야기해주세요. 특히 '프로덕트 서빙 방법을 몰라서 배포하지 못한 것이 아쉬움으로 남는다'는 부분에 대해 자세히 설명해주세요."""
    st.write(string3)
    text_input3 = st.text_area(f"{string3}에 대한 답변을 입력해주세요", height=500)
    with st.form('form3', clear_on_submit=True):
        submitted = st.form_submit_button('Send')
    if submitted and text_input3:
        st.write("피드백:", feedback_gpt(string3, text_input3))