__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

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

import yaml


with open("../secret_key.yaml", "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

# OpenAI API 키를 환경 변수로 설정
os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']
api_key = config['OPENAI_API_KEY']

# 채용공고에서 핵심 기술 추출 - 직무명, 주요업무, 필요역량 및 우대조건
llm = ChatOpenAI(temperature=0)



# 파일 경로 및 이름 설정
ABILITY_SUM_PROMPT_PATH = config['ABILITY_KE_QUESTIONSUM_PROMPT']
MAKE_QUESTION_PROMPT_PATH = config['MA_PROMPT']

# 텍스트 파일 읽기
with open(ABILITY_SUM_PROMPT_PATH, 'r', encoding='utf-8') as file:
    ABILITY_SUM_PROMPT = file.read()


# Pass question to the qa_chain
prompt_template = ABILITY_SUM_PROMPT


prompt = PromptTemplate(
    template=prompt_template, input_variables=["jd"])


# jd 예시 입력
jd = '''

jd:
Language Lab은 자연어 처리 분야의 기술적 난제 해결을 위한 핵심 선행기술을 연구하며 Learning-by-Reading AI 확보를 통한 챗봇 등 Language 분야 서비스 혁신 이라는 비전을 가지고 있습니다.
최적의 개발 환경에서 다양한 현장의 데이터를 다루어 볼 수 있는 기회이자, 최고의 전문가들과 함께 심도있게 연구하고 구현해 보는 값진 경험을 쌓을 수 있는 인턴 프로그램에 지원해주세요!
수행 업무
[Internship - 채용 포지션 (4)]
- 초거대 언어모델 개발- 한국어 언어 모델 Tuning
- 한국어 언어 모델 벤치마크 구축
- 한국어 언어 모델 Inference 엔진 최적화
- 심층문서이해 기술 개발 - 영어 Chemical 도메인의 언어 모델을 위한 데이터 처리 및 모델 튜닝
- 강화학습 기반 언어모델 개발- 강화학습 기반 언어모델 개발 관련 데이터 처리 및 모델 튜닝
- 테이블이해 기술(TableMRC) 개발- 테이블 구조 이해를 위한 언어모델 (Pre-trained Langauge Model) 구현
- 한국어 모델 Tuning 및 Inference 엔진 최적화
지원자격
- 학사/석사/박사 무관
- 6개월 이상 근무 가능하신 분 (일정은 개별 조율 가능합니다)
필요역량/우대사항
- Linux, Python, HuggingFace 언어 모델 활용 능력
- 한국어 언어 모델 튜닝 숙련자 우대
- 한국어 벤치마크 구축 경험자 우대
- Multi-GPU Model-Parallelism 경험자 우대
- HuggingFace Transformers 등 Deep NLP 학습 경험 (pytorch or jax)
- Linux 활용 능숙, python 코딩 중급 이상, github 등 Coding Tool 활용 능력
- 최신 딥러닝 논문 독해
전형절차
서류심사 → 코딩테스트 → 1차 기술 인터뷰(온라인) → 최종 합격
* 전형 절차는 변경될 수 있습니다. 서류 합격 시 전형 절차에 대해 별도로 안내 해 드립니다.
현재 LG AI연구원은 병역지정업체가 아님으로, 전문연구요원 채용 및 전직이 불가함을 알려드립니다.
지원시 문제가 있을 경우 careers@lgresearch.ai 로 문의 부탁드립니다.

'''

chain = LLMChain(llm=llm, prompt=prompt)

job_description = chain.run(jd)


# 이력서 질문 생성
# user 이력서 입력
text_splitter = CharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20
    )

loader = PyPDFLoader("oty.pdf") #이력서
pages = loader.load_and_split(text_splitter)


vector_index = Chroma.from_documents(
    pages, # Documents
    OpenAIEmbeddings(),) # Text embedding model

#user_resume_lst = [n.page_content for n in pages]
#user_resume = " \n ".join(user_resume_lst)
llm = ChatOpenAI(temperature=0)


# 텍스트 파일 읽기
with open(MAKE_QUESTION_PROMPT_PATH, 'r', encoding='utf-8') as file:
    MAKE_QUESTION_PROMPT = file.read()

# Pass question to the qa_chain
prompt_template = MAKE_QUESTION_PROMPT



PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chain_type_kwargs = {"prompt": PROMPT}
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vector_index.as_retriever(),
    chain_type_kwargs=chain_type_kwargs, verbose = True)

print(qa_chain.run(job_description))

