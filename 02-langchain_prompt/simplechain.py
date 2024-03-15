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

with open("config.yaml", "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

#openai key 설정
os.environ['OPENAI_API_KEY'] = config['OPENAI_API_KEY']
api_key = os.environ.get('OPENAI_API_KEY')

def read_prompt_from_txt(path):
    with open(path,"r", encoding='utf-8') as f:
        data = f.read()
    return data

resume_pdf = config['RESUME']
jd_prompt_template = read_prompt_from_txt(config['JD_PROMPT'])
jd = read_prompt_from_txt(config['JD'])
resume_prompt_template = read_prompt_from_txt(config['RESUME_PROMPT'])

# 채용공고에서 핵심 기술 추출 - 직무명, 주요업무, 필요역량 및 우대조건
def from_jd(jd_prompt_template, jd):
    llm = ChatOpenAI(temperature=0)
    prompt = PromptTemplate(
    template=jd_prompt_template, input_variables=["jd"])
    chain = LLMChain(llm=llm, prompt=prompt)
    job_description = chain.run(jd)
    return job_description


# 이력서 질문 생성
def rag_resume(resume_pdf, resume_prompt_template, job_description):
    # user 이력서 입력
    text_splitter = CharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
        )
    loader = PyPDFLoader(resume_pdf)
    pages = loader.load_and_split(text_splitter)
    vector_index = Chroma.from_documents(
    pages, # Documents
    OpenAIEmbeddings(),) # Text embedding model
    llm = ChatOpenAI(temperature=0, model_name = 'gpt-3.5-turbo-16k')

    PROMPT = PromptTemplate(
    template=resume_prompt_template, input_variables=["context", "question"]
)
    chain_type_kwargs = {"prompt": PROMPT}
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_index.as_retriever(),
        chain_type_kwargs=chain_type_kwargs, verbose = True)
    result = qa_chain.run(job_description)
    return result

job_description = from_jd(jd_prompt_template, jd)
print(job_description)
print(rag_resume(resume_pdf, resume_prompt_template, job_description ))


