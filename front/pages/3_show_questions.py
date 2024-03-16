# 인터뷰 진행이 아닌 예상 질문을 모아보기 위한 임시 페이지 입니다.
import streamlit as st
import yaml

# YAML 파일 로드
with open("secret_key.yaml", "r") as yaml_file:
    config = yaml.safe_load(yaml_file)
    
st.session_state.logger.info("start show_questions page")

# 사용자 정의 CSS 스타일을 추가합니다.
st.markdown(
    """
    <style>
    .stExpander > div:first-child {
        font-weight: bold;
        color: navy;
        border: 1px solid rgba(28, 131, 225, 0.1);
        border-radius: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# questions 
questions = st.session_state.main_question

# 사용자 인터페이스 생성

st.title(f'{st.session_state.user_name}님의 이력서 예상 질문입니다.')


# 각 질문에 대해 번호를 매기고 토글 위젯 생성
for i, question in enumerate(questions, 1):
    # 질문이 비어있거나 개행 문자만 포함된 경우 토글을 생성하지 않음
    if question.strip():
        # 토글 위젯 생성
        with st.expander(f"{i}. {question}", expanded=False):
            st.caption("질문에 대한 답변을 500자 이내로 작성해 주세요")
            # 텍스트 입력 박스
            user_input = st.text_area("답변:", key=f"input_{i}", max_chars=500)
            
            # 답변하기 버튼
            if st.button("답변하기", key=f"button_{i}"):
                # 버튼 클릭 시 안내 텍스트 출력
                st.text("답변이 제출되었습니다.")
            
            
'''
휴 tlqkf 프롬프트 뭐가문제지. 못읽어오는데. 이력서도 이상하게 읽어오고. 민석스 이력서는 제대로 읽어오지도 못함. 질문이 개떡이야 ㅅㅂ

상수스
1. 이력서에서 언급된 NLP, Machine Learning, Prompt Engineering에 대해 어떤 경험이 있으신가요?
2. 이력서에서 언급된 Python, Pytorch, Scikit-Learn에 대해 어떤 프로젝트나 경험이 있으신가요?
3. Boostcamp AI Tech 6th 교육을 통해 어떤 프로젝트를 진행하셨나요? 해당 프로젝트에서 어떤 역할을 맡았고 어떤 기술을 활용했나요?
4. 데이터 세상 동아리 회장으로 활동하면서 어떤 프로젝트를 진행했고 어떤 역할을 맡았나요?
5. 멘토링 멘토로 참여하면서 어떤 과목을 가르치고 어떤 도움을 주었나요?
6. 데이터 사이언스 학술제에서 수상한 프로젝트에 대해 자세히 설명해주세요. 프로젝트를 진행하면서 어떤 어려움을 겪었고 어떤 결과를 얻었나요?

민석스
1. 면접자의 이력서에는 어떤 프로젝트 경험이 있나요? 해당 프로젝트에서 어떤 역할을 맡았고, 어떤 기술을 사용했나요?

2. 면접자가 언급한 NLP, Machine Learning, Prompt Engineering에 대해 자세히 설명해주세요. 이 분야에서 어떤 경험이 있나요?

3. 면접자가 언급한 Python, Pytorch, Scikit-Learn에 대해 어떤 경험이 있나요? 이 도구들을 사용하여 어떤 프로젝트를 진행한 적이 있나요?

4. 면접자가 언급한 Boostcamp AI Tech 6기 교육과정에서 어떤 프로젝트를 진행했나요? 프로젝트에서 어떤 역할을 맡았고, 어떤 기술을 사용했나요?

5. 면접자가 언급한 데이터 사이언스 학술제에서 어떤 프로젝트를 진행했나요? 프로젝트의 주제와 선정 이유, 진행한 내용에 대해 설명해주세요.

6. 면접자가 언급한 기술면접 준비를 도우미 AI 프로젝트에서 어떤 역할을 맡았나요? 프로젝트의 주요 내용과 진행한 과정에 대해 설명해주세요.
'''
