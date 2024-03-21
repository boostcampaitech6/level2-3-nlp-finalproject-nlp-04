from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain
from langchain.callbacks import get_openai_callback
from langchain.prompts import (PromptTemplate,
                               ChatPromptTemplate,
                               SystemMessagePromptTemplate,
                               HumanMessagePromptTemplate)
import json
import re
import random
import openai
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings



def generate_llm_sub_chain(llm, template, output_key: str):
    """
    주어진 LLM(Language Model)과 템플릿을 사용하여 LLM 체인을 생성합니다.

    :param llm: LLM 모델 객체
    :type llm: LLM (Language Model) 객체

    :param template: 프롬프트 템플릿 (템플릿 문자열 또는 PromptTemplate 객체)
    :type template: str 또는 PromptTemplate

    :param output_key: 생성된 체인의 출력을 저장할 출력 키
    :type output_key: str

    :return: 생성된 LLM 체인 객체
    :rtype: LLMChain 객체
    """
    if type(template)==str:
        # 프롬프트 템플릿 정의
        prompt_template = PromptTemplate.from_template(template)
    else:
        prompt_template = template
    # 프롬프트와 출력 키를 사용하여 LLM 체인 생성
    sub_chain = LLMChain(llm=llm, prompt=prompt_template, output_key=output_key)
    return sub_chain

def preprocess_questions(result):
    """
    사용안함
    질문 데이터를 전처리하는 함수입니다.
    
    원본 하이어뷰는 한번에 주요질문, 추가질문 을 생성하고, 이를 BIG_QUESTION_SAVE_DIR 파일에 저장한다음, 전처리합니다
    하지만 우리는 그냥 question1, 2, 3 에 임시로 저장한 다음, 앞의 번호만 없이 

    :param result: 질문 데이터가 포함된 결과 객체
    :type result: dict

    :return: 전처리된 주요 질문과 추가 질문을 담은 두 개의 딕셔너리
    :rtype: tuple (main_question: dict, add_question: dict)
    """
    total_question = eval(result['generated_big_question_lst'])
    core_competencies = eval(result['core_competencies'])

    ### 질문 앞단에 숫자가 등장하는 경우 전처리 진행
    for key in total_question:
        total_question[key] = re.sub(r'\d+\.', '', total_question[key])

    ### 질문 전처리
    ### Create main_question dictionary with core_competencies as keys
    main_question = {key: value.split(';') for key, value in total_question.items() if key in core_competencies}
    ### Create add_question dictionary with remaining keys from total_question
    add_question = {key: value.split(';') for key, value in total_question.items() if key not in core_competencies}
    ### Randomly select one question for each competency in main_question
    main_question = {key: random.choice(value) for key, value in main_question.items()}
    
    return main_question,add_question,core_competencies




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
    print(len(pages), print(pages[0].page_content[0:500]), pages[0].metadata)

    ### User Total 이력서 Import
    user_resume_lst = [n.page_content for n in pages]
    user_resume = " \n ".join(user_resume_lst)
    return user_resume

def save_user_resume(USER_RESUME_SAVE_DIR,uploaded_file):
    with open(USER_RESUME_SAVE_DIR, 'wb') as f:
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
    with open(USER_JD_SAVE_DIR, 'r', encoding='utf-8') as file:
        user_JD = file.read()

    return user_JD

# def save_user_JD(USER_JD_SAVE_DIR,uploaded_file):
#     with open(USER_JD_SAVE_DIR, 'wb') as f:
#         f.write(uploaded_file.getbuffer())  

def save_user_JD(USER_JD_SAVE_DIR, uploaded_file_path):
    # 파일 경로에서 파일을 읽어와 다른 위치에 저장합니다.
    with open(uploaded_file_path, 'rb') as read_file:  # 원본 파일을 바이너리 읽기 모드로 엽니다.
        content = read_file.read()  # 파일 내용을 읽습니다.

    with open(USER_JD_SAVE_DIR, 'wb') as write_file:  # 새로운 위치에 파일을 바이너리 쓰기 모드로 엽니다.
        write_file.write(content)  # 읽은 내용을 새 파일에 씁니다.


def create_prompt_with_jd( template):
    """
    주어진 JD(채용공고) 내용을 템플릿에 포함시켜 최종 프롬프트를 생성합니다.

    :param jd: 채용공고 내용
    :type jd: str
    :param template: 채용공고 내용을 포함시킬 템플릿
    :type template: str

    :return: 완성된 프롬프트
    :rtype: str
    """
    
    prompt = PromptTemplate(
        template=template, input_variables=["jd"])

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
    
    prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"] )
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
    
    #prompt_template = prompt_template.format(question=questions,answer=answers)
    prompt_feedback = PromptTemplate(template=prompt_template, input_variables=["question", "answer"] )
    
    # 생성된 프롬프트를 반환
    #prompt_feedback = prompt.format(question=questions, answer=answers)
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
    
    #prompt_template = prompt_template.format(question=questions,answer=answers)
    prompt_hint = PromptTemplate(template=prompt_template, input_variables=["question"] )
    
    # 생성된 프롬프트를 반환
    #prompt_feedback = prompt.format(question=questions, answer=answers)
    return prompt_hint
    


def calculate_token_usage(response, prompt):
    """
    토큰 사용량을 계산하는 함수. 사용안합니다만 나중을 위해 남겨둠

    :param response: GPT API로부터 받은 응답 객체
    :param prompt: GPT 모델에 전달된 프롬프트 텍스트
    :return: 사용된 전체 토큰 수, 프롬프트 토큰 수, 완성 토큰 수
    """
    total_tokens_used = response
    prompt_tokens_used = len(openai.Completion.tokenize(prompt))
    completion_tokens_used = total_tokens_used - prompt_tokens_used

    return total_tokens_used, prompt_tokens_used, completion_tokens_used


def create_resume_vectordb(USER_RESUME_SAVE_DIR):
    '''
    이력서를 text_splitter로 chunking하고 chromadb에 embedding으로 저장합니다.
    
    '''
    text_splitter = CharacterTextSplitter(chunk_size=200,chunk_overlap=20)
    loader = PyPDFLoader(USER_RESUME_SAVE_DIR)
    pages = loader.load_and_split(text_splitter)
            
    vector_index = Chroma.from_documents(pages, # Documents
                OpenAIEmbeddings(),) # Text embedding model
    return vector_index

