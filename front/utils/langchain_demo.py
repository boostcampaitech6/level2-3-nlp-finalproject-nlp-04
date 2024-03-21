

import os
import pandas as pd
import tiktoken
import chromadb
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import LLMChain


#openai key 설정
os.environ['OPENAI_API_KEY'] = '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'
api_key = os.environ.get('OPENAI_API_KEY')

### 채용공고에서 핵심 기술 추출 - 직무명, 주요업무, 필요역량 및 우대조건
llm = ChatOpenAI(temperature=0)

# Pass question to the qa_chain
prompt_template = '''
아래와 같은 채용공고에서 핵심 내용을 추출해서 요약해주세요. 추출할 내용은 다음과 같으며, 내용은 한국어로 생성해주세요.

직무명 :
주요 업무 :
필요역량 및 우대조건 :

채용공고 : {jd}
추출할 내용 : 직무명, 주요업무, 필요역량 및 우대조건

'''

prompt = PromptTemplate(
    template=prompt_template, input_variables=["jd"])


jd = '''
조직소개

우리 조직은 전사 데이터의 가치를 최대화하는 역할을 담당하는 조직입니다. 데이터 수집, 처리 및 분석 과정을 통해 전략적 인사이트를 도출하고, 이를 기반으로 비즈니스 문제를 해결하는 핵심 역할을 합니다. 최신 인공지능 기술을 신속하게 검토 및 활용하여 예측 모델을 개발하고, 이를 통해 업무 효율성 향상과 비즈니스 성장을 도모합니다. 또한 회사 내 데이터 기반의 문화를 조성하여 모든 직원이 데이터를 이해하고 활용할 수 있도록 데이터 리터러시를 향상시키는 데 기여합니다.
ㅤ

직무상세

[제조 및 SCM 영역 최적화 모델 개발 지원]
- 제조공정에서 발생되는 시계열/다변량 데이터 분석(시각화, 주요 인자 발굴, 이상 감지 등)- SCM 관련 최적화 모형 개발(수요/리스크 예측, 재고/물류 최적화 등)
[컴퓨터 비전 알고리즘 개발 지원]
- 이미지 기반 품질불량 검출 모델 개발- 영상데이터 객체 탐지, 맥락 분석, 변환 기술 개발
[LLM 모델 개발 지원]
- LLM 기반 생성형 AI 연구 개발- sLLM 기반 모델 연구 및 서비스 개발
ㅤ

지원자격

산업공학, 인공지능, 컴퓨터공학, 통계학 관련 전공자
※ 기계/전자/전기공학 전공자 중 AI/ML 유관 전공자 포함

2024년 4월 ~ 2024년 9월 (6개월) 인턴 실습이 가능한 자
※ 최종 합격 후 회사에서 지정하는 날짜에 입사 가능하고 Full Time 근무가 가능자에 한합니다.
ㅤ

우대사항

관련 분야 논문, 공모전 성과 우수자
최신 논문(알고리즘)을 이해하고 구현할수 있는 수준의 연구/개발 능력 보유자
오픈소스 기반 최신 딥러닝 프레임워크 활용 능력 보유자(Tensorflow, Pytorch 등)
커뮤니케이션 역량 우수자
전형절차

지원서 접수(3월) → 코딩테스트(3월) → 면접 전형(4월) → 채용 검진(4월) → 입사(4월) ※ 운영 상황에 따라 일부 전형은 온라인으로 진행될 수 있으며, 전형 및 일정 또한 변경될 수 있습니다.
기타

본 공고는 입사 시 사전에 근로계약기간을 약정하고, 해당 종료일 도래 시 근로계약이 종료되는 기간제 근로 형태입니다.
본 공고의 상세 일정은 전형별 합격자에 한하여 개별 안내드릴 예정입니다.
지원서를 포함한 채용 전형 전 과정에서 제출한 내용이 사실과 다르거나 문서로 증빙이 불가할 경우, 혹은 고의적인 기재사항 누락이 확인될 경우 합격이 취소되거나 전형 상의 불이익을 받을 수 있습니다.
취업보호대상자(장애, 보훈 등)는 관계 법령에 의거하여 우대합니다.
입사지원자는 지원시점부터 채용 전 과정에 걸쳐 전/현직 직장의 영업비밀을 침해하는 일이 없도록 각별히 유의 바랍니다.
지원서 접수는 온라인(채용사이트)을 통해 접수하며, 그 외의 개별 접수는 받지 않습니다.
전형이 진행중인 경우, 당사 타 공고에 중복 지원 불가합니다. 단, 전형이 종료된 이후(전형포기 및 탈락)에는 당사 타 공고에 지원이 가능합니다. 예시) - 경영지원부문 전형 진행 中, 경영지원부문 내 타 공고 중복지원 불가 - 경영지원부문 전형 진행 中, 타 사업부(부문/BU) 내 공고 중복지원 불가 - 경영지원부문 전형 종료(전형포기 및 탈락) 후, 타 공고 지원 가능. ※ 전형포기: 본인의 의사로 전형을 포기할 경우, 해당 전형 인사담당자에게 전형포기 의사를 밝힌 시점부터 타 공고 지원 가능합니다. ※ 탈락: 전형 결과 발표에서 불합격 통보를 받은 인원의 경우, 불합격 통보 시점부터 타 공고 지원 가능합니다.
'''

chain = LLMChain(llm=llm, prompt=prompt)

job_description = chain.run(jd)


###############################


# 이력서 질문 생성
# user 이력서 입력
text_splitter = CharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
    )

loader = PyPDFLoader("koo.pdf")
pages = loader.load_and_split(text_splitter)

vector_index = Chroma.from_documents(
    pages, # Documents
    OpenAIEmbeddings(),) # Text embedding model

# user_resume_lst = [n.page_content for n in pages]
# user_resume = " \n ".join(user_resume_lst)
llm = ChatOpenAI(temperature=0)

# Pass question to the qa_chain
prompt_template = '''
당신은 IT 기업의 채용 담당자입니다.
아래 채용 공고 내용과 면접자의 이력서를 바탕으로 기술 면접 질문을 작성해 주시기 바랍니다.
이때, 면접자의 이력서 프로젝트에서 채용공고 내용과 유사한 내용이 있으면 해당 내용을 중심으로 기술 면접 질문을 생성해주세요.
검색한 다음 컨텍스트를 사용하여 기술 인터뷰 질문을 생성합니다. 인터뷰 질문은 한국어로 생성해주세요.
만약 답을 모른다면, 그냥 모른다고 말하세요. 문장을 세 개까지 사용하고 답을 간결하게 유지하세요.

{context}

채용공고: {question}
'''

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chain_type_kwargs = {"prompt": PROMPT}
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_index.as_retriever(),)


qa_chain.run(job_description)

