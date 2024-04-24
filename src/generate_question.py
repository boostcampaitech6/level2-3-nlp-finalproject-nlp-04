import os
import random
import re

import openai
from langchain.chains.llm import LLMChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain.prompts.prompt import PromptTemplate
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_chroma.vectorstores import Chroma

import streamlit as st




def load_user_resume(USER_RESUME_SAVE_DIR):
    """
    사용자 이력서를 로드하는 함수입니다.

    :param USER_RESUME_SAVE_DIR: 사용자 이력서가 저장된 디렉토리 경로
    :type USER_RESUME_SAVE_DIR: str

    :return: 사용자 이력서의 내용을 하나의 문자열로 합친 결과
    :rtype: str
    """
    loader = PyPDFLoader(USER_RESUME_SAVE_DIR)
    pages = loader.load()

    ### User Total 이력서 Import
    user_resume_lst = [n.page_content for n in pages]
    user_resume = " \n ".join(user_resume_lst)
    return user_resume


def save_user_resume(USER_RESUME_SAVE_DIR, uploaded_file):
    """
    사용자가 입력한 이력서를 저장하는 함수입니다
    """
    with open(USER_RESUME_SAVE_DIR, "wb") as f:
        f.write(uploaded_file.getbuffer())


def load_user_JD(USER_JD_SAVE_DIR):
    """
    사용자가 입력한 채용공고JD 를 로드하는 함수입니다.

    :param USER_JD_SAVE_DIR: 사용자 이력서가 저장된 디렉토리 경로
    :type USER_JD_SAVE_DIR: str

    :return: 사용자 이력서의 내용을 하나의 문자열로 합친 결과
    :rtype: str
    """

    # 사용자 이력서 파일을 열어 내용을 읽고 저장
    with open(USER_JD_SAVE_DIR, "r", encoding="utf-8") as file:
        user_JD = file.read()

    return user_JD


# def save_user_JD(USER_JD_SAVE_DIR,uploaded_file):
#     with open(USER_JD_SAVE_DIR, 'wb') as f:
#         f.write(uploaded_file.getbuffer())


def save_user_JD(USER_JD_SAVE_DIR, uploaded_file_path):
    """
    사용자가 입력한 채용공고(JD)를 저장하는 함수입니다
    """
    # 파일 경로에서 파일을 읽어와 다른 위치에 저장합니다.
    with open(uploaded_file_path, "rb") as read_file:  # 원본 파일을 바이너리 읽기 모드로 엽니다.
        content = read_file.read()  # 파일 내용을 읽습니다.

    with open(USER_JD_SAVE_DIR, "wb") as write_file:  # 새로운 위치에 파일을 바이너리 쓰기 모드로 엽니다.
        write_file.write(content)  # 읽은 내용을 새 파일에 씁니다.


def create_prompt_with_jd(template):
    """
    주어진 JD(채용공고) 내용을 템플릿에 포함시켜 최종 프롬프트를 생성합니다.

    :param jd: 채용공고 내용
    :type jd: str
    :param template: 채용공고 내용을 포함시킬 템플릿
    :type template: str

    :return: 완성된 프롬프트
    :rtype: str
    """

    prompt = PromptTemplate(template=template, input_variables=["jd"])

    # JD 내용을 템플릿의 {jd} 부분에 삽입합니다.
    prompt_jd = prompt
    return prompt_jd


def create_prompt_with_resume(prompt_template):
    """
    앞서 JD(채용공고 를 이용해 LLMChain 한 job_description 과, resume txt를 템플릿에 포함시켜 최종 프롬프트를 생성합니다.

    :param jd: 채용공고 내용
    :type jd: str
    :param template: 채용공고 내용을 포함시킬 템플릿
    :type template: str

    :return: 완성된 프롬프트
    :rtype: str
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    # JD 내용을 템플릿의 {jd} 부분에 삽입합니다.
    prompt_qa = prompt
    return prompt_qa


def create_prompt_feedback(prompt_template):
    """
    feedback 프롬프트를 위해 해당 질문과 답변을 입력받아, 최종 프롬프트를 생성합니다.


    :param template: 채용공고 내용을 포함시킬 템플릿
    :type template: str
    :param question : 질문 내용
    :type question: str
    :param answer : 답변 내용
    :type answer: str


    :return: 완성된 프롬프트
    :rtype: str
    """
    # input_variables에 'question'과 'answer'를 명시적으로 설정

    # prompt_template = prompt_template.format(question=questions,answer=answers)
    prompt_feedback = PromptTemplate(template=prompt_template, input_variables=["question", "answer"])

    # 생성된 프롬프트를 반환
    # prompt_feedback = prompt.format(question=questions, answer=answers)
    return prompt_feedback


def create_prompt_hint(prompt_template):
    """
    feedback 프롬프트를 위해 해당 질문과 답변을 입력받아, 최종 프롬프트를 생성합니다.


    :param template: 채용공고 내용을 포함시킬 템플릿
    :type template: str
    :param question : 질문 내용
    :type question: str
    :param answer : 답변 내용
    :type answer: str


    :return: 완성된 프롬프트
    :rtype: str
    """
    # input_variables에 'question'과 'answer'를 명시적으로 설정

    # prompt_template = prompt_template.format(question=questions,answer=answers)
    prompt_hint = PromptTemplate(template=prompt_template, input_variables=["question"])

    # 생성된 프롬프트를 반환
    # prompt_feedback = prompt.format(question=questions, answer=answers)
    return prompt_hint




def create_resume_vectordb(USER_RESUME_SAVE_DIR):
    """
    이력서를 text_splitter로 chunking하고 chromadb에 embedding으로 저장합니다.

    """
    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    loader = PyPDFLoader(USER_RESUME_SAVE_DIR)
    pages = loader.load_and_split(text_splitter)

    vector_index = Chroma.from_documents(
        pages,  # Documents
        OpenAIEmbeddings(),
        persist_directory=os.path.dirname(USER_RESUME_SAVE_DIR)
    )  # Text embedding model
    return vector_index


def create_prompt_with_question(prompt_template):
    """
    3_chain에서 마지막 단계에서 사용되는 함수, chain1,2에서 요약된 jd와 resume을 이용해
    기술 면접 질문을 생성해줍니다.
    :param jd: 채용공고 내용
    :type jd: str
    :param template: 채용공고 내용을 포함시킬 템플릿
    :type template: str

    :return: 완성된 프롬프트
    :rtype: str
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["jd", "resume"])
    # JD 내용을 템플릿의 {jd} 부분에 삽입합니다.
    prompt_question = prompt
    return prompt_question
