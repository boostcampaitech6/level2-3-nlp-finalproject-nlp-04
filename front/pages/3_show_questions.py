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