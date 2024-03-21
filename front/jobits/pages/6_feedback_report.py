import streamlit as st
from langchain.chat_models import ChatOpenAI
from openai import OpenAI

api_key = OPENAI_API_KEY
client = OpenAI(
    api_key=api_key,
)

# 질문과 답변을 함께 'user'의 메시지로 포함시킵니다.
def generate_feedback_for_qa_pair(system, question, answer):
    combined_message = f"질문: {question}\n답변: {answer}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": combined_message},
        ],
    )
    response = response.json()
    response = json.loads(response)
    return response["choices"][0]["message"]['content']

system = """예상 면접 질문의 의도를 파악하고, 이를 바탕으로 사용자의 답변에 대한 피드백을 제공하세요."""
past_responses = st.session_state.get('past', [])
generated_questions = st.session_state.get('generated', [])
paired_qa = list(zip(generated_questions, past_responses))

st.title("모의 면접 종합 피드백")

# 세션 상태에서 가져온 질문-답변 쌍(paired_qa)에 대해 피드백을 생성하고 표시합니다.
for idx, (question, answer) in enumerate(paired_qa):
    feedback = generate_feedback_for_qa_pair(system, question, answer)
    st.markdown(f"### 질문 {idx+1}")
    st.text(question)
    st.markdown("### 답변")
    st.text(answer)
    st.markdown("### 피드백")
    st.text(feedback)
    st.write("---")
