import streamlit as st
from langchain.chat_models import ChatOpenAI
from openai import OpenAI

api_key = OPENAI_API_KEY # 유효 API key로 교체
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
    return response["choices"][0]["message"]["content"]


system = """예상 면접 질문의 의도를 파악하고, 이를 바탕으로 사용자의 답변에 대한 피드백을 제공하세요."""

st.title("모의 면접 종합 피드백")

# 세션 상태에서 가져온 질문-답변 쌍(paired_qa)에 대해 피드백을 생성하고 표시합니다.
if st.button("피드백 받기"):
    # 세션 상태에서 정보 가져오기
    past_responses = st.session_state.get("answer", [])
    generated_questions = st.session_state.get("main_question", [])
    tail_questions = st.session_state.get("tail", [])
    paired_qa = list(zip(generated_questions, past_responses))

    # 피드백 데이터를 저장할 리스트 초기화
    feedback_data = []

    # 각 질문-답변 쌍에 대한 피드백 생성 및 데이터 저장
    for question, answer in paired_qa:
        feedback = generate_feedback_for_qa_pair(system, question, answer)
        feedback_data.append(["질문", question, feedback])
        feedback_data.append(["답변", answer, feedback])

    # 꼬리질문에 대한 피드백 추가
    for tail_question in tail_questions:
        feedback = generate_feedback_for_qa_pair(system, tail_question, "")
        feedback_data.append(["꼬리질문", tail_question, feedback])

    # 피드백 테이블을 표시
    st.table(feedback_data)
